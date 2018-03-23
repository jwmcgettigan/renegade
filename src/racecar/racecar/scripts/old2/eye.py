#!/usr/bin/python
import helper
import rospy as rp
import cv2
from sensor_msgs.msg import Image, Joy
from cv_bridge import CvBridge, CvBridgeError
from ackermann_msgs.msg import AckermannDriveStamped, AckermannDrive

VERBOSE=False # not used
DEBUG=False # not used
DISPLAY=False


class Eye:
    slope = 0.0
    helper_functions = helper.Functions()

    def __init__(self, image, eye):
        self.image = image
        self.eye = eye
        if DISPLAY:
            cv2.imshow(self.eye + ' Eye', self.frame_processor(self.image))
        self.frame_processor(self.image)


    def frame_processor(self, image):
        f = self.helper_functions
        color = f.hsv_color_selection(image)
        gray = f.gray_scale(color)
        smooth = f.gaussian_smoothing(gray)
        edges = f.canny_detector(smooth)
        hough = f.hough_transform(edges)
        self.linesExist = f.getLinesExist()
        self.firstLinesSeen = f.getFirstLinesSeen()
        if DISPLAY:
            result = f.draw_lane_line(image, f.lane_line(image, hough))
            return result
        else:
            f.lane_line(image, hough)
        self.slope = f.getSlope()


    def getSlope(self):
        return self.slope


    def getLinesExist(self):
        return self.linesExist


    def getFirstLinesSeen(self):
        return self.firstLinesSeen


#=================================================================
#/////////////////////////////////////////////////////////////////
#=================================================================
