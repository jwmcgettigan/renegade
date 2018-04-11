#!/usr/bin/python
# ----------------
#

from mode import Mode
from cone import Cone
import cv2, numpy as np

DISPLAY=True
DEBUG=True

class Serpentine(Mode):

    def __init__(self, zed, vesc):
        super(Serpentine, self).__init__(vesc)
        self.process(zed.getImage().copy())


    def process(self, image):
        left = self.camera(image[0:256, 0:672], 'left')
        right = self.camera(image[0:256, 672:1344], 'right')

        return self.control(left.getCenter(), right.getCenter())


    def camera(self, image, side):
        cone = self.detectCone(image)
        if DISPLAY:
            cv2.imshow(side + ' Camera', cone.draw())
            cv2.waitKey(1)
        return cone


    def detectCone(self, image):
        """Detects the closest cone"""
        color = self.color
        maskedImage = self.colorMask(image, color[0])
        imgray = cv2.cvtColor(maskedImage, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(imgray, (5,5), 0)
        thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY)[1]
        contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
        if len(contours) > 0:
            c = max(contours, key = cv2.contourArea)
            return Cone(c, image)
            #for c in contours:
                #if largest and closest, create cone object
        else:
            pass


    def control(self, lCenter, rCenter):
        if lCenter == [0, 0] and rCenter == [0, 0]: coneSeen = False
        else: coneSeen = True
        #coneSeen = (False if lCenter == [0, 0] and rCenter == [0, 0] else True)
        vCenter = lCenter[0]+rCenter[0]/2, lCenter[1]+rCenter[1]/2
        direction = ""
        error = 0
        steeringAngle = 0
        if steeringAngle > 0.3: steeringAngle = 0.3
        if steeringAngle < -0.3: steeringAngle = -0.3
        if steeringAngle > 0.02: direction = "Left"
        elif steeringAngle < -0.02: direction = "Right"
        else: direction = "Center"
        #speedLimit = 0.6
        #speedPower = 1.13678
        #speed = speedLimit * (1 - abs(steeringAngle))**speedPower
        speed = 0.4
        if DEBUG and coneSeen:
            print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
            print "Direction:\t "       +    direction
            print "Steering Angle:\t %.4f" % steeringAngle
            print "Speed:\t\t %.4f"        % speed
            print "\nError:\t\t %.4f"      % error
            print "Left Cener:\t %s"       % (lCenter,)
            print "Right Center:\t %s"     % (rCenter,)
            print "Average Center:\t %s"   % (aCenter,)
        return self.decide(speed, steeringAngle, coneSeen)


    def decide(self, speed, steeringAngle, coneSeen):
        if coneSeen:
            self.apply_control(speed, steeringAngle)
        else:
            self.apply_control(1, 0)
