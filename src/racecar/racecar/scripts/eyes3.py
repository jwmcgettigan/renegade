#!/usr/bin/env python
import rospy as rp
import functions as f
import controller as con
import cv2
from sensor_msgs.msg import Image, Joy
from cv_bridge import CvBridge, CvBridgeError
from ackermann_msgs.msg import AckermannDriveStamped, AckermannDrive

VERBOSE=False
DEBUG=True
DISPLAY=True

class Controller:
    kill_switch = 0
    
    def __init__(self):
        '''Initialize ros publisher, ros subscriber'''
        #topic where we publish
        self.vesc = rp.Publisher("/vesc/high_level/ackermann_cmd_mux/input/nav_0", AckermannDriveStamped, queue_size=1)
        self.bridge = CvBridge()
        #subscribed topic
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
        self.controller_(left_eye.get_slope(), right_eye.get_slope())
        if DISPLAY:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                pass


    def joy_callback(self, ros_data):
        Controller.kill_switch = ros_data.buttons[5]


    def controller_(self, left_slope, right_slope):
        sum_of_slopes = left_slope + right_slope
        #steering_control = con.turn_control(sum_of_slopes)
        steering_control = (0.3/2.5)*sum_of_slopes
        if steering_control > 0.3:
            steering_control = 0.3
        if steering_control < -0.3:
            steering_control = -0.3
        direction = ""
        if steering_control > 0.02:
            direction = "Left"
        elif steering_control < -0.02:
            direction = "Right"
        else:
            direction = "Center"
        if DEBUG:
            print "=================="
            print "(Left|Right): (" + str(right_slope) + "|" + str(left_slope) + ")"
            print "Sum: " + str(sum_of_slopes)
            print "(Control|Direction): (" + str(steering_control) + "|" + str(direction) + ")"
        speed_limit = 0.6
        speed_power = 1.13678
        speed_control = speed_limit * (1 - abs(steering_control))**speed_power
        #speed_control = 0.4
        drive_msg_stamped = AckermannDriveStamped()
        drive_msg = AckermannDrive()
        if f.getLinesExist and Controller.kill_switch:
            self.apply_control(drive_msg, speed_control, steering_control)
        else:
            self.stop(drive_msg)
            #apply_control(1, 0)
        drive_msg_stamped.drive = drive_msg
        self.vesc.publish(drive_msg_stamped)


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


class Eye:
    slope = 0.0

    def __init__(self, image, eye):
        self.image = image
        self.eye = eye

    def process(self):
        if DISPLAY:
            cv2.imshow(self.eye + ' Eye', self.frame_processor(self.image, self.eye))
        else:
            self.frame_processor(self.image, self.eye)

    def frame_processor(self, image, side):
        color = f.hsv_color_selection(image)
        gray = f.gray_scale(color)
        smooth = f.gaussian_smoothing(gray)
        edges = f.canny_detector(smooth)
        hough = f.hough_transform(edges, side)
        Eye.slope = f.getSlope()
        result = f.draw_lane_line(image, f.lane_line(image, hough))
        return result


    def get_slope(self):
        return Eye.slope


if __name__ == '__main__':
    controller = Controller()
    rp.init_node("controller", anonymous=True)
    try:
        rp.spin()
    except KeyboardInterrupt:
        print "Shutting down ROS Image feature detector module."
    cv2.destroyAllWindows()
#=================================================================
#/////////////////////////////////////////////////////////////////
#=================================================================
