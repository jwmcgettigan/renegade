#!/usr/bin/env python
import rospy as rp
import functions as f
import controller as con
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from ackermann_msgs.msg import AckermannDriveStamped, AckermannDrive

VERBOSE=False
DISPLAY=False

class Eye:
    slope = 0.0

    def __init__(self, eye):
        self.eye = eye
        '''Initialize ros publisher, ros subscriber'''
        #topic where we publish
        vesc = rp.Publisher("/vesc/high_level/ackermann_cmd_mux/input/nav_0", AckermannDriveStamped, queue_size=1)
        self.bridge = CvBridge()
        #subscribed topic
        rp.Subscriber("eyes", Image, callback)
        if VERBOSE:
            print "subscribed to /crying_eyes"


    def frame_processor(self, image, side):
        color = f.hsv_color_selection(image)
        gray = f.gray_scale(color)
        smooth = f.gaussian_smoothing(gray)
        edges = f.canny_detector(smooth)
        hough = f.hough_transform(edges, side)
        Eye.slope = f.getSlope()
        result = f.draw_lane_line(image, f.lane_line(image, hough))
        return result


    def callback(self, ros_data):
        '''Callback function of subscribed topic.
        Here images get converted and commands published.'''
        if VERBOSE:
            print 'recieved image of type: %s' % ros_data.format
        image = bridge.imgmsg_to_cv2(data, desired_encoding="passthrough")
        if self.eye=='left':
            crop = image[0:256, 0:672]
        if self.eye=='right':
            crop = image[0:256, 672:1344]

        if DISPLAY:
            cv2.imshow(self.eye + ' Eye', frame_processor(crop, self.eye))
            controller()
            if cv2.waitKey(1) & 0xFF == ord('q'):
                pass
        else:
            frame_processor(left_img, self.eye)
            controller()


        def controller():



if __name__ == '__main__':
    left_eye = Eye('left')
    right_eye = Eye('right')
    rp.init_node("controller", anonymous=True)
    try:
        rp.spin()
    except KeyboardInterrupt:
        print "Shutting down ROS Image feature detector module."
    cv2.destroyAllWindows()


#=================================================================
#/////////////////////////////////////////////////////////////////
#=================================================================
bridge = CvBridge()
leftSlope = 0.0
rightSlope = 0.0

def frame_processor(image, side):
    hsv = f.hsv_color_selection(image)
    #hsl = f.hsl_color_selection(image)
    color_select = hsv
    gray = f.gray_scale(color_select)
    smooth = f.gaussian_smoothing(gray)
    edges = f.canny_detector(smooth)
    # region = f.region_of_interest(edges)
    hough = f.hough_transform(edges, side)

    if side=='left':
        #print "---left---"
        global leftSlope
        leftSlope = f.getSlope()

    if side=='right':
        #print "---right---"
        global rightSlope
        rightSlope = f.getSlope()

    result = f.draw_lane_line(image, f.lane_line(image, hough))
    #color_result = f.draw_lane_line(color_select, f.lane_line(color_select, hough))
    #hough_lines = f.hough_lines(edges, side)
    #weighted_hough = cv2.addWeighted(image, 1.0, f.hough_lines(edges), 1.0, 0.0)
    return result

vesc = rp.Publisher("/vesc/high_level/ackermann_cmd_mux/input/nav_0", \
                      AckermannDriveStamped, queue_size=1)

def callback(data):
    img = bridge.imgmsg_to_cv2(data, desired_encoding="passthrough")
    #left_img = img[0:188, 0:672]
    #right_img = img[0:188, 672:1344]
    #left_img = img[0:376, 0:672]
    #right_img = img[0:376, 672:1344]
    left_img = img[0:256, 0:672]
    right_img = img[0:256, 672:1344]

    cv2.imshow('Left Eye', frame_processor(left_img, 'left'))
    cv2.imshow('Right Eye', frame_processor(right_img, 'right'))
    #frame_processor(left_img, 'left')
    #frame_processor(right_img, 'right')
    controller()
    if cv2.waitKey(1) & 0xFF == ord('q'):
        pass


rp.Subscriber("eyes", Image, callback)


def controller():
    global leftSlope, rightSlope
    print "=================="
    print "(Left|Right): (" + str(rightSlope) + "|" + str(leftSlope) + ")"
    print "Sum: " + str(leftSlope + rightSlope)
    control = con.turn_control(leftSlope + rightSlope)
    if control > 0.3:
        control = 0.3
    if control < -0.3:
        control = -0.3
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
    #else:
        #stop()
        #apply_control(1, 0)


def apply_control(speed, steering_angle):
    drive_msg_stamped = AckermannDriveStamped()
    drive_msg = AckermannDrive()
    drive_msg.speed = speed
    drive_msg.steering_angle = steering_angle
    drive_msg.acceleration = 0
    drive_msg.jerk = 0
    drive_msg.steering_angle_velocity = 0
    drive_msg_stamped.drive = drive_msg
    vesc.publish(drive_msg_stamped)
    #rp.sleep(1.0 / 20)


def stop():
    drive_msg_stamped = AckermannDriveStamped()
    drive_msg = AckermannDrive()
    drive_msg.speed = 0
    drive_msg.steering_angle = 0
    drive_msg.acceleration = 0
    drive_msg.jerk = 0
    drive_msg.steering_angle_velocity = 0
    drive_msg_stamped.drive = drive_msg
    vesc.publish(drive_msg_stamped)


if __name__ == '__main__':
    rp.init_node("controller", anonymous=True)
    rp.spin()
    cv2.destroyAllWindows()
