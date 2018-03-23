#!/usr/bin/env python
import cv2, numpy as np

DEBUG = False
VERBOSE = False

class Functions:
    slope = x1 = 0.0
    firstLinesSeen = False
    linesExist = True
    lastHoughLines = None

    def __init__(self):
        pass


    def nothing(self):
        pass


    def hsv_color_selection(self, image):
        """Apply blue color mask"""
        converted = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        lower = np.uint8([0, 80, 0])
        upper = np.uint8([17, 255, 255])
        mask = cv2.inRange(converted, lower, upper)
        return cv2.bitwise_and(image, image, mask=mask)


    def gray_scale(self, image):
        """Applies the grayscale transform"""
        return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)


    def gaussian_smoothing(self, image):
        """Applies a gaussian noise kernel"""
        kernel_size = 3
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)


    def canny_detector(self, image):
        """Applies the canny transform"""
        low_threshold = 100
        high_threshold = 200
        return cv2.Canny(image, low_threshold, high_threshold)


    #=============================================================
    def hough_transform(self, image):
        """
        Determine and cut the region of interest in the input image.
            Parameters:
                image: The output of a Canny transform.
        """
        rho = 1              #Distance resolution of the accumulator in pixels.
        theta = np.pi/180    #Angle resolution of the accumulator in radians.
        threshold = 35#5     #Only lines that are greater than threshold will be returned.
        minLineLength = 30#3   #Line segments shorter than that are rejected.
        maxLineGap = 300#15   #Maximum allowed gap between points on the same line to link them

        houghLines = cv2.HoughLinesP(image, rho = rho, theta = theta, threshold = threshold, minLineLength = minLineLength, maxLineGap = maxLineGap)
        if houghLines is not None:
	    if self.firstLinesSeen == False:
                print "\nA line has been detected.\n"
                self.firstLinesSeen = True
            self.linesExist = True
            self.lastHoughLines = houghLines
            return houghLines
        elif self.lastHoughLines is not None:#Functions.lastHoughLinesLeft is not None or Functions.lastHoughLinesRight is not None:
            self.linesExist = False
            return self.lastHoughLines
        else:
            self.linesExist = False
            print "\rA line is yet to be detected.",
    #=============================================================
    def average_slope_intercept(self, lines):
        """
        Find the slope and intercept of the lanes of each image.
            Parameters:
                lines: The output lines from Hough Transform.
        """
        lines_ = []  # (slope, intercept)
        weights = []  # (length)
        for line in lines:
            if line is not None:
                for x1, y1, x2, y2 in line:
                    if x1 == x2:
                        continue
                    x1 = float(x1)
                    y1 = float(y1)
                    x2 = float(x2)
                    y2 = float(y2)
                    slope = (y2 - y1) / (x2 - x1)
                    intercept = y1 - (slope * x1)
                    length = np.sqrt(((y2 - y1) ** 2) + ((x2 - x1) ** 2))
                    lines_.append((slope, intercept))
                    weights.append(length)
        lane = np.dot(weights, lines_) / np.sum(weights) if len(weights) > 0 else None
        return lane
    #=============================================================
    def pixel_points(self, y1, y2, line, image):
        """
        Converts the slope and intercept of each line into pixel points.
            Parameters:
                y1: y-value of the line's starting point.
                y2: y-value of the line's end point.
                line: The slope and intercept of the line.
        """
        slope, intercept = line
        if slope == 0.0:
            slope += 0.000001

        x1 = image.shape[1]/2
        x2 = (y2 - intercept) / slope
        self.x1 = int((y1 - intercept) / slope)
        self.slope = (x2 - x1)/(y2 - y1)
        x1 = int(x1)
        x2 = int(x2)
        y1 = int(y1)
        y2 = int(y2)
        if DEBUG and self.firstLinesSeen:
            print "GUIDE(x1|x2|y1|y2): (" + str(x1) + "|" + str(x2) + "|" + str(y1) + "|" + str(y2) + ")"
            print "FOLLOW(x1|x2|y1|y2): (" + str(self.x1) + "|" + str(x2) + "|" + str(y1) + "|" + str(y2) + ")"
        return (x1, y1), (x2, y2)
    #=============================================================
    def lane_line(self, image, lines):
        """
        Create full length lines from pixel points.
            Parameters:
                image: The input test image.
                lines: The output lines from Hough Transform.
        """
        try:
            lane = self.average_slope_intercept(lines)
            y1 = image.shape[0]
            y2 = 0
            line = self.pixel_points(y1, y2, lane, image)
            return line
        except:
            pass
    #=============================================================
    def draw_lane_line(self, image, lines, thickness=12):
        """
        Draw lines onto the input image.
            Parameters:
                image: The input test image.
                lines: The output lines from Hough Transform.
                thickness (Default = 12): Line thickness.
        cv2.line(img, pt1, pt2, color, thickness)
        cv2.line(img, (x1, y1), (x2, y2), [0, 0, 255], thickness)
        """
        line_image = np.zeros_like(image)
        #cv2.line(line_image, (Functions.x1, lines[0][1]), lines[1], [0, 255, 0], thickness)
        try:
            self.isLine = True
            cv2.line(line_image, lines[0], lines[1], [0, 0, 255], thickness)
            return cv2.addWeighted(image, 1.0, line_image, 1.0, 0.0)
        except:
            pass
    #=============================================================
    def weighted_img(self, img, initial_img, a=0.8, b=1., y=0.):
        """ 'img' is the output of the hough_lines(), An image with lines drawn on it.
        Should be a blank image (all black) with lines drawn on it.
        'initial_img' should be the image before any processing."""
        return cv2.addWeighted(initial_img, a, img, b, y)


    def getSlope(self):
        return self.slope


    def getLinesExist(self):
        return self.linesExist

    def getFirstLinesSeen(self):
	return self.firstLinesSeen

#=================================================================
#/////////////////////////////////////////////////////////////////
#=================================================================
