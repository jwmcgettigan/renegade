#!/usr/bin/env python
import rospy as rp
import functions as f
import controller as con
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from ackermann_msgs.msg import AckermannDriveStamped, AckermannDrive

VERBOSE=False
DEBUG=True
DISPLAY=True

class Controller:

    def __init__(self):
        '''Initialize ros publisher, ros subscriber'''
        #topic where we publish
        vesc = rp.Publisher("/vesc/high_level/ackermann_cmd_mux/input/nav_0", AckermannDriveStamped, queue_size=1)
        self.bridge = CvBridge()
        #subscribed topic
        rp.Subscriber("eyes", Image, callback)
        if VERBOSE:
            print "subscribed to /crying_eyes"

    def callback(self, ros_data):
        '''Callback function of subscribed topic.
        Here images get converted and commands published.'''
        if VERBOSE:
            print 'recieved image of type: %s' % ros_data.format
        image = self.bridge.imgmsg_to_cv2(data, desired_encoding="passthrough")
        left_eye = Eye(image[0:256, 0:672], 'left')
        right_eye = Eye(image[0:256, 672:1344], 'right')

        left_eye.process()
        right_eye.process()
        controller(left_eye.getSlope(), right_eye.getSlope())
        if DISPLAY:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                pass


    def controller(self, left_slope, right_slope):
        if DEBUG:
            print "=================="
            print "(Left|Right): (" + str(right_slope) + "|" + str(left_slope) + ")"
            print "Sum: " + str(left_slope + right_slope)
        control = con.turn_control(left_slope + right_slope)
        control = 0.3 if control > 0.3
        control = -0.3 if control < -0.3
        direction = ""
        if control > 0.02:
            direction = "Left"
        elif control < -0.02:
            direction = "Right"
        else:
            direction = "Center"
        print "(Control|Direction): (" + str(control) + "|" + str(direction) + ")"
        speed_limit = 0.6
        speed_control = speed_limit * (1 - abs(control))**1.13678
        #speed_control = 0.4
        if f.getLinesExist:
        	apply_control(speed_control, control)
        else:
            stop()
            #apply_control(1, 0)


    def apply_control(self, speed, steering_angle):
        drive_msg_stamped = AckermannDriveStamped()
        drive_msg = AckermannDrive()
        drive_msg.speed = speed
        drive_msg.steering_angle = steering_angle
        drive_msg.acceleration = 0
        drive_msg.jerk = 0
        drive_msg.steering_angle_velocity = 0
        drive_msg_stamped.drive = drive_msg
        vesc.publish(drive_msg_stamped)

    def stop(self):
        drive_msg_stamped = AckermannDriveStamped()
        drive_msg = AckermannDrive()
        drive_msg.speed = 0
        drive_msg.steering_angle = 0
        drive_msg.acceleration = 0
        drive_msg.jerk = 0
        drive_msg.steering_angle_velocity = 0
        drive_msg_stamped.drive = drive_msg
        vesc.publish(drive_msg_stamped)


class Eye:
    slope = 0.0

    def __init__(self, image, eye):
        self.image = image
        self.eye = eye

    def process(self):
        if DISPLAY:
            cv2.imshow(self.eye + ' Eye', frame_processor(self.image, self.eye))
        else:
            frame_processor(self.image, self.eye)

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
