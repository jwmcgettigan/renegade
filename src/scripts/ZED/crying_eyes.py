#!/usr/bin/env python
import rospy as rp
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError


def talker():

    left_eye = rp.Publisher("left_eye", Image, queue_size=10)
    right_eye = rp.Publisher("right_eye", Image, queue_size=10)
    rp.init_node('image_converter', anonymous=True)
    rate = rp.Rate(60)
    bridge = CvBridge()
    cap = cv2.VideoCapture(1)
    while not rp.is_shutdown():
        ret, img = cap.read()

        left_img = img[0:367, 0:672]
        right_img = img[0:367, 672:1344]

        left_eye.publish(bridge.cv2_to_imgmsg(left_img, encoding="passthrough"))
        right_eye.publish(bridge.cv2_to_imgmsg(right_img, encoding="passthrough"))
        rate.sleep()


if __name__ == '__main__':
    try:
        talker()
    except rp.ROSInterruptException:
        pass
