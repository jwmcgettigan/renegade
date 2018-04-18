#!/usr/bin/python
# ----------------
#

from mode import Mode
from cone import Cone
from cube import Cube
import cv2, numpy as np, math

DEBUG=False
VERBOSE=True
VISUAL=False

class ObjectFollower(Mode):

    def __init__(self, zed, lidar, vesc, DISPLAY):
        super(ObjectFollower, self).__init__(vesc)
        # self.lastDirection = serpentineValues[0]
        # self.lastOrbit = serpentineValues[1]
        # self.count = serpentineValues[2]
        # self.numberOfCones = serpentineValues[3]
        self.vesc = vesc
        self.DISPLAY = DISPLAY
        # self.process(zed.getImage(), lidar.getData()) # do I need to copy the image?
        self.data = lidar.getData()
        # self.process(zed.getImage())

        
        self.setCurrentObject()
        print(self.getCurrentObject())
        self.edgeDetection(5)
        print 1
        self.control()
        print 2
        self.decide(0, 0.2)
        print 3
        vesc.setDriveMsg(self.driveMsg)
        print 4
        vesc.publish()
        print 5

    """
    def run(self, zed, lidar, DISPLAY):
        self.DISPLAY = DISPLAY
        self.data = lidar.getData()
        self.process(zed.getImage())
        self.vesc.setDriveMsg(self.driveMsg)
        self.vesc.publish()
    """

    # def getLastDirection(self):
    #     return self.lastDirection


    # def getLastOrbit(self):
    #     return self.lastOrbit


    # def getCount(self):
    #     return self.count


    # def getNumberOfCones(self):
    #     return self.numberOfCones

    def getCurrentObject(self):
        return self.currentObject

    def setCurrentObject(self):
        self.currentObject = (1,2)

    def edgeDetection(self, tempMaxDistance):
        lowestAngle = -100
        highestAngle = 100
        tempRanges = self.reduceMaxDistance(tempMaxDistance)
        ObjectCenterAngle = self.unconvertAngle(tempRanges.index(min(tempRanges)))
        objectCenterDistance = min(tempRanges)
        objectRightEdgeIndex = 0
        objectLeftEdgeIndex = 0
        print(objectCenterDistance, ObjectCenterAngle)
        for x in range(self.convertAngle(ObjectCenterAngle), self.convertAngle(ObjectCenterAngle)+20):
            if ObjectLeftEdgeIndex is 0:
                if tempRanges[x]*1.1 < tempRanges[x+1]: #If current position is 10% closest or more than the next position, that is an edge.
                    objectLeftEdgeIndex = x
        if ObjectLeftEdgeIndex is 0:
            for x in range(self.convertAngle(ObjectCenterAngle), self.convertAngle(ObjectCenterAngle)-20, -1):
                if tempRanges[x]*1.1 < tempRanges[x-1]: #If current position is 10% closest or more than the next position, that is an edge.
                    objectRightEdgeIndex = x
        print(objectLeftEdgeIndex,objectRightEdgeIndex)


        #start with the closest distance, then work outward until a distance changes by more than 1.1x from the previous. If yes, that that is an edge.





    def convertAngle(self, desiredAngle): #Input = angle normal people use. Counter clockwise from -135 to 135
        desiredAngle += 135
        return int(1081-(desiredAngle*(1081/270))) #1081 is max angle (back left). (Angle+135)*len(LidarRanges)/len(RearAngles)

    def unconvertAngle(self, arrayIndex): #Input = angle normal people use. Counter clockwise from -135 to 135
        return -(arrayIndex-1081)*(float(270)/1081)-135

    def reduceMaxDistance(self, newMaxDistance): #To make this a permanent change, assign the result to data.ranges
        reducedArray = []
        for x in range(0,len(self.data.ranges)):
            if self.data.ranges[x] > newMaxDistance: 
                reducedArray.append(newMaxDistance)
            else:
                reducedArray.append(self.data.ranges[x])
        return reducedArray


    def control(self):
        steeringAngle = 1
        return self.decide(speed, steeringAngle)

    # def edgeDetection(self, frontAngle, rearAngle, tempMaxDistance):
    #     convertedFrontAngle = self.convertAngle(frontAngle)
    #     convertedRearAngle = self.convertAngle(rearAngle)
    #     tempRanges = self.reduceMaxDistance(tempMaxDistance)
    #     print "\n\n\n\n\n\nfrontAngle:\t" + str(frontAngle)
    #     print "rearAngle:\t" + str(rearAngle)
    #     print "frontAngleCon:\t" + str(convertedFrontAngle)
    #     print "rearAngleCon:\t" + str(convertedRearAngle)
    #     frontEdge = 0
    #     rearEdge = 0
    #     print "index\tangle\tdistance\tdistance-2"
    #     for x in range(convertedFrontAngle, convertedRearAngle, -1): #starts looking from the front and continue looking backwards
    #         print str(x) + "\t" + str(self.unconvertAngle(x)) + "\t" + str(tempRanges[x]) + "\t" + str(tempRanges[x-2])
    #         if ((tempRanges[x] * 0.8) > tempRanges[x-2]): #If the distance 2 array positions towards the rear is less than the current position * 0.8. We have the front edge
    #             frontEdge = x-2
    #             print "Front Edge Found"
    #         if ((tempRanges[x]) < tempRanges[x-2] * 0.8): #Same concept for rear edge, but now the more forward position must be the object, so it should be the object.
    #             rearEdge = x
    #             print "Rear Edge Found"
    #     print ("objFrontAng:\t" + str(frontEdge))
    #     print ("objRearAng:\t" + str(rearEdge))


    # def process(self, image):
    #     height, width = image.shape[:2]
    #     left = self.side(image[:height, :width/2], (540, 1055), 'left')
    #     right = self.side(image[:height, width/2:width], (25, 540), 'right')
    #     return self.control(left, right)



    # def side(self, image, ranges, label):
    #     height, width = image.shape[:2]
    #     cone = self.detectCone(image, ranges)
    #     cube = self.detectCube(image, ranges)
    #     if cone.getCenter()[1] < cube.getCenter()[1]:
    #         if self.DISPLAY:
    #             cv2.imshow(label + ' Camera', cube.draw())
    #             #cv2.imshow(label + ' Camera', np.hstack([cone.draw(), cube.draw()]))
    #             cv2.waitKey(1)
    #         return cube
    #     else:
    #         if self.DISPLAY:
    #             cv2.imshow(label + ' Camera', cone.draw())
    #             #cv2.imshow(label + ' Camera', np.hstack([cone.draw(), cube.draw()]))
    #             cv2.waitKey(1)
    #         return cone


    # def detectCone(self, image, ranges):
    #     """Detects the closest cone"""
    #     distance, angle = self.rangeAnalysis(ranges)
    #     yellow = self.color[2]
    #     return Cone(self.imageAnalysis(image, yellow), image, distance, angle)


    # def detectCube(self, image, ranges):
    #     """Detects the closest cube"""
    #     distance, angle = self.rangeAnalysis(ranges)
    #     orange = self.color[3]
    #     return Cube(self.imageAnalysis(image, orange), image, distance, angle)


    # def control(self, left, right):
    #     perpendicularDistance = adjacentDistance = distance = angle = error = 0
    #     angleOffset = distanceOffset = perpendicularOffset = 0
    #     height, width = left.getImage().shape[:2]
    #     lCenter, rCenter = left.getCenter(), right.getCenter()
    #     center = (lCenter[0] + rCenter[0]) / 2, (lCenter[1] + rCenter[1]) / 2
    #     if lCenter[0] == 0: center = rCenter
    #     if rCenter[0] == 0: center = lCenter
    #     #coneSeen = (False if lCenter == [0, 0] and rCenter == [0, 0] else True)
    #     coneSeen = center[0] > 0

    #     lDistance, rDistance = left.getDistance(), right.getDistance()
    #     lAngle, rAngle = left.getAngle(), right.getAngle()

    #     """ THIS WORKS GREAT
    #     distanceConstant, angleConstant, perpendicularConstant = 1, 0.3/131, 1.0/2
    #     desiredDistance, desiredAngle, desiredPerpendicular = 0.3, 0, 0.3
    #     triggerAngle, direction = 80, ""
    #     """
    #     distanceConstant, angleConstant, perpendicularConstant, adjacentConstant = 1, 0.3/131, 1.0/2, 1.0/2
    #     desiredDistance, desiredAngle, desiredPerpendicular = 0.3, 0, 0.3
    #     triggerAngle, direction = 80, ""

    #     print "Count: " + str(self.count)
    #     print "NumCones: " + str(self.numberOfCones)
    #     print "IsCube: " + str(left.getIsCube() and right.getIsCube())
    #     if left.getIsCube() and right.getIsCube() or self.count == self.numberOfCones:
    #         if VERBOSE: print "TREATING IT LIKE A CUBE"
    #         desiredDistance, desiredAngle, desiredPerpendicular = 0.3, 0, 1.0
    #         self.numberOfCones = self.count
    #         self.count = 0

    #     perpendicular, orbit = True, False
    #     useLeft, useRight = False, False

    #     if self.lastDirection == "Left":
    #         if VERBOSE: print "THE CONE WAS ON THE LEFT"
    #         if self.lastOrbit:
    #             if VERBOSE: print "YOU ARE ORBITING TO THE LEFT"
    #             useLeft, useRight = True, False
    #             perpendicular, orbit = False, True
    #             if center[0] >= width*(2/3.0):
    #                 useLeft, useRight = False, True
    #                 if VERBOSE: print "YOU ARE NOW PERPENDICULAR TO THE RIGHT"
    #                 perpendicular, orbit = True, False
    #         elif not coneSeen: # or middle:
    #             useLeft, useRight = True, False
    #         elif coneSeen and center[0] <= width/2:
    #             useLeft, useRight = True, False
    #         elif center[0] > width/2:
    #             useLeft, useRight = False, True
    #         else:
    #             print "THERE IS SOMETHING SERIOUSLY WRONG!1"
    #     elif self.lastDirection == "Right":
    #         if VERBOSE: print "THE CONE WAS ON THE RIGHT"
    #         if self.lastOrbit:
    #             if VERBOSE: print "YOU ARE ORBITING TO THE RIGHT"
    #             useLeft, useRight = False, True
    #             perpendicular, orbit = False, True
    #             if coneSeen and center[0] <= width/3.0:
    #                 useLeft, useRight = True, False
    #                 if VERBOSE: print "YOU ARE NOW PERPENDICULAR TO THE LEFT"
    #                 perpendicular, orbit = True, False
    #         elif not coneSeen: # or middle:
    #             useLeft, useRight = False, True
    #         elif coneSeen and center[0] <= width/2:
    #             useLeft, useRight = True, False
    #         elif center[0] > width/2:
    #             useLeft, useRight = False, True
    #         else:
    #             print "THERE IS SOMETHING SERIOUSLY WRONG!2"
    #     elif coneSeen and center[0] <= width/2:
    #         if VERBOSE: print "THE CONE IS ON THE LEFT"
    #         useLeft, useRight = True, False
    #     elif center[0] > width/2:
    #         if VERBOSE: print "THE CONE IS ON THE RIGHT"
    #         useLeft, useRight = False, True
    #     else:
    #         print "No cone has been seen."


    #     if useLeft: # LEFT
    #         if VERBOSE: print "YOU ARE USING THE LEFT SIDE"
    #         distance, angle = lDistance, lAngle
    #         adjacentDistance = self.adjacentLineDistance(angle, distance)
    #         perpendicularDistance = self.perpendicularLineDistance(angle, distance)
    #         perpendicularOffset = perpendicularConstant*(perpendicularDistance - desiredPerpendicular)
    #         distanceOffset = distanceConstant*(distance - desiredDistance)
    #         angleOffset = -angleConstant*(angle + desiredAngle)

    #         if abs(angle) > triggerAngle:
    #             if VERBOSE: print "YOU ARE NOW ORBITING TO THE LEFT"
    #             if VERBOSE: print "distance, angle: %.2f, %.2f" % (distance, angle)
    #             perpendicular, orbit = False, True

    #         if perpendicular:
    #             if VERBOSE: print "YOU ARE PERPENDICULAR TO THE LEFT"
    #             if VERBOSE: print "distance, angle: %.2f, %.2f" % (distance, angle)
    #             error = perpendicularOffset
    #         elif orbit: error = 0.3#(1 * angleOffset) + (0 * distanceOffset)
    #         #if distance < 0.3:
    #             #error -= distance
    #         direction = "Left"
    #     elif useRight: # RIGHT
    #         if VERBOSE: print "YOU ARE USING THE RIGHT SIDE"
    #         distance, angle = rDistance, rAngle
    #         adjacentDistance = self.adjacentLineDistance(angle, distance)
    #         perpendicularDistance = self.perpendicularLineDistance(angle, distance)
    #         perpendicularOffset = perpendicularConstant*(desiredPerpendicular - perpendicularDistance)
    #         distanceOffset = distanceConstant*(desiredDistance - distance)
    #         angleOffset = angleConstant*(desiredAngle - angle)

    #         if abs(angle) > triggerAngle:
    #             if VERBOSE: print "YOU ARE NOW ORBITING TO THE RIGHT"
    #             if VERBOSE: print "distance, angle: %.2f, %.2f" % (distance, angle)
    #             perpendicular, orbit = False, True

    #         if perpendicular:
    #             if VERBOSE: print "YOU ARE PERPENDICULAR TO THE RIGHT"
    #             if VERBOSE: print "distance, angle: %.2f, %.2f" % (distance, angle)
    #             error = perpendicularOffset
    #         elif orbit: error = -0.3#(1 * angleOffset) + (0 * distanceOffset)
    #         #if distance < 0.3:
    #             #error += distance
    #         direction = "Right"
    #     if self.lastDirection is not direction:
    #         self.count += 1
    #         #print self.count
    #     self.lastDirection = direction
    #     self.lastOrbit = orbit

    #     """
    #     Need errors for coneOrbit for left and right side.
    #     Need mechanism to make sure the last cone seen is considered the side.

    #     """

    #     #if lCenter == [0, 0] and rCenter == [0, 0]: coneSeen = False
    #     #else: coneSeen = True

    #     #error = self.perpendicularLineDistance(angle, distance)
    #     #error = distance - desiredDistance
    #     #error = 0.35 - distance
    #     #steeringAngle = (0.3/0.1)*error
    #     steeringAngle = error
    #     if steeringAngle > 0.3: steeringAngle = 0.3
    #     if steeringAngle < -0.3: steeringAngle = -0.3
    #     print "Steering Angle: " + str(steeringAngle)
    #     """
    #     if steeringAngle > 0.02: direction = "Left"
    #     elif steeringAngle < -0.02: direction = "Right"
    #     else: direction = "Center"
    #     """
    #     #speedLimit = 0.6
    #     #speedPower = 1.13678
    #     #speed = speedLimit * (1 - abs(steeringAngle))**speedPower
    #     speed = 1*1.5
    #     #speed = adjacentDistance * error
    #     if error >= 0.2:
    #         speed = 0.5*1.5
    #     if DEBUG:
    #         print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"

    #         print "\t%10s\t\t||%-20s" % ("Left Side", "Right Side")
    #         print "%9s %4s %4s %2s %5s %1s %9s %5s %4s %2s %5s" % ("Center","|","Angle","|","Distance","||","Center","|","Angle","|","Distance")
    #         print "%9s %4s %4.2f %2s %5.4f %1s %9s %5s %4.2f %2s %5.4f"      % ((lCenter,),"|", lAngle,"|", lDistance,"||", (rCenter,),"|", rAngle,"|", rDistance)
    #         print "\n\tOrbit:%s\t    ||   Perpendicular:%s" % (orbit, perpendicular)
    #         print "Angle Offset | Orbit Offset || Perpendicular Offset"
    #         print "%.4f\t     |   %.4f     || %.4f" % (angleOffset, distanceOffset, perpendicularOffset)
    #         print "\nError  | Steering Angle | Speed"
    #         print "%.4f |    %.4f      | %.2f" % (error, steeringAngle, speed)
    #         print "\n Center  | Width | Cone Seen | Last Orbit"
    #         print "%s |  %d  | %s | %s" % ((center,), width, coneSeen, self.lastOrbit)
    #         print "\nDistance | Angle | Direction | Last Direction " #add real direction in
    #         print "%.2f     | %.2f  |   %s   | %s" % (distance, angle, direction, self.lastDirection)

    #     if VISUAL:
    #         print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
    #         print "Perpendicular: " + str(perpendicular)
    #         print "Orbit: " + str(orbit)

    #         """
    #         if direction == "Left":
    #             print " _____ "
    #             print "|\\"
    #             print "| \\"
    #             print "   \\"
    #         if direction == "Right":
    #             print "  ____ "
    #             print "     /|"
    #             print "    / |"
    #             print "   /   "
    #         """

    #     return self.decide(speed, steeringAngle)


    def decide(self, speed, steeringAngle):
        self.apply_control(speed, steeringAngle)


    # def imageAnalysis(self, image, color):
    #     maskedImage = self.colorMask(image, color[0])
    #     imgray = cv2.cvtColor(maskedImage, cv2.COLOR_BGR2GRAY)
    #     blurred = cv2.GaussianBlur(imgray, (5,5), 0)
    #     thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY)[1]
    #     contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
    #     if len(contours) > 0: # cv2.contourArea(c) >= 5000
    #         c = max(contours, key = cv2.contourArea)
    #         return c
    #         #return Cone(c, image)
    #         #for c in contours:
    #             #if largest and closest, create cone object
    #     else:
    #         pass


    # def rangeAnalysis(self, ranges):
    #     """Returns: distance from closest object, angle of closest object"""
    #     tempRanges = []
    #     for x in range(0, ranges[0]): tempRanges.append(65)
    #     for x in range(ranges[0], ranges[1]): tempRanges.append(self.data.ranges[x])
    #     for x in range(ranges[1], 1081): tempRanges.append(65)
    #     # return min(tempRanges), tempRanges.index(min(tempRanges))
    #     minimum = min(tempRanges)
    #     #print tempRanges
    #     #print "minimum: " + str(minimum) + "," + str(tempRanges.index(minimum)) + "," + str(self.toAngle(tempRanges.index(minimum)))
    #     #tempRanges.sort()
    #     #print "==========="
    #     #for x in range(0, 10): print self.toAngle(self.data.ranges.index(tempRanges[x]))
    #     #print tempRanges
    #     #print "==========="

    #     return minimum, self.toAngle(tempRanges.index(minimum))


    # def fromAngle(self, angle): #Input = angle normal people use. Counter clockwise from -135 to 135
    #     angle += 135
    #     return int(1081-(angle*(float(1081)/270))) #1081 is max angle (back left). (Angle+135)*len(LidarRanges)/len(RearAngles)


    # def toAngle(self, index):
    #     return -(index-1081)*(float(270)/1081) - 135




    # def perpendicularLineDistance(self, angle, hypotenuse):
    #     return abs(hypotenuse*math.sin(angle*0.0174533))

    # def adjacentLineDistance(self, angle, hypotenuse):
    #     return abs(hypotenuse*math.cos(angle*0.0174533))
