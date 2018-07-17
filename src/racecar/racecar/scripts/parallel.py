#!/usr/bin/python
# ----------------
#

from mode import Mode
from cone import Cone
import cv2, numpy as np, math

DEBUG=False
VERBOSE=False

class Parallel(Mode):

    def __init__(self, zed, lidar, vesc, DISPLAY):
        super(Parallel, self).__init__(vesc)
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
        if self.DISPLAY:
            cv2.imshow(label + ' Camera', cone.draw())
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
        stop = False
        perpendicularDistance = distance = angle = error = 0
        angleOffset = distanceOffset = perpendicularOffset = 0
        height, width = left.getImage().shape[:2]
        lCenter, rCenter = left.getCenter(), right.getCenter()
        center = (lCenter[0] + rCenter[0]) / 2, (lCenter[1] + rCenter[1]) / 2
        if lCenter[0] == 0: center = rCenter
        if rCenter[0] == 0: center = lCenter
        coneSeen = center[0] > 0

        if not coneSeen:
            stop = True

        lDistance, rDistance = left.getDistance(), right.getDistance()
        lAngle, rAngle = left.getAngle(), right.getAngle()

        perpendicularConstant = 1/2.0
        desiredPerpendicular = 0.3
        triggerAngle, direction = 70, ""
        useLeft, useRight = False, False

        if coneSeen and center[0] <= width/2:
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
            error = perpendicularOffset
            direction = "Left"
        elif useRight: # RIGHT
            distance, angle = rDistance, rAngle
            perpendicularDistance = self.perpendicularLineDistance(angle, distance)
            perpendicularOffset = perpendicularConstant*(desiredPerpendicular - perpendicularDistance)
            error = perpendicularOffset
            direction = "Right"

        print error
        steeringAngle = error
        if steeringAngle > 0.3: steeringAngle = 0.3
        if steeringAngle < -0.3: steeringAngle = -0.3
        speed = 1
        return self.decide(speed, steeringAngle, stop)


    def decide(self, speed, steeringAngle, stop):
        if stop: self.apply_control(0, 0)
        else: self.apply_control(speed, steeringAngle)


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


    def toAngle(self, index):
        return -(index-1081)*(float(270)/1081) - 135


    def perpendicularLineDistance(self, angle, hypotenuse):
        #hypotenuse = self.data.ranges[self.fromAngle(angle)]
        adjacentDistance = abs(hypotenuse*math.sin(angle*0.0174533))
        # print str(angle) + "\t" + str(self.data.ranges[self.convertAngle(angle)]) + "\t" + str(abs(self.data.ranges[self.convertAngle(angle)]*math.sin(angle)))
        #print str(angle) + "\t" + str(hypotenuse) + "\t" + str(adjacentDistance)
        return adjacentDistance
