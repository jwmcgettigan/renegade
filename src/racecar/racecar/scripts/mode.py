#!/usr/bin/python
# ----------------
#

import cv2, numpy as np

# Should I have start and kill functions?
# I need to relate the processing functions to the mode rather than the component.
class Mode(object):

    def __init__(self):
        self.color = self.colorDict()


    def apply_control(self, speed, steeringAngle):
        self.driveMsg.speed = speed
        self.driveMsg.steering_angle = steeringAngle


    def getCommands(self):
        pass


    def colorDict(self):
        """
        red =    [np.uint8([110, 185, 0]), np.uint8([130, 255, 255])], 'red'
        green =  [np.uint8([20, 40, 0]), np.uint8([90, 255, 180])], 'green'
        blue =   [np.uint8([  0,  80,  0]), np.uint8([ 17, 255, 255])], 'blue'
        yellow = [np.uint8([ 93, 190, 77]), np.uint8([106, 255, 255])], 'yellow'
        #orange = [np.uint8([104, 209,  0]), np.uint8([122, 255, 255])], 'orange'
        orange = [np.uint8([110, 200,  100]), np.uint8([125, 255, 255])], 'orange'
        greyBlue = [np.uint8([0, 0, 87]), np.uint8([96, 255, 174])], 'greyBlue'
        #greyBlue = [np.uint8([0, 0, 50]), np.uint8([180, 70, 174])], 'greyBlue'
        #greyBlue = [np.uint8([0, 10, 110]), np.uint8([30, 255, 255])], 'greyBlue'
        blueGreyBlue = [np.uint8([10, 90, 130]), np.uint8([20, 185, 215])], 'blueGreyBlue'
        #lane = [np.uint8([0, 120, 100]), np.uint8([30, 255, 255])], 'lane'
        #lane = [np.uint8([0, 0, 90]), np.uint8([100, 100, 140])], 'lane'
        #lane = [np.uint8([0, 0, 0]), np.uint8([100, 100, 140])], 'lane'
        lane = [np.uint8([71, 109, 109]), np.uint8([161, 133, 141])], 'lane'
        """

        red = (np.uint8([0, 150, 140]), np.uint8([255, 190, 160])), 'red'
        green = (np.uint8([0, 110, 0]), np.uint8([60, 120, 255])), 'green'
        #blue = [np.uint8([71, 109, 109]), np.uint8([161, 133, 141])], 'blue'
        #blue = [np.uint8([0, 90, 80]), np.uint8([255, 140, 125])], 'blue' # LAB
        #blue = [np.uint8([0, 0, 110]), np.uint8([30, 255, 255])], 'blue' # RGB2HSV
        blue = (np.uint8([90, 90, 0]), np.uint8([110, 255, 255])), 'blue' # BGR2HSV
        return red, green, blue


    def colorMask(self, image, color):
        if color[1] is "blue":
            cvtImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        else:
            cvtImage = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        color = color[0]
        mask = cv2.inRange(cvtImage, color[0], color[1])
        return cv2.bitwise_and(image, image, mask=mask)
