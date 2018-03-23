#!/usr/bin/python
import rospy as rp
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError


def talker():
    eyes = rp.Publisher("eyes", Image, queue_size=10)
    rp.init_node('crying_eyes', anonymous=True)
    rate = rp.Rate(30)
    bridge = CvBridge()
    cap = cv2.VideoCapture(1)
    while not rp.is_shutdown():
        ret, img = cap.read()
	 
        #imgCrop = img[188:376, 0:1344]
        imgCrop = img[120:376, 0:1344]

    	eyes.publish(bridge.cv2_to_imgmsg(imgCrop, encoding="passthrough"))
    	rate.sleep()


if __name__ == '__main__':
    try:
        talker()
    except rp.ROSInterruptException:
        pass
