#!/usr/bin/python

import probe2
import rospy as rp
from sensor_msgs.msg import LaserScan
from sensor_msgs.msg import Image
import matplotlib.pyplot as plt


class Probe3:
    global theta
    theta = []
    def probe_callback(data):
        theprobe = probe2.Probe(data, theta)
        #print(theprobe.averageAllRanges())
        #print(theprobe.averageRanges(-120,-110))
        theprobe.offsetBetweenWalls(90,5)
    #rp.init_node("controller", anonymous=True)
        pass
    
   
    def createAnglesUsedToPlotGraph(): #Used in the polar graph as the angles
	    REDUCED = False
	    REDUCINGFACTOR = 10
	    theta = []
	    if REDUCED:
	        for x in xrange(0,1081,REDUCINGFACTOR):
	            theta.append(x*0.00436332309619)
	    else:
	        for x in range(0,1081):
	            theta.append(x*0.00436332309619) #data.angle_increment == PI/(4*180) == 0.00436332309619


    if __name__ == '__main__':
        createAnglesUsedToPlotGraph()
        rp.Subscriber("scan", LaserScan, probe_callback)
        rp.init_node("probe")

        try:
            rp.spin()
        except KeyboardInterrupt:
            print "Shutting down ROS Image feature detector module."