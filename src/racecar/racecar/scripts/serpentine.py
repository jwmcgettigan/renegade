#!/usr/bin/python
# ----------------
#

from mode import Mode
from cone import Cone
import cv2, numpy as np, math

DEBUG=True

class Serpentine(Mode):

    def __init__(self, zed, lidar, vesc, DISPLAY):
        super(Serpentine, self).__init__(vesc)
        self.DISPLAY = DISPLAY
        # self.process(zed.getImage(), lidar.getData()) # do I need to copy the image?
        self.data = lidar.getData()
        self.process(zed.getImage())
        vesc.setDriveMsg(self.driveMsg)
        vesc.publish()


    def process(self, image):
        #left = self.camera(image[0:256, 0:672], self.lidarRange(data.ranges[21:550]), 'left')
        #right = self.camera(image[0:256, 672:1344], self.lidarRange(data.ranges[551:1080]), 'right')
        left = self.side(image[0:256, 0:672], (540, 1055), 'left')
        right = self.side(image[0:256, 672:1344], (25, 540), 'right')

        return self.control(left, right)


    def side(self, image, ranges, label):
        cone = self.detectCone(image, ranges)
        if self.DISPLAY:
            cv2.imshow(label + ' Camera', cone.draw())
            cv2.waitKey(1)
        return cone


    def detectCone(self, image, ranges):
        """Detects the closest cone"""
        distance, angle = self.rangeAnalysis(ranges)
        return Cone(self.imageAnalysis(image), image, distance, angle)


    def control(self, left, right):
        lCenter, rCenter = left.getCenter(), right.getCenter()
        coneSeen = (False if lCenter == [0, 0] and rCenter == [0, 0] else True)
        aCenter = (lCenter[0] + rCenter[0]) / 2, (lCenter[1] + rCenter[1]) / 2

        lDistance, rDistance = left.getDistance(), right.getDistance()
        lAngle, rAngle = left.getAngle(), right.getAngle()

        desired = 0.35

        direction = ""
        height, width = left.getImage().shape[:2]
        if aCenter[0] < width/2: # LEFT
            direction, distance, angle = "Left", lDistance, lAngle
            error = -(desired - self.perpendicularLineDistance(angle, distance))
        else:                    # RIGHT
            direction, distance, angle = "Right", rDistance, rAngle
            error = desired - self.perpendicularLineDistance(angle, distance)

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
        speed = 0.2
        if DEBUG and coneSeen:
            print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
            #print "Acenterx:\t "        +    str(aCenter[0])
            #print "Width:\t\t "           +    str(width/2)
            print "Direction:\t "       +    direction
            print "Distance:\t %.4f"       % distance
            print "Angle:\t\t %.4f"        % angle
            print "Cone Seen:\t %s"        % coneSeen

            print "\nError:\t\t %.4f"      % error
            print "Steering Angle:\t %.4f" % steeringAngle
            print "Speed:\t\t %.4f"        % speed
            """
            print "    Left  Right"
            print "Center:\t %s"      % ((lCenter,),(rCenter,))
            print "Distance:\t %.4f, %.4f"  % (lDistance, rDistance)
            print "Angle:\t %.4f, %.4f"     % (lAngle, rAngle)
            """
            print "\nLeft Center:\t %s"      % (lCenter,)
            print "Left Distance:\t %.4f"  % lDistance
            print "Left Angle:\t %.4f"     % lAngle
            print "\nRight Center:\t %s"   % (rCenter,)
            print "Right Distance:\t %.4f" % rDistance
            print "Right Angle:\t %.4f"    % rAngle
            print "\nAverage Center:\t %s" % (aCenter,)

        return self.decide(speed, steeringAngle, coneSeen)


    def decide(self, speed, steeringAngle, coneSeen):
        if coneSeen:
            self.apply_control(speed, steeringAngle)
        else:
            self.apply_control(1, 0)


    def imageAnalysis(self, image):
        color = self.color
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
