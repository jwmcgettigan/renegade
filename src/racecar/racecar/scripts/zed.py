#!/usr/bin/python
# ----------------
# zed data can be retrieved from this file
# publish and subscribe to zed

import cv2, rospy as rp, numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

DISPLAY=False

class Zed:
    bridge = CvBridge()

    def __init__(self):
        pass


    def setImage(self, data):
        self.image = self.bridge.imgmsg_to_cv2(data, desired_encoding="passthrough")


    def getImage(self):
        return self.image


class Publisher:
    bridge = CvBridge()

    def __init__(self):
        rp.init_node('zed', anonymous=True)
        self.zedNormal = rp.Publisher("zed/normal", Image, queue_size=1)
        #self.zedStream = rp.Publisher("zed/stream", Image, queue_size=1)
        self.rate = rp.Rate(30)
        self.publish()


    def publish(self):
        cap = cv2.VideoCapture(1)
        while not rp.is_shutdown():
            ret, img = cap.read()
            self.normal(img)
            #self.stream(img)
            self.rate.sleep()


    # I should try to derive the height and width using variables.
    def normal(self, img):
        height, width = img.shape[:2]
        #top, bottom, left, right = 120, height, 0, width

        top, bottom = 120, height
        left, right = 0, width
        """
        top, bottom = 120, img.shape[:2][0]
        left, right = 0, img.shape[:2][1]

        top = 120
        bottom = height
        left = 0
        right = width"""
        #imgCrop = img[top:bottom, left:right]
        imgCrop = img[120:376,0:1344]
        self.zedNormal.publish(self.bridge.cv2_to_imgmsg(imgCrop, encoding="passthrough"))


    def stream(self, img):
        self.zedStream.publish(self.bridge.cv2_to_imgmsg(img, encoding="bgr8"))


if __name__ == '__main__':
    try:
        publisher = Publisher()
    except rp.ROSInterruptException:
        print "You messed up!"
