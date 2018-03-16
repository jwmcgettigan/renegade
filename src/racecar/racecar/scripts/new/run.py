#!/usr/bin/python
import process, auto, zed
import cv2
import rospy as rp
from sensor_msgs.msg import Image, Joy
from cv_bridge import CvBridge, CvBridgeError
from ackermann_msgs.msg import AckermannDriveStamped, AckermannDrive

VERBOSE=False
DEBUG=True
DISPLAY=False
RECORD=False

class Renegade:
    bridge = CvBridge()

    def __init__(self):
        # zed.Publish()
        rp.Subscriber("vesc/joy", Joy, self.joy_callback)
        rp.Subscriber("zed/image", Image, self.zed_image_callback)


    def joy_callback(self, ros_data): # ros_data = joy_msg = Joy()
        self.pilot_mode = ros_data.buttons[5]


    def zed_image_callback(self, ros_data): # ros_data = img_msg = Image()
        image = self.bridge.imgmsg_to_cv2(ros_data, desired_encoding="passthrough")

        left = process.Frame(image[0:256, 0:672], 'left')
        right = process.Frame(image[0:256, 672:1344], 'right')

        linesExist = left.getLinesExist or right.getLinesExist
        firstLinesSeen = left.getFirstLinesSeen() and right.getFirstLinesSeen()
        auto.Pilot(left.getSlope(), right.getSlope(), linesExist, firstLinesSeen)


if __name__ == '__main__':
    rp.init_node("renegade", anonymous=True)
    car = Renegade()
    try:
        rp.spin()
    except KeyboardInterrupt:
        print "Shutting down ROS Image feature detector module."
    cv2.destroyAllWindows()


#=================================================================
#/////////////////////////////////////////////////////////////////
#=================================================================
