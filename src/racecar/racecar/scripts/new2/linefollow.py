#!/usr/bin/python
# ----------------
#

from autonomous import Autonomous

class LineFollow(Autonomous):

    def __init__(self, zed):
        self.decide(self.control(self.process( zed.getImage() )))

    # I need to seperate the processing done in Camera (and the zed file in general).
    def process(self, image):
        left = processCamera(image[0:256, 0:672], 'left')
        right = processCamera(image[0:256, 672:1344], 'right')
        linesExist = left.getLinesExist() or right.getLinesExist()
        firstLinesSeen = left.getFirstLinesSeen() and right.getFirstLinesSeen()
        return left.getSlope(), right.getSlope(), linesExist, firstLinesSeen


    def processCamera(self, image, camera):
        processedFrame = self.processFrame(image)
        if DISPLAY:
            cv2.imshow(eye + ' Eye', processedFrame)


    def processFrame(self, image):
        util   = Utility()
        color  = util.hsv_color_selection(image)
        gray   = util.gray_scale(color)
        smooth = util.gaussian_smoothing(gray)
        edges  = util.canny_detector(smooth)
        hough  = util.hough_transform(edges)
        self.linesExist     = util.getLinesExist()
        self.firstLinesSeen = util.getFirstLinesSeen()
        if DISPLAY:
            result = util.draw_lane_line(image, util.lane_line(image, hough))
            return result
        else:
            util.lane_line(image, hough)
        self.slope = util.getSlope()


    def control(self, leftSlope, rightSlope, linesExist, firstLinesSeen):
        direction = ""
        error = leftSlope + rightSlope # sum of slopes
        steeringAngle = self.pid(error, (0.3/2.5), 0, 0)
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
        self.zedData = [speed, steeringAngle, linesExist]


    def decide(self, speed, steeringAngle, linesExist):
        if linesExist:
            self.apply_control(speed, steeringAngle)
        else:
            self.apply_control(1, 0)
