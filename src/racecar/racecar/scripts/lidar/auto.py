#!/usr/bin/python
import cv2
import rospy as rp
from sensor_msgs.msg import Image, Joy
from cv_bridge import CvBridge, CvBridgeError
from ackermann_msgs.msg import AckermannDriveStamped, AckermannDrive

VERBOSE=True
DEBUG=True
DISPLAY=False
RECORD=False

class Pilot:

    def __init__(self, data, pilotMode):
        #rp.init_node("autopilot", anonymous=True)
        vesc = rp.Publisher("/vesc/high_level/ackermann_cmd_mux/input/nav_0", AckermannDriveStamped, queue_size=1)
        controller = Controller(data, pilotMode, vesc)
    #Logic(controller, self)


class Controller:
    zedData = []
    lidarData = []
    errorList = [0]
    historySize = 10
   
    def __init__(self, data, pilotMode, vesc):
        drive_msg_stamped = AckermannDriveStamped()
        drive_msg = AckermannDrive() #self.drive_msg = AckermannDrive()

        if data[1]!='zed' and data[1]!='lidar':
            #self.both(data[0], data[1])
            logicData = [self.zedData, self.lidarData]
        elif data[1]=='zed':
            self.zed(data[0][0], data[0][1], data[0][2], data[0][3])
            logicData = [self.zedData, 'zed']
        elif data[1]=='lidar':
            #self.lidar(data[0][0], data[0][1], data[0][2], data[0][3], data[0][4], data[0][5])
            self.lidar(data[0][0], data[0][1], data[0][2], data[0][3], data[0][4], data[0][5], data[0][6], data[0][7])
            logicData = [self.lidarData, 'lidar']

        Logic(logicData, drive_msg, pilotMode)
        drive_msg_stamped.drive = drive_msg
        vesc.publish(drive_msg_stamped)


    def zed(self, leftSlope, rightSlope, linesExist, firstLinesSeen):
        direction = ""
        error = leftSlope + rightSlope # sum of slopes
        steeringAngle = self.pid(error, (0.3/2.5), 0, 0)
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
        self.zedData = [speed, steeringAngle, linesExist]


        #TODO: Average all angles from 45-90, replaces wall and forward offset
    #def lidar(self, slope, wallOffset, forwardOffset, forwardDistance, stopCondition, stopList):
    def lidar(self, slope, wallOffset, forwardOffset, forwardDistance, stopCondition, stopList, overRideSpeed, overRideTurn):
        direction = ""

        #Slalom: Great for keeping center, but if goes off center, becomes drunk.
        #180: Turns late but tight
        wallOffsetWeight = 2
        #Slalom: Turns early and sharp
        #180: Turns sharp early. Half way through turn, goes nearly straight
        forwardOffsetWeight = 3
        #Slalom: Turns slower in slalom but smoothish.
        #180: Very wide
        slopeWeight = 4

        maxTurningAngle = 0.3
        slopeLimit = 30
        inchToMeter = 0.0254

        slope *= (maxTurningAngle/slopeLimit)
        wallOffset *= (maxTurningAngle/(12*inchToMeter))
        forwardOffset *= (maxTurningAngle/(12*inchToMeter))
        error = ((slopeWeight*slope) + (wallOffsetWeight*wallOffset) + (forwardOffsetWeight*forwardOffset))/(wallOffsetWeight+forwardOffsetWeight+slopeWeight)
        #error = ((slopeWeight*slope) + (offsetWeight*offset))/(2*(offsetWeight+slopeWeight))
        #steeringAngle = error;
        
        speedLimit = 1.7
        speedPower = 0.4
        speed = speedLimit - (1/forwardDistance)**speedPower

        steeringAngle = self.pid(error, 1, 0, 0)
        if steeringAngle > 0.3: steeringAngle = 0.3
        if steeringAngle < -0.3: steeringAngle = -0.3
        if steeringAngle > 0.05: direction = "Left"
        elif steeringAngle < -0.05: direction = "Right"
        else: direction = "Center"

        # if DEBUG:
        #     print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
        #     print "Direction:\t "       +                                                 direction
        #     print "Steering Angle:\t"   + (' ' if steeringAngle > 0 else '')   + "%.4f" % steeringAngle
        #     print "Speed:\t\t"          + (' ' if speed > 0 else '')           + "%.4f" % speed
        #     print "\nError:\t\t"        + (' ' if error > 0 else '')           + "%.4f" % error
        #     print "Wall Offset\t"       + (' ' if wallOffset > 0 else '')      + "%.4f" % wallOffset
        #     print "Forward Offset:\t"   + (' ' if forwardOffset > 0 else '')   + "%.4f" % forwardOffset
        #     print "Slope:\t\t"          + (' ' if slope > 0 else '')           + "%.4f" % slope
        #     print "Forward Distance:\t:"+ (' ' if forwardDistance > 0 else '') + "%.4f" % forwardDistance
        
        #if stopCondition: speed = 0
        #if forwardDistance < 0.35:
        #    speed = -5
        #    steeringAngle = 0

        reverseCondition = forwardDistance < 0.35
        
        ##So car doesn't drive off table!!!!!!!#!#!#!#!
        speed = 0
        steeringAngle = 0
        stopCondition = 0
        reverseCondition = 0


        speed = overRideSpeed
        steeringAngle = overRideTurn

        self.lidarData = [speed, steeringAngle, stopCondition, reverseCondition, stopList]
    

    def pid(self, error, Kp, Ki, Kd):
        length = len(self.errorList)

        # if list is larger than the desired history size -1, remove item at index 0
        if (length > self.historySize-1):
            self.errorList.pop(0)

        self.errorList.append(error) # adds new error to last position in array

        P = I = D = 0
        for x in self.errorList:
            I += x

        P = self.errorList[length-1]
        I = (I/length) # averages values
        D = 1 # Placeholder for now.
        return (Kp * P) + (Ki * I) + (Kd * D)
    

class Logic:


    def __init__(self, data, drive_msg, pilotMode):
        self.drive_msg = drive_msg
        drive_msg = [0,0,0,0,0] # [steering_angle, steering_angle_velocity, speed, acceleration, jerk]
        if pilotMode:
            if data[1]!='zed' and data[1]!='lidar':
                self.zed(data[0][0], data[0][1], data[0][2])
                self.lidar(data[1][0], data[1][1], data[1][2], data[1][3])
            elif data[0]=='zed':
                self.zed(data[0][0], data[0][1], data[0][2])
            elif data[1]=='lidar':
                self.lidar(data[0][0], data[0][1], data[0][2], data[0][3], data[0][4])
        else:
            self.stop()


    def zed(self, speed, steeringAngle, linesExist):
        if linesExist:
            self.apply_control(speed, steeringAngle)
        else:
            self.apply_control(1, 0)


    def lidar(self, speed, steeringAngle, stopCondition, reverseCondition, stopList):
        """
        STOP = False
        REVERSE = not STOP

        if STOP and stopCondition:
            speed = 0
        if REVERSE and reverseCondition:
            speed = -2
            steeringAngle = 0
        """
        if reverseCondition:
            speed = -2
            steeringAngle = 0
            stopList.append(1)
        
        if len(stopList) > 60:
            steeringAngle = 0
            speed = 0
        
        self.apply_control(speed, steeringAngle)


    def apply_control(self, speed, steeringAngle):
        self.drive_msg.speed = speed
        self.drive_msg.steering_angle = steeringAngle


    def stop(self):
        self.drive_msg.speed = 0

#=================================================================
#/////////////////////////////////////////////////////////////////
#=================================================================
