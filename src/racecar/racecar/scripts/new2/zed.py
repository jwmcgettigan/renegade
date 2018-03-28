#!/usr/bin/python
# ----------------
# zed data can be retrieved from this file
# publish and subscribe to zed

import cv2, rospy as rp
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

DISPLAY=False

class Zed:
    bridge = CvBridge()
    cap = cv2.VideoCapture(1)

    def __init__(self):
        #rp.init_node('car/zed', anonymous=True)
        self.zed = rp.Publisher("zed/image", Image, queue_size=1)
        rp.Subscriber("zed/image", Image, self.callback)


    # I should to derive the height and width using variables.
    def publish(self):
        ret, img = self.cap.read()
        imgCrop = img[120:376, 0:1344]
        self.zed.publish(self.bridge.cv2_to_imgmsg(imgCrop, encoding="passthrough"))


    def callback(self, data):
        self.publish()
        self.image = self.bridge.imgmsg_to_cv2(data, desired_encoding="passthrough")


    def getImage(self):
        return self.image
