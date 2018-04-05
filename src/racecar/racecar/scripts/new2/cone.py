#!/usr/bin/python
# ----------------
#

class Cone:
    # color (hsv)
    # size (radius)

    def __init__(self, image):
        self.detect(image)
        pass


    def detect(self):


    def processFrame(self):


class Utility:

    def __init__(self):
        pass

    def color_detection(self, image):
        # have a colors dictionary to define what colors we care about
        red = [0, 0, 0], [0, 0, 0]
        blue = [0, 80, 0], [17, 255, 255]
        yellow = [0, 0, 0], [0, 0, 0]
        orange = [0, 0, 0], [0, 0, 0]


    def hsv_color_selection(self, image, color):
        """Apply color mask"""
        converted = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        lower = np.uint8(color[0])
        upper = np.uint8(color[1])
        mask = cv2.inRange(converted, lower, upper)
        return cv2.bitwise_and(image, image, mask=mask)
