#!/usr/bin/python
import process, auto, probe#, zed
import cv2
import rospy as rp
from sensor_msgs.msg import Image, LaserScan, Joy
from cv_bridge import CvBridge, CvBridgeError
from ackermann_msgs.msg import AckermannDriveStamped, AckermannDrive

VERBOSE=False
DEBUG=False
DISPLAY=False
RECORD=False
ZED=False
LIDAR=True

class Renegade:
    bridge = CvBridge()
    theta = []
    wallAngle = 55 #90 degrees is parallel to car

    def __init__(self):
        #zed.Publish()
        rp.Subscriber("vesc/joy", Joy, self.joy_callback)
        if ZED:
            rp.Subscriber("zed/image", Image, self.zed_image_callback)
        if LIDAR:
	    self.createAnglesUsedToPlotGraph()
            rp.Subscriber("scan", LaserScan, self.probe_callback)	


    def joy_callback(self, ros_data): # ros_data = joy_msg = Joy()
        pilotMode = ros_data.buttons[5]
        if ZED and LIDAR:
            data = [self.zedData, self.lidarData]
        elif ZED:
            data = [self.zedData, 'zed']
        elif LIDAR:
            data = [self.lidarData, 'lidar']
        auto.Pilot(data, pilotMode)
 

    def zed_image_callback(self, ros_data): # ros_data = img_msg = Image()
        image = self.bridge.imgmsg_to_cv2(ros_data, desired_encoding="passthrough")

        left = process.Frame(image[0:256, 0:672], 'left')
        right = process.Frame(image[0:256, 672:1344], 'right')

        linesExist = left.getLinesExist or right.getLinesExist
        firstLinesSeen = left.getFirstLinesSeen() and right.getFirstLinesSeen()
        self.zedData = [left.getSlope(), right.getSlope(), linesExist, firstLinesSeen]


    def probe_callback(self, data):
        theprobe = probe.Probe(data, self.theta)
	offset = theprobe.offsetBetweenWalls(self.wallAngle,5)
	slope = -theprobe.theWalls()
	self.lidarData = [slope, offset]


    def offsetBetweenWalls(self, data):
    	if VERBOSE: print("\n\n\n\n\n")

    	FOV = 5 #amount of angle of which to see
    	leftWallDistance = theprobe.distanceToWall(-self.wallAngle,FOV)
    	rightWallDistance = theprobe.distanceToWall(self.wallAngle,FOV)
    	offsetBetweenWalls = theprobe.offsetBetweenWalls(self.wallAngle,FOV)

    	if VERBOSE:
        	print("Left Wall: " + str(leftWallDistance))
        	print("Right Wall: " + str(rightWallDistance))
        	print("\nWall offset" + str(offsetBetweenWalls)+"\n")
    	return offsetBetweenWalls


    def createAnglesUsedToPlotGraph(self): #Used in the polar graph as the angles
        REDUCED = False
        REDUCINGFACTOR = 10
        if REDUCED:
            for x in xrange(0,1081,REDUCINGFACTOR):
                self.theta.append(x*0.00436332309619)
        else:
            for x in range(0,1081):
                self.theta.append(x*0.00436332309619) #data.angle_increment == PI/(4*180) == 0.00436332309619


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
