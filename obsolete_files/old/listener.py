#!/usr/bin/env python
import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import rospy as rp

class image_converter:
	def callback (self, data):
		try:
			cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
		except CvBridgeError as e:
			print(e)

def callback(data):
	rp.loginfo(rp.get_caller_id()+ " I heard %s", data.data)
def listener():
	rp.init_node('polylistener', anonymous = True)
	rp.Subscriber('polycrier', String, callback)
	rp.spin()
if __name__ == "__main__":
	try:	
		listener()
	except rp.ROSInterruptException:
		pass
