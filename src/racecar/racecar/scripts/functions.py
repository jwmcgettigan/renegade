import numpy as np
import cv2
import matplotlib.pyplot as plt

mainSlope = globalX1 = 0.0
linesExist = True
lastHoughLinesLeft = lastHoughLinesRight = None
stop = False

def nothing(self):
    pass


def rgb_color_selection(image):
    # white color mask
    lower = np.uint8([200, 200, 200])
    upper = np.uint8([255, 255, 255])
    white_mask = cv2.inRange(image, lower, upper)
    # yellow color mask
    lower = np.uint8([190, 190,   0])
    upper = np.uint8([255, 255, 255])
    yellow_mask = cv2.inRange(image, lower, upper)
    # combine the mask
    mask = cv2.bitwise_or(white_mask, yellow_mask)
    masked = cv2.bitwise_and(image, image, mask = mask)
    return masked


def hsv_color_selection(image):
    converted = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    # Blue color mask
    #lower = np.uint8([0, 95, 151])
    #upper = np.uint8([13, 255, 255])
    lower = np.uint8([0, 80, 0]) # 0,125,0
    upper = np.uint8([17, 255, 255])
    mask = cv2.inRange(converted, lower, upper)
    return cv2.bitwise_and(image, image, mask=mask)


def hsl_color_selection(image):
    """
    Apply color selection to the HSL images to blackout everything except for white and yellow lane lines.
        Parameters:
            image: An np.array compatible with plt.imshow.
    """
    # Convert the input image to HSL
    converted_image = cv2.cvtColor(image, cv2.COLOR_RGB2HLS)

    # Blue color mask
    lower_threshold = np.uint8([0, 0, 34])
    upper_threshold = np.uint8([40, 255, 255])
    mask = cv2.inRange(converted_image, lower_threshold, upper_threshold)

    masked_image = cv2.bitwise_and(image, image, mask=mask)

    return masked_image


def gray_scale(img):
    """Applies the Grayscale transform"""
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)


def gaussian_smoothing(img):
    """Applies a Gaussian Noise kernel"""
    kernel_size = 3
    return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)


def canny_detector(img):
    """Applies the Canny transform"""
    low_threshold = 100
    high_threshold = 200
    return cv2.Canny(img, low_threshold, high_threshold)


def region_of_interest(image):
    """Applies an image mask.
    Only keeps the region of the image defined by the polygon
    formed from `vertices`. The rest of the image is set to black."""
    # defining a blank mask to start with
    mask = np.zeros_like(image)

    # defining a 3 channel or 1 channel color to fill the mask with depending on the input image
    if len(image.shape) > 2:
        channel_count = image.shape[2]  # i.e. 3 or 4 depending on your image
        ignore_mask_color = (255,) * channel_count
    else:
        ignore_mask_color = 255

    height, width = image.shape[:2]
    bottom_left = [(0 * width), height]
    top_left = [(0 * width), (0.5 * height)]
    top_right = [(1 * width), (0.5 * height)]
    bottom_right = [(1 * width), height]
    vertices = [np.array([[bottom_left, top_left, top_right, bottom_right]], dtype=np.int32)]
    # filling pixels inside the polygon defined by "vertices" with the fill color
    cv2.fillPoly(mask, vertices, ignore_mask_color)

    # returning the image only where mask pixels are nonzero
    masked_image = cv2.bitwise_and(image, mask)
    return masked_image


def hough_transform(image, side):
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
    #print "houghLines: " + str(houghLines)
    global linesExist, lastHoughLinesLeft, lastHoughLinesRight, stop
    if houghLines is not None:
        stop = False
        linesExist = True 
        if side == 'left':
	    lastHoughLinesLeft = houghLines
        if side == 'right':
            lastHoughLinesRight = houghLines
        return houghLines
    elif lastHoughLinesLeft is not None and lastHoughLinesRight is not None:
        #print "Couldn't find lines."
        print "Using last instance of houghLines as reference."
        stop = False
        linesExist = False
	if side == 'left':
            return lastHoughLinesLeft
        if side == 'right':
            return lastHoughLinesRight
    else:
        stop = True
        linesExist = False


def hough_lines(image, side):
    lines = hough_transform(image, side)
    line_img = np.zeros((image.shape[0], image.shape[1], 3), dtype=np.uint8)
    color = [255, 0, 0]
    thickness = 2
    for line in lines:
        if line is not None:
            for x1, y1, x2, y2 in line:
                 cv2.line(line_img, (x1, y1), (x2, y2), color, thickness)
    return line_img


def average_slope_intercept(lines):
    """
    Find the slope and intercept of the lanes of each image.
        Parameters:
            lines: The output lines from Hough Transform.
    """
    lines_ = []  # (slope, intercept)
    weights = []  # (length,)
    #print "lines: " + str(lines)
    for line in lines:
        #print "line: " + str(line)
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
                #if slope > 1:
                lines_.append((slope, intercept))
                weights.append(length)
    #print "weights: " + str(weights)
    lane = np.dot(weights, lines_) / np.sum(weights) if len(weights) > 0 else None
    return lane


def pixel_points(y1, y2, line, image):
    """
    Converts the slope and intercept of each line into pixel points.
        Parameters:
            y1: y-value of the line's starting point.
            y2: y-value of the line's end point.
            line: The slope and intercept of the line.
    """
    slope, intercept = line
    if slope == 0.0:
        slope += 0.00001

    global mainSlope, globalX1
    #x1 = (y1 - intercept) / slope
    #globalX1 = int((y2 - intercept) / slope)
    x1 = image.shape[1]/2
    x2 = (y2 - intercept) / slope
    #print "(y2-y1)/(x2-x1): " + str((y2 - y1)/(x2 - x1))
    #print "(x2-x1)/(y2-y1): " + str((x2 - x1)/(y2 - y1))
    mainSlope = (x2 - x1)/(y2 - y1)
    x1 = int(x1)
    x2 = int(x2)
    y1 = int(y1)
    y2 = int(y2)
    print "(x1|x2|y1|y2): (" + str(x1) + "|" + str(x2) + "|" + str(y1) + "|" + str(y2) + ")"
    return (x1, y1), (x2, y2)


def lane_line(image, lines):
    """
    Create full length lines from pixel points.
        Parameters:
            image: The input test image.
            lines: The output lines from Hough Transform.
    """
    lane = average_slope_intercept(lines)
    y1 = image.shape[0]
    #y2 = y1 * 0.6
    y2 = 0
    line = pixel_points(y1, y2, lane, image)
    return line


def draw_lane_line(image, lines, color=[0, 0, 255], thickness=12):
    """
    Draw lines onto the input image.
        Parameters:
            image: The input test image.
            lines: The output lines from Hough Transform.
            color (Default = red): Line color.
            thickness (Default = 12): Line thickness.
    """
    line_image = np.zeros_like(image)
    global isLine, globalX1
    isLine = True
    #print lines
    #cv2.line(line_image, (globalX1, lines[0][1]), lines[1], [0, 255, 0], thickness)
    cv2.line(line_image, lines[0], lines[1], color, thickness)
    return cv2.addWeighted(image, 1.0, line_image, 1.0, 0.0)


def weighted_img(img, initial_img, a=0.8, b=1., y=0.):
    """ 'img' is the output of the hough_lines(), An image with lines drawn on it.
    Should be a blank image (all black) with lines drawn on it.
    'initial_img' should be the image before any processing."""
    return cv2.addWeighted(initial_img, a, img, b, y)


def getSlope():
    global mainSlope
    return mainSlope


def getLinesExist():
    global linesExist
    return linesExist
