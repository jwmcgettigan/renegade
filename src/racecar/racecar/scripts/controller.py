#!/usr/bin/env python
import eye
import cv2
import rospy as rp
from sensor_msgs.msg import Image, Joy
from cv_bridge import CvBridge, CvBridgeError
from ackermann_msgs.msg import AckermannDriveStamped, AckermannDrive

VERBOSE=False
DEBUG=True
DISPLAY=False
RECORD=False

class Controller:
    kill_switch = 0
    errorList = [0], HISTORYSIZE = 10

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


    def eyes_callback(self, ros_data): # ros_data = img_msg = Image()
        '''Callback function of subscribed topic.
        Here images get converted and commands published.'''
        if VERBOSE:
            print 'recieved image of type: %s' % ros_data.format
        image = self.bridge.imgmsg_to_cv2(ros_data, desired_encoding="passthrough")

        left_eye = eye.Eye(image[0:256, 0:672], 'left')
        right_eye = eye.Eye(image[0:256, 672:1344], 'right')

        linesExist = left_eye.getLinesExist or right_eye.getLinesExist
        firstLinesSeen = left_eye.getFirstLinesSeen() and right_eye.getFirstLinesSeen()
        self.controller_(left_eye.getSlope(), right_eye.getSlope(), linesExist, firstLinesSeen)
        if DISPLAY and if cv2.waitKey(1) & 0xFF == ord('q'):
            pass


    def joy_callback(self, ros_data): # ros_data = joy_msg = Joy()
        self.kill_switch = ros_data.buttons[5]


    def controller_(self, leftSlope, rightSlope, linesExist, firstLinesSeen):
        direction = ""
        error = leftSlope + rightSlope # sum of slopes
        # steeringAngle = (0.3/2.5)*error
        steeringAngle = self.pid_controller(error)
        if steeringAngle > 0.3: steeringAngle = 0.3
        if steeringAngle < -0.3: steeringAngle = -0.3
        if steeringAngle > 0.02: direction = "Left"
        elif steeringAngle < -0.02: direction = "Right"
        else: direction = "Center"
        if DEBUG and firstLinesSeen:
            # print "=================="
            print "|Left    |Right   |Sum     |Control |Direction|"
            print "|%f|%f|%f|%f|%s     |" % (leftSlope, rightSlope, sumOfSlopes, steeringAngle, direction)
            # print "(Left|Right): (%f|%f)" % (leftSlope, rightSlope)
            # print "Sum: %f" % (sumOfSlopes)
            # print "(Control|Direction): (%f|%s)" % (steeringAngle, direction)
        speedLimit = 0.6
        speedPower = 1.13678
        speed = speedLimit * (1 - abs(steeringAngle))**speedPower
        # speed = 0.4
        drive_msg_stamped = AckermannDriveStamped()
        drive_msg = AckermannDrive()

        self.logic(drive_msg, speed, steeringAngle, linesExist)
        drive_msg_stamped.drive = drive_msg
        self.vesc.publish(drive_msg_stamped)


    def logic(self, drive_msg, speed, steeringAngle, linesExist):
        if self.kill_switch:
            if lines_exist:
                self.apply_control(drive_msg, speed, steeringAngle)
            else:
                self.apply_control(drive_msg, 1, 0)
        else:
            self.stop(drive_msg)


    def apply_control(self, msg, speed, steeringAngle):
        msg.speed = speed
        msg.steering_angle = steeringAngle
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
