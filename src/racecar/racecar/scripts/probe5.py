#!/usr/bin/python
import probe2, probeauto, proberun
import rospy as rp
from sensor_msgs.msg import LaserScan, Joy, Image
from ackermann_msgs.msg import AckermannDriveStamped, AckermannDrive
import matplotlib.pyplot as plt

# class Probe5:
# 	if __name__ == '__main__':
# 		rp.initNode("HelpMeNow", anonoymous = True)

proberun.Renegade.runThis(proberun.Renegade())
rp.init_node("renegadre", anonymous=True)
rp.spin()