#!/usr/bin/python
# ----------------
#

import cv2, numpy as np

# Should I have start and kill functions?
# I need to relate the processing functions to the mode rather than the component.
class Mode(object):

    def __init__(self, vesc):
        self.driveMsg = vesc.getDriveMsg()
        self.color = self.colorDict()[2]


    def apply_control(self, speed, steeringAngle):
        self.driveMsg.speed = speed
        self.driveMsg.steering_angle = steeringAngle


    def stop(self):
        self.driveMsg.speed = 0


    def getCommands(self):
        pass


    def colorDict(self):
        red =    [np.uint8([  0,   0,  0]), np.uint8([  0,   0,   0])], 'red'
        blue =   [np.uint8([  0,  80,  0]), np.uint8([ 17, 255, 255])], 'blue'
        yellow = [np.uint8([ 93, 190, 77]), np.uint8([106, 255, 255])], 'yellow'
        orange = [np.uint8([104, 209,  0]), np.uint8([122, 255, 255])], 'orange'
        return red, blue, yellow, orange


    def colorMask(self, image, color):
        cvtImage = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(cvtImage, color[0], color[1])
        return cv2.bitwise_and(image, image, mask=mask)
