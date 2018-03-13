#!/usr/bin/env python
import helper
import rospy as rp
import cv2
from sensor_msgs.msg import Image, Joy
from cv_bridge import CvBridge, CvBridgeError
from ackermann_msgs.msg import AckermannDriveStamped, AckermannDrive

VERBOSE=False
DEBUG=True
DISPLAY=False

class Controller:
    kill_switch = 0

    def __init__(self):
        '''Initialize ros publisher, ros subscriber'''
        # topic where we publish
        self.vesc = rp.Publisher("/vesc/high_level/ackermann_cmd_mux/input/nav_0", AckermannDriveStamped, queue_size=1)
        self.bridge = CvBridge()
        # subscribed topic
        rp.Subscriber("vesc/joy", Joy, self.joy_callback)
        rp.Subscriber("eyes", Image, self.eyes_callback)
        if VERBOSE:
            print "subscribed to /crying_eyes"

    def eyes_callback(self, ros_data):
        '''Callback function of subscribed topic.
        Here images get converted and commands published.'''
        if VERBOSE:
            print 'recieved image of type: %s' % ros_data.format
        image = self.bridge.imgmsg_to_cv2(ros_data, desired_encoding="passthrough")
        left_eye = Eye(image[0:256, 0:672], 'left')
        right_eye = Eye(image[0:256, 672:1344], 'right')

        left_eye.process()
        right_eye.process()
        linesExist = left_eye.getLinesExist or right_eye.getLinesExist
        firstLinesSeen = left_eye.getFirstLinesSeen() and right_eye.getFirstLinesSeen()
        self.controller_(left_eye.getSlope(), right_eye.getSlope(), linesExist, firstLinesSeen)
        if DISPLAY:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                pass


    def joy_callback(self, ros_data):
        self.kill_switch = ros_data.buttons[5]


    def controller_(self, leftSlope, rightSlope, linesExist, firstLinesSeen):
        error = leftSlope + rightSlope # sum of slopes
        # steeringControl = (0.3/2.5)*error
        steeringControl = self.pid_controller(error)
        if steeringControl > 0.3:
            steeringControl = 0.3
        if steeringControl < -0.3:
            steeringControl = -0.3
        direction = ""
        if steeringControl > 0.02:
            direction = "Left"
        elif steeringControl < -0.02:
            direction = "Right"
        else:
            direction = "Center"
        if DEBUG and firstLinesSeen:
            # print "=================="
	    print "|Left    |Right   |Sum     |Control |Direction|"
	    print "|%f|%f|%f|%f|%s     |" % (leftSlope, rightSlope, sumOfSlopes, steeringControl, direction)
            # print "(Left|Right): (%f|%f)" % (leftSlope, rightSlope)
            # print "Sum: %f" % (sumOfSlopes)
            # print "(Control|Direction): (%f|%s)" % (steeringControl, direction)
        speedLimit = 0.6
        speedPower = 1.13678
        speedControl = speedLimit * (1 - abs(steeringControl))**speedPower
        # speed_control = 0.4
        drive_msg_stamped = AckermannDriveStamped()
        drive_msg = AckermannDrive()

        self.logic(drive_msg, speedControl, steeringControl, linesExist)
        drive_msg_stamped.drive = drive_msg
        self.vesc.publish(drive_msg_stamped)


    def logic(self, drive_msg, speed_control, steering_control, lines_exist):
	if self.kill_switch:
	    if lines_exist:
		self.apply_control(drive_msg, speed_control, steering_control)
	    else:
		self.apply_control(drive_msg, 1, 0)
	else:
	    self.stop(drive_msg)


    def apply_control(self, msg, speed, steering_angle):
        msg.speed = speed
        msg.steering_angle = steering_angle
        msg.acceleration = 0
        msg.jerk = 0
        msg.steering_angle_velocity = 0


    def stop(self, msg):
        msg.speed = 0
        msg.steering_angle = 0
        msg.acceleration = 0
        msg.jerk = 0
        msg.steering_angle_velocity = 0

    def pid_controller(self, error):
        self.errorList = [0], self.HISTORYSIZE = 10
        length = len(self.errorList)

        # if list is larger than the desired history size -1, remove item at index 0
    	if (length > self.HISTORYSIZE-1):
    		self.errorList.pop(0)

        self.errorList.append(error) # adds new error to last position in array

        P = I = D = 0
    	for x in self.errorList:
    		I += x

        P = self.errorList[length-1]
    	I = (I/length) # averages values
        D = 1 # Placeholder for now.

        Kp = (0.3/2.5) # 0.12
        Ki = 0 # ignored
        Kd = 0 # ignored
        return (Kp * P) + (Ki * I) + (Kd * D)


class Eye:
    slope = 0.0
    helper_functions = helper.Functions()

    def __init__(self, image, eye):
        self.image = image
        self.eye = eye

    def process(self):
        if DISPLAY:
            cv2.imshow(self.eye + ' Eye', self.frame_processor(self.image))
        else:
            self.frame_processor(self.image)

    def frame_processor(self, image):
        f = self.helper_functions
        color = f.hsv_color_selection(image)
        gray = f.gray_scale(color)
        smooth = f.gaussian_smoothing(gray)
        edges = f.canny_detector(smooth)
        hough = f.hough_transform(edges)
        self.slope = f.getSlope()
	self.linesExist = f.getLinesExist()
	self.firstLinesSeen = f.getFirstLinesSeen()
        result = f.draw_lane_line(image, f.lane_line(image, hough))
        return result


    def getSlope(self):
        return self.slope


    def getLinesExist(self):
	return self.linesExist


    def getFirstLinesSeen(self):
	return self.firstLinesSeen


if __name__ == '__main__':
    rp.init_node("controller", anonymous=True)
    controller = Controller()
    try:
        rp.spin()
    except KeyboardInterrupt:
        print "Shutting down ROS Image feature detector module."
    cv2.destroyAllWindows()
#=================================================================
#/////////////////////////////////////////////////////////////////
#=================================================================
