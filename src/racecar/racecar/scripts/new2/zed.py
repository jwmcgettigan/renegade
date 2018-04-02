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
        #self.zedNorm = rp.Publisher("zed/normal", Image, queue_size=1)
        self.zedCrop = rp.Publisher("zed/cropped", Image, queue_size=1)
        #self.zedStream = rp.Publisher("zed/stream", Image, queue_size=1)
        self.rate = rp.Rate(30)
        self.publish()
        pass


    def publish(self):
        cap = cv2.VideoCapture(1)
        while not rp.is_shutdown():
            ret, img = cap.read()
            #self.publishNormal(img)
            self.publishCropped(img)
            #self.publishStream(img)
            self.rate.sleep()


    # I should try to derive the height and width using variables.
    def publishNormal(self, img):
        imgCrop = img[0:376, 0:1344]
        self.zedNorm.publish(self.bridge.cv2_to_imgmsg(imgCrop, encoding="passthrough"))


    def publishCropped(self, img):
        imgCrop = img[120:376, 0:1344]
        self.zedCrop.publish(self.bridge.cv2_to_imgmsg(imgCrop, encoding="passthrough"))


    def publishStream(self, img):
        imgCrop = img[0:376, 0:1344]
        self.zedStream.publish(self.bridge.cv2_to_imgmsg(imgCrop, encoding="bgr8"))


if __name__ == '__main__':
    try:
        publisher = Publisher()
    except rp.ROSInterruptException:
        pass
