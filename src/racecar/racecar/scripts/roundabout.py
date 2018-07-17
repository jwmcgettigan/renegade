#!/usr/bin/python
# ----------------
#

from mode import Mode

class Roundabout(Mode):

    def __init__(self, zed, lidar, vesc, DISPLAY):
        super(Roundabout, self).__init__(vesc)
        self.vesc = vesc
        self.DISPLAY = DISPLAY
        self.data = lidar.getData()
        self.process(zed.getImage())
        vesc.setDriveMsg(self.driveMsg)
        vesc.publish()


    def process(self, image):
        left = self.side(image[0:256, 0:672], (540, 1055), 'left')
        right = self.side(image[0:256, 672:1344], (25, 540), 'right')
        return self.control(left, right)


    def side(self, image, ranges, label):
        cone = self.detectCone(image, ranges)
        #cube = self.detectCube(image, ranges)
        if self.DISPLAY:
            cv2.imshow(label + ' Camera', cone.draw())
            #cv2.imshow(label + ' Camera', np.hstack([cone.draw(), cube.draw()]))
            cv2.waitKey(1)
        return cone


    def detectCone(self, image, ranges):
        """Detects the closest cone"""
        distance, angle = self.rangeAnalysis(ranges)
        yellow = self.color[2]
        return Cone(self.imageAnalysis(image, yellow), image, distance, angle)


    def detectCube(self, image, ranges):
        """Detects the closest cube"""
        distance, angle = self.rangeAnalysis(ranges)
        orange = self.color[3]
        return Cube(self.imageAnalysis(image, orange), image, distance, angle)


    def control(self, left, right):
        perpendicularDistance = distance = angle = error = 0
        angleOffset = distanceOffset = perpendicularOffset = 0
        height, width = left.getImage().shape[:2]
        lCenter, rCenter = left.getCenter(), right.getCenter()
        center = (lCenter[0] + rCenter[0]) / 2, (lCenter[1] + rCenter[1]) / 2
        if lCenter[0] == 0: center = rCenter
        if rCenter[0] == 0: center = lCenter
        #coneSeen = (False if lCenter == [0, 0] and rCenter == [0, 0] else True)
        coneSeen = center[0] > 0

        lDistance, rDistance = left.getDistance(), right.getDistance()
        lAngle, rAngle = left.getAngle(), right.getAngle()

        """ THIS WORKS GREAT
        distanceConstant, angleConstant, perpendicularConstant = 1, 0.3/131, 1.0/2
        desiredDistance, desiredAngle, desiredPerpendicular = 0.3, 0, 0.3
        triggerAngle, direction = 80, ""
        """
        distanceConstant, angleConstant, perpendicularConstant = 1, 0.3/131, 1.0/2
        desiredDistance, desiredAngle, desiredPerpendicular = 0.3, 0, 1.0
        triggerAngle, direction = 70, ""

        perpendicular, orbit = True, False
        useLeft, useRight = False, False

        if self.lastDirection == "Left":
            if VERBOSE: print "THE CONE WAS ON THE LEFT"
            if self.lastOrbit:
                if VERBOSE: print "YOU ARE ORBITING TO THE LEFT"
                useLeft, useRight = True, False
                perpendicular, orbit = False, True
                if center[0] >= width*(2/3.0):
                    useLeft, useRight = False, True
                    if VERBOSE: print "YOU ARE NOW PERPENDICULAR TO THE RIGHT"
                    perpendicular, orbit = True, False
            elif not coneSeen: # or middle:
                useLeft, useRight = True, False
            elif coneSeen and center[0] <= width/2:
                useLeft, useRight = True, False
            elif center[0] > width/2:
                useLeft, useRight = False, True
            else:
                print "THERE IS SOMETHING SERIOUSLY WRONG!1"
        elif self.lastDirection == "Right":
            if VERBOSE: print "THE CONE WAS ON THE RIGHT"
            if self.lastOrbit:
                if VERBOSE: print "YOU ARE ORBITING TO THE RIGHT"
                useLeft, useRight = False, True
                perpendicular, orbit = False, True
                if coneSeen and center[0] <= width/3.0:
                    useLeft, useRight = True, False
                    if VERBOSE: print "YOU ARE NOW PERPENDICULAR TO THE LEFT"
                    perpendicular, orbit = True, False
            elif not coneSeen: # or middle:
                useLeft, useRight = False, True
            elif coneSeen and center[0] <= width/2:
                useLeft, useRight = True, False
            elif center[0] > width/2:
                useLeft, useRight = False, True
            else:
                print "THERE IS SOMETHING SERIOUSLY WRONG!2"
        elif coneSeen and center[0] <= width/2:
            if VERBOSE: print "THE CONE IS ON THE LEFT"
            useLeft, useRight = True, False
        elif center[0] > width/2:
            if VERBOSE: print "THE CONE IS ON THE RIGHT"
            useLeft, useRight = False, True
        else:
            print "No cone has been seen."


        if useLeft: # LEFT
            distance, angle = lDistance, lAngle
            perpendicularDistance = self.perpendicularLineDistance(angle, distance)
            perpendicularOffset = perpendicularConstant*(perpendicularDistance - desiredPerpendicular)
            distanceOffset = distanceConstant*(distance - desiredDistance)
            angleOffset = -angleConstant*(angle + desiredAngle)

            if abs(angle) > triggerAngle:
                if VERBOSE: print "YOU ARE NOW ORBITING TO THE LEFT"
                if VERBOSE: print "distance, angle: %.2f, %.2f" % (distance, angle)
                perpendicular, orbit = False, True

            if perpendicular:
                if VERBOSE: print "YOU ARE PERPENDICULAR TO THE LEFT"
                error = perpendicularOffset
            elif orbit: error = 0.3#(1 * angleOffset) + (0 * distanceOffset)
            direction = "Left"
        elif useRight:                 # RIGHT
            distance, angle = rDistance, rAngle
            perpendicularDistance = self.perpendicularLineDistance(angle, distance)
            perpendicularOffset = perpendicularConstant*(desiredPerpendicular - perpendicularDistance)
            distanceOffset = distanceConstant*(desiredDistance - distance)
            angleOffset = angleConstant*(desiredAngle - angle)

            if abs(angle) > triggerAngle:
                if VERBOSE: print "YOU ARE NOW ORBITING TO THE RIGHT"
                if VERBOSE: print "distance, angle: %.2f, %.2f" % (distance, angle)
                perpendicular, orbit = False, True

            if perpendicular:
                if VERBOSE: print "YOU ARE PERPENDICULAR TO THE RIGHT"
                error = perpendicularOffset
            elif orbit: error = -0.3#(1 * angleOffset) + (0 * distanceOffset)
            direction = "Right"
        self.lastDirection = direction
        self.lastOrbit = orbit

        """
        Need errors for coneOrbit for left and right side.
        Need mechanism to make sure the last cone seen is considered the side.

        """

        #if lCenter == [0, 0] and rCenter == [0, 0]: coneSeen = False
        #else: coneSeen = True

        #error = self.perpendicularLineDistance(angle, distance)
        #error = distance - desiredDistance
        #error = 0.35 - distance
        #steeringAngle = (0.3/0.1)*error
        steeringAngle = error
        if steeringAngle > 0.3: steeringAngle = 0.3
        if steeringAngle < -0.3: steeringAngle = -0.3
        """
        if steeringAngle > 0.02: direction = "Left"
        elif steeringAngle < -0.02: direction = "Right"
        else: direction = "Center"
        """
        #speedLimit = 0.6
        #speedPower = 1.13678
        #speed = speedLimit * (1 - abs(steeringAngle))**speedPower
        speed = 1
        if error >= 0.3:
            speed = 0.5
        if DEBUG:
            print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"

            print "\t%10s\t\t||%-20s" % ("Left Side", "Right Side")
            print "%9s %4s %4s %2s %5s %1s %9s %5s %4s %2s %5s" % ("Center","|","Angle","|","Distance","||","Center","|","Angle","|","Distance")
            print "%9s %4s %4.2f %2s %5.4f %1s %9s %5s %4.2f %2s %5.4f"      % ((lCenter,),"|", lAngle,"|", lDistance,"||", (rCenter,),"|", rAngle,"|", rDistance)
            print "\n\tOrbit:%s\t    ||   Perpendicular:%s" % (orbit, perpendicular)
            print "Angle Offset | Orbit Offset || Perpendicular Offset"
            print "%.4f\t     |   %.4f     || %.4f" % (angleOffset, distanceOffset, perpendicularOffset)
            print "\nError  | Steering Angle | Speed"
            print "%.4f |    %.4f      | %.2f" % (error, steeringAngle, speed)
            print "\n Center  | Width | Cone Seen | Last Orbit"
            print "%s |  %d  | %s | %s" % ((center,), width, coneSeen, self.lastOrbit)
            print "\nDistance | Angle | Direction | Last Direction " #add real direction in
            print "%.2f     | %.2f  |   %s   | %s" % (distance, angle, direction, self.lastDirection)

        return self.decide(speed, steeringAngle)


    def decide(self, speed, steeringAngle):
        self.apply_control(speed, steeringAngle)


    def imageAnalysis(self, image, color):
        maskedImage = self.colorMask(image, color[0])
        imgray = cv2.cvtColor(maskedImage, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(imgray, (5,5), 0)
        thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY)[1]
        contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
        if len(contours) > 0: # cv2.contourArea(c) >= 5000
            c = max(contours, key = cv2.contourArea)
            return c
            #return Cone(c, image)
            #for c in contours:
                #if largest and closest, create cone object
        else:
            pass


    def rangeAnalysis(self, ranges):
        """Returns: distance from closest object, angle of closest object"""
        tempRanges = []
        for x in range(0, ranges[0]): tempRanges.append(65)
        for x in range(ranges[0], ranges[1]): tempRanges.append(self.data.ranges[x])
        for x in range(ranges[1], 1081): tempRanges.append(65)
        # return min(tempRanges), tempRanges.index(min(tempRanges))
        minimum = min(tempRanges)
        return minimum, self.toAngle(tempRanges.index(minimum))


    def fromAngle(self, angle): #Input = angle normal people use. Counter clockwise from -135 to 135
        angle += 135
        return int(1081-(angle*(float(1081)/270))) #1081 is max angle (back left). (Angle+135)*len(LidarRanges)/len(RearAngles)


    def toAngle(self, index):
        return -(index-1081)*(float(270)/1081) - 135


    def perpendicularLineDistance(self, angle, hypotenuse):
        #hypotenuse = self.data.ranges[self.fromAngle(angle)]
        adjacentDistance = abs(hypotenuse*math.sin(angle*0.0174533))
        # print str(angle) + "\t" + str(self.data.ranges[self.convertAngle(angle)]) + "\t" + str(abs(self.data.ranges[self.convertAngle(angle)]*math.sin(angle)))
        #print str(angle) + "\t" + str(hypotenuse) + "\t" + str(adjacentDistance)
        return adjacentDistance
