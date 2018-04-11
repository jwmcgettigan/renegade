#!/usr/bin/python
import rospy as rp
from sensor_msgs.msg import LaserScan
from sensor_msgs.msg import Image
import matplotlib.pyplot as plt
import math
import numpy as np

DEBUG = False
VERBOSE = False
DISPLAY = False
objDebug = False
#RATE = 1 #1 = 40 Hz, 2 = 20 Hz, 4 == 10 Hz, 8 = 5 Hz, 20 == 2 Hz, 40 == 1 Hz, 80 == 0.5 Hz



class Probe:
    counter = 0

    def __init__(self, data, theta):
        self.data = data
        self.theta = theta
        pass

    def closestObjectsAngleFullRanges(self): #distance from closest object, angle of closest object
        tempRanges = []
        for x in range(0,21):
            tempRanges.append(65)
        for x in range(21,1080):
            tempRanges.append(self.data.ranges[x])
        #print tempRanges
        return min(tempRanges), tempRanges.index(min(tempRanges))

















    if __name__ == '__main__':
        rp.init_node("lidarListener", anonymous=True)
        try: rp.spin()
        except KeyboardInterrupt: print "Shutting down ROS LiDAR feature dector module."