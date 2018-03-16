#!/usr/bin/python
import rospy as rp
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

class Publish:
    bridge = CvBridge()

    def __init__(self):
        rp.init_node('zed', anonymous=True)
        zed = rp.Publisher("zed/image", Image, queue_size=1)
        rate = rp.Rate(30)
        self.stream()


    def stream(self):
        cap = cv2.VideoCapture(1)
        while not rp.is_shutdown():
            ret, img = cap.read()

            #imgCrop = img[188:376, 0:1344]
            imgCrop = img[120:376, 0:1344]

            zed.publish(self.bridge.cv2_to_imgmsg(imgCrop, encoding="passthrough"))
            rate.sleep()


if __name__ == '__main__':
    try:
        stream = Publish()
    except rp.ROSInterruptException:
        pass
#=================================================================
#/////////////////////////////////////////////////////////////////
#=================================================================
