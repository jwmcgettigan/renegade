#!/usr/bin/python
import cv2
import rospy as rp
from sensor_msgs.msg import Image, Joy
from cv_bridge import CvBridge, CvBridgeError
from ackermann_msgs.msg import AckermannDriveStamped, AckermannDrive

VERBOSE=False
DEBUG=False
DISPLAY=False
RECORD=False

class Pilot:

    def __init__(self, data, pilotMode):
        #rp.init_node("autopilot", anonymous=True)
        vesc = rp.Publisher("/vesc/high_level/ackermann_cmd_mux/input/nav_0", AckermannDriveStamped, queue_size=1)
        controller = Controller(data, pilotMode, vesc)
	#Logic(controller, self)


class Controller:
    zedLogic = []
    lidarLogic = []
    logic = []
   
    def __init__(self, data, pilotMode, vesc):
	drive_msg_stamped = AckermannDriveStamped()
        self.drive_msg = AckermannDrive()

        if data[1]!='zed' and data[1]!='lidar':
            zedData = data[0]
            lidarData = data[1]
	    #self.both(zedDat, lidarData)
            self.logic = [self.zedLogic, self.lidarLogic]
        elif data[1]=='zed':
            zedData = data[0]
	    self.zed(zedData)
	    self.logic = [self.zedLogic, 'zed']
        elif data[1]=='lidar':
            lidarData = data[0]
	    self.lidar(lidarData)
	    self.logic = [self.lidarLogic, 'lidar'] 

	Logic(self.logic, self.drive_msg, pilotMode)
	drive_msg_stamped.drive = self.drive_msg
        vesc.publish(drive_msg_stamped)


    def zed(self, data):
	leftSlope = data[0]
        rightSlope = data[1]
	linesExist = data[2]
        firstLinesSeen = data[3]
	direction = ""
        error = leftSlope + rightSlope # sum of slopes
        # steeringAngle = (0.3/2.5)*error
        steeringAngle = self.pid_controller(error)
        if steeringAngle > 0.3: steeringAngle = 0.3
        if steeringAngle < -0.3: steeringAngle = -0.3
        if steeringAngle > 0.02: direction = "Left"
        elif steeringAngle < -0.02: direction = "Right"
        else: direction = "Center"
        if DEBUG and firstLinesSeen:
            print "====================================="
            # print "|Left    |Right   |Sum     |Control |Direction|"
            # print "|%f|%f|%f|%f|%s     |" % (leftSlope, rightSlope, error, steeringAngle, direction)
            # print "(Left|Right): (%f|%f)" % (leftSlope, rightSlope)
            # print "Sum: %f" % (error)
            # print "(Control|Direction): (%f|%s)" % (steeringAngle, direction)
        speedLimit = 0.6
        speedPower = 1.13678
        speed = speedLimit * (1 - abs(steeringAngle))**speedPower
        # speed = 0.4
        self.zedLogic = [speed, steeringAngle, linesExist]


    def lidar(self, data):
	error = data[0]
	wallsExist = True
	direction = ""
	steeringAngle = error;
        if DEBUG:
	    if (distanceBetweenWalls > 0.2):
                print(str(distanceBetweenWalls) + "\tRight wall is closer")
            elif (distanceBetweenWalls < -0.2):
                print(str(distanceBetweenWalls) + "\tLeft wall is closer")
            else:
                print(str(distanceBetweenWalls) + "\tEvenly between walls")
	speed = 0.4
	self.lidarLogic = [speed, steeringAngle, wallsExist]
    

    def pid(self, error):
        length = len(self.errorList)

        # if list is larger than the desired history size -1, remove item at index 0
        if (length > self.HISTORYSIZE-1):
                self.errorList.pop(0)

        self.errorList.append(error) # adds new error to last position in array

        P = I = D = 0
        for x in self.errorList:
                I += x

        P = self.errorList[length-1]
        I = (I/length) # averages values
        D = 1 # Placeholder for now.

        Kp = (0.3/2.5) # 0.12
        Ki = 0 # ignored
        Kd = 0 # ignored
        return (Kp * P) + (Ki * I) + (Kd * D)
    

class Logic:


    def __init__(self, data, drive_msg, pilotMode):
        self.drive_msg = drive_msg
        drive_msg = [0,0,0,0,0]
	if pilotMode:
	    if data[1]!='zed' and data[1]!='lidar':
                zedData = data[0]
                lidarData = data[1]
		self.zed(zedData)
		self.lidar(lidarData)
            elif data[0]=='zed':
                zedData = data[0]
		self.zed(zedData)
            elif data[1]=='lidar':
                lidarData = data[0]
		self.lidar(lidarData)
        else:
	    self.stop()


    def zed(self, data):
        speed = data[0]
        steeringAngle = data[1]
        linesExist = data[2]
        if linesExist:
            self.apply_control(speed, steeringAngle)
        else:
            self.apply_control(1, 0)


    def lidar(self, data):
        speed = data[0]
        steeringAngle = data[1]
        wallsExist = data[2]
        if wallsExist:
            self.apply_control(speed, steeringAngle)
        else:
            self.apply_control(1, 0)


    def apply_control(self, speed, steeringAngle):
        # steering_angle, steering_angle_velocity, speed, acceleration, jerk
        self.drive_msg.speed = speed
        self.drive_msg.steering_angle = steeringAngle


    def stop(self):
        drive_msg = [0,0,0,0,0]

#=================================================================
#/////////////////////////////////////////////////////////////////
#=================================================================
