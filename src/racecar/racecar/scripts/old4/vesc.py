#!/usr/bin/python
# ----------------
# vesc data will be retrieved by this file
# publish to vesc

import rospy as rp
from ackermann_msgs.msg import AckermannDriveStamped, AckermannDrive

class Vesc:

    def __init__(self):
        #rp.init_node('car/vesc', anonymous=True)
        self.vesc = rp.Publisher("/vesc/high_level/ackermann_cmd_mux/input/nav_0", AckermannDriveStamped, queue_size=1)


    def publish(self):
        drive_msg_stamped = AckermannDriveStamped()
        drive_msg = AckermannDrive()

        # APPLY LOGIC

        drive_msg_stamped.drive = drive_msg
        self.vesc.publish(drive_msg_stamped)
