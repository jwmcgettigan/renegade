#!/usr/bin/python
# ----------------
#

from mode import Mode
from line import Line
import cv2

DISPLAY=False
DEBUG=False

class LineFollow(Mode):

    def __init__(self, zed, vesc):
        super(LineFollow, self).__init__(vesc)
        self.process(zed.getImage())
        vesc.setDriveMsg(self.driveMsg)
        vesc.publish()


    # I need to seperate the processing done in Camera (and the zed file in general).
    def process(self, image):
        left = self.camera(image[0:256, 0:672], 'left')
        right = self.camera(image[0:256, 672:1344], 'right')
        linesExist = left.getLinesExist() or right.getLinesExist()
        firstLinesSeen = left.getFirstLinesSeen() and right.getFirstLinesSeen()
        return self.control(left.getSlope(), right.getSlope(), linesExist, firstLinesSeen)


    def camera(self, image, side):
        line = Line(image)
        if DISPLAY:
            cv2.imshow(side + ' Camera', line.draw())
            cv2.waitKey(1)
        return line


    def control(self, leftSlope, rightSlope, linesExist, firstLinesSeen):
        direction = ""
        error = leftSlope + rightSlope # sum of slopes
        steeringAngle = (0.3/2.5)*error# self.pid(error, (0.3/2.5), 0, 0)
        if steeringAngle > 0.3: steeringAngle = 0.3
        if steeringAngle < -0.3: steeringAngle = -0.3
        if steeringAngle > 0.02: direction = "Left"
        elif steeringAngle < -0.02: direction = "Right"
        else: direction = "Center"
        speedLimit = 0.6
        speedPower = 1.13678
        speed = speedLimit * (1 - abs(steeringAngle))**speedPower
        if DEBUG and firstLinesSeen:
            print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
            print "Direction:\t "       +                                                 direction
            print "Steering Angle:\t"   + (' ' if steeringAngle > 0 else '')   + "%.4f" % steeringAngle
            print "Speed:\t\t"          + (' ' if speed > 0 else '')           + "%.4f" % speed
            print "\nError:\t\t"        + (' ' if error > 0 else '')           + "%.4f" % error
            print "Left Slope\t"        + (' ' if leftSlope > 0 else '')       + "%.4f" % leftSlope
            print "Right Slope:\t"      + (' ' if rightSlope > 0 else '')      + "%.4f" % rightSlope
        return self.decide(speed, steeringAngle, linesExist)


    def decide(self, speed, steeringAngle, linesExist):
        if linesExist:
            self.apply_control(speed, steeringAngle)
        else:
            self.apply_control(1, 0)
