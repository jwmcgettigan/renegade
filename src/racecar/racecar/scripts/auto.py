#!/usr/bin/python
import cv2
import rospy as rp
from sensor_msgs.msg import Image, Joy
from cv_bridge import CvBridge, CvBridgeError
from ackermann_msgs.msg import AckermannDriveStamped, AckermannDrive

VERBOSE=False
DEBUG=True
DISPLAY=False
RECORD=False

class Pilot:
    errorList = [0]
    HISTORYSIZE = 10

    def __init__(self, pilotMode):
        self.pilotMode = pilotMode
        rp.init_node("autopilot", anonymous=True)
        self.vesc = rp.Publisher("/vesc/high_level/ackermann_cmd_mux/input/nav_0", AckermannDriveStamped, queue_size=1)



    def controller(self, leftSlope, rightSlope, linesExist, firstLinesSeen):
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
        drive_msg_stamped = AckermannDriveStamped()
        drive_msg = AckermannDrive()

        self.logic(drive_msg, speed, steeringAngle, linesExist)
        drive_msg_stamped.drive = drive_msg
        self.vesc.publish(drive_msg_stamped)


    def logic(self, drive_msg, speed, steeringAngle, linesExist):
        if self.kill_switch:
            if lines_exist:
                self.apply_control(drive_msg, speed, steeringAngle)
            else:
                self.apply_control(drive_msg, 1, 0)
        else:
            self.stop(drive_msg)


    def apply_control(self, msg, speed, steeringAngle):
        msg.speed = speed
        msg.steering_angle = steeringAngle
        msg.acceleration = 0
        msg.jerk = 0
        msg.steering_angle_velocity = 0


    def stop(self, msg):
        msg.speed = 0
        msg.steering_angle = 0
        msg.acceleration = 0
        msg.jerk = 0
        msg.steering_angle_velocity = 0

    def pid_controller(self, error):
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


#=================================================================
#/////////////////////////////////////////////////////////////////
#=================================================================
