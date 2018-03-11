#!/usr/bin/env python
import rospy as rp
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError


bridge = CvBridge()
#newVideo = cv2.VideoWriter('eyes_capture.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 29,(int(1344), int(376)))

def callback(data):
    img = bridge.imgmsg_to_cv2(data, desired_encoding="passthrough")
    cv2.imshow("eyes", img)
    #newVideo.write(img)
    if cv2.waitKey(20) & 0xFF == ord('q'):
        pass


def listener():
    rp.init_node('listener', anonymous=True)
    rp.Subscriber("eyes", Image, callback)
    rp.spin()



if __name__ == '__main__':
    listener()
    cv2.destroyAllWindows()
 #   newVideo.release()
