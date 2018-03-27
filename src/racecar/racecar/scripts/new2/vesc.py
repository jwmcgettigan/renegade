#!/usr/bin/python
# ----------------
# vesc data will be retrieved by this file
# publish to vesc

import rospy as rp
from ackermann_msgs.msg import AckermannDriveStamped, AckermannDrive

class Vesc:
    driveMsgStamped = AckermannDriveStamped()
    driveMsg = AckermannDrive()

    def __init__(self):
        #rp.init_node('car/vesc', anonymous=True)
        self.vesc = rp.Publisher("/vesc/high_level/ackermann_cmd_mux/input/nav_0", AckermannDriveStamped, queue_size=1)


    def publish(self):
        self.driveMsgStamped.drive = self.driveMsg
        self.vesc.publish(driveMsgStamped)


    def getDriveMsg(self):
        return self.driveMsg


    def setDriveMsg(self, driveMsg):
        self.driveMsg = driveMsg
