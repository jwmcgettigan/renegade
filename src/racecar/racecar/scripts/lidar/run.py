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
    stopList = []

    def __init__(self):
        #zed.Publish()
        rp.Subscriber("vesc/joy", Joy, self.joy_callback)
        if ZED:
            rp.Subscriber("zed/image", Image, self.zed_image_callback)
        if LIDAR:
            self.createAnglesUsedToPlotGraph()
            rp.Subscriber("scan", LaserScan, self.probe_callback)   


    def joy_callback(self, ros_data): # ros_data = joy_msg = Joy()
        self.pilotMode = ros_data.buttons[5]
        if ZED and LIDAR:
            data = [self.zedData, self.lidarData]
        elif ZED:
            data = [self.zedData, 'zed']
        elif LIDAR:
            data = [self.lidarData, 'lidar'] #Error here is a race condition
        auto.Pilot(data, self.pilotMode)


    def zed_image_callback(self, ros_data): # ros_data = img_msg = Image()
        image = self.bridge.imgmsg_to_cv2(ros_data, desired_encoding="passthrough")

        left = process.Frame(image[0:256, 0:672], 'left')
        right = process.Frame(image[0:256, 672:1344], 'right')

        linesExist = left.getLinesExist or right.getLinesExist
        firstLinesSeen = left.getFirstLinesSeen() and right.getFirstLinesSeen()
        self.zedData = [left.getSlope(), right.getSlope(), linesExist, firstLinesSeen]


    def probe_callback(self, data):
        theprobe = probe.Probe(data, self.theta)
        wallOffset = theprobe.offsetBetweenWalls(90,5)
        forwardOffset = theprobe.offsetBetweenWalls(45,5)
        slope = -theprobe.theWalls(70,90,110,3)
        forwardDistance = theprobe.averageRanges(-20,20)
        stopCondition = (theprobe.averageRanges(-10,10) < .25)
        # leftRearObject = theprobe.objectDetection(-90,-125,1,0.9,"Left") #front angle, rear angle, max distance, distance required to detect object#rightRearObject = theprobe.objectDetection(90,125,2,1.8) #front angle, rear angle, max distance, distance required to detect object#rightRearObject = theprobe.objectDetection(90,125,2,1.8) #front angle, rear angle, max distance, distance required to detect object
        # rightRearObject = theprobe.objectDetection(90,125,1,0.9,"Right") #front angle, rear angle, max distance, distance required to detect object#rightRearObject = theprobe.objectDetection(90,125,2,1.8) #front angle, rear angle, max distance, distance required to detect object#rightRearObject = theprobe.objectDetection(90,125,2,1.8) #front angle, rear angle, max distance, distance required to detect object
        

        #leftRearObject = theprobe.objectDetection3(25,110,135,1,0.5,"Right")
        rightSideObj = theprobe.objectDetection3(25,90,130,1.5,0.5,"Right")
        leftSideObj = theprobe.objectDetection3(-25,-90,-130,1.5,0.5,"Left")

        #theprobe.edgeDetection(45,120,5)
        
        # print "distance: %f\tangle: %f\n" % theprobe.closestObjectsAngle()
        # print "distance: %f\tangle: %f\n" % theprobe.closestObjectsAngleFullRanges()



        # print "\n\n\n\n\nAngle\tH-Dist\t\tA-Dist" #Hypotenuse Distance/Distance to wall from Lidar #Adjacent Distance/X Component of distance to wall
        # theprobe.perpendicularLineDistance(-120)
        # theprobe.perpendicularLineDistance(-105)
        # theprobe.perpendicularLineDistance(-90)
        # theprobe.perpendicularLineDistance(-75)
        # theprobe.perpendicularLineDistance(-60)
        # theprobe.perpendicularLineDistance(-45)
        # theprobe.perpendicularLineDistance(-30)
        # theprobe.perpendicularLineDistance(-15)
        # theprobe.perpendicularLineDistance(0)
        # theprobe.perpendicularLineDistance(15)
        # theprobe.perpendicularLineDistance(30)
        # theprobe.perpendicularLineDistance(45)
        # theprobe.perpendicularLineDistance(60)
        # theprobe.perpendicularLineDistance(75)
        # theprobe.perpendicularLineDistance(90)
        # theprobe.perpendicularLineDistance(105)
        # theprobe.perpendicularLineDistance(120)
        


        # rightRearObject = theprobe.objectDetection(-30,30,1,0.9,"Center")
        # leftRearObject = theprobe.objectDetection(-30,30,1,0.9,"Center")
        # theprobe.objectDetection2(45,90,135, 2, 1.5, "test") #frontAngle, midAngle, rearAngle, tempMaxDistance, objectDetectionCutoffDistance, debugDirectionString

        
        overRideSpeed = 0.6
        overRideTurn = rightSideObj
        if leftSideObj != 0: overRideTurn = -leftSideObj

        #slope = -theprobe.theWalls(45,80,100,3)
        #theprobe.averageWallSlope(-45,-135)
        if not self.pilotMode:
            self.stopList = []
        self.lidarData = [slope, wallOffset, forwardOffset, forwardDistance, stopCondition, self.stopList, overRideSpeed, overRideTurn]
        # self.lidarData = [slope, wallOffset, forwardOffset, forwardDistance, stopCondition, self.stopList]


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
