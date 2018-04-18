#!/usr/bin/python
# ----------------
#

from item import Item
import cv2, numpy as np

DEBUG=False

class Line(Item):
    slope = x1 = 0.0

    def __init__(self, image):
        self.coords = self.create(image)
        self.image = image


    def getSlope(self):
        return self.slope


    def getCoords(self):
        return self.coords


    def getLinesExist(self):
        return self.linesExist


    def getFirstLinesSeen(self):
        return self.firstLinesSeen


    def create(self, image):
        houghLines = self.processFrame(image)
        try:
            y1 = image.shape[0]
            y2 = 0
            coords = self.pixelPoints(y1, y2, self.averageSlopeIntercept(houghLines), image)
            return coords
        except:
            pass


    def draw(self, thickness=12):
        """
        Draw lines onto the input image.
            Parameters:
                image: The input test image.
                coords: The pixel coordinates of the line.
                thickness (Default = 12): Line thickness.
        cv2.line(img, pt1, pt2, color, thickness)
        cv2.line(img, (x1, y1), (x2, y2), [0, 0, 255], thickness)
        """
        line_image = np.zeros_like(self.image)
        #cv2.line(line_image, (Functions.x1, lines[0][1]), lines[1], [0, 255, 0], thickness)
        try:
            cv2.line(line_image, self.coords[0], self.coords[1], [0, 0, 255], thickness)
            return cv2.addWeighted(self.image, 1.0, line_image, 1.0, 0.0)
        except:
            #print "CAN'T DRAW LINE"
            return self.image


    # Do I need to create a new Utility object every loop?
    # It would be better if I only need to call it once.
    def processFrame(self, image):
        util   = Utility()
        color  = util.hsv_color_selection(image)
        gray   = util.gray_scale(color)
        smooth = util.gaussian_smoothing(gray)
        edges  = util.canny_detector(smooth)
        hough  = util.hough_transform(edges) # hough lines
        self.linesExist     = util.getLinesExist()
        self.firstLinesSeen = util.getFirstLinesSeen()
        return hough


    def averageSlopeIntercept(self, houghLines):
        """
        Find the slope and intercept of the lanes of each image.
            Parameters:
                lines: The output lines from Hough Transform.
        """
        lines = []  # (slope, intercept)
        weights = []  # (length)
        for line in houghLines:
            if line is not None:
                for x1, y1, x2, y2 in line:
                    if x1 == x2: # Try removing this if statement. It may harm our algorithm some.
                        continue
                    x1 = float(x1)
                    y1 = float(y1)
                    x2 = float(x2)
                    y2 = float(y2)
                    slope = (y2 - y1) / (x2 - x1)
                    intercept = y1 - (slope * x1)
                    length = np.sqrt(((y2 - y1) ** 2) + ((x2 - x1) ** 2))
                    lines.append((slope, intercept))
                    weights.append(length)
        slopeIntercept = np.dot(weights, lines) / np.sum(weights) if len(weights) > 0 else None
        return slopeIntercept


    def pixelPoints(self, y1, y2, slopeIntercept, image):
        """
        Converts the slope and intercept of each line into pixel points.
            Parameters:
                y1: y-value of the line's starting point.
                y2: y-value of the line's end point.
                line: The slope and intercept of the line.
        """
        slope, intercept = slopeIntercept
        if slope == 0.0:
            slope += 0.000001

        x1 = image.shape[1]/2
        x2 = (y2 - intercept) / slope
        self.x1 = int((y1 - intercept) / slope)
        self.slope = (x2 - x1) / (y2 - y1)
        x1 = int(x1)
        x2 = int(x2)
        y1 = int(y1)
        y2 = int(y2)
        if DEBUG and self.firstLinesSeen:
            print "GUIDE (x1|x2|y1|y2): (" + str(x1)      + "|" + str(x2) + "|" + str(y1) + "|" + str(y2) + ")"
            print "FOLLOW(x1|x2|y1|y2): (" + str(self.x1) + "|" + str(x2) + "|" + str(y1) + "|" + str(y2) + ")"
        return (x1, y1), (x2, y2)



class Utility:
    firstLinesSeen = False
    lastHoughLines = None

    def __init__(self):
        pass


    def getLinesExist(self):
        return self.linesExist


    def getFirstLinesSeen(self):
        return self.firstLinesSeen


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
                print "A line has been detected."
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
    def weighted_img(self, img, initial_img, a=0.8, b=1., y=0.):
        """ 'img' is the output of the hough_lines(), An image with lines drawn on it.
        Should be a blank image (all black) with lines drawn on it.
        'initial_img' should be the image before any processing."""
        return cv2.addWeighted(initial_img, a, img, b, y)
