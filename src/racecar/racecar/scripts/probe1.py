#!/usr/bin/python

import probe
import rospy as rp
from sensor_msgs.msg import LaserScan, Joy, Image
from ackermann_msgs.msg import AckermannDriveStamped, AckermannDrive
import matplotlib.pyplot as plt

class Renegade:
    global theta
    theta = []

    def probe_callback(data):
        theprobe = probe.Probe(data, theta)
        #print(theprobe.averageAllRanges())
        #print(theprobe.averageRanges(-120,-110))
        print("\n\nWall offset" + str(theprobe.offsetBetweenWalls(90,5))+"\n\n")
        #print(theprobe.angleOfWall(-45,-90,2))
        theprobe.theWalls()
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
        print("This is here")
        rp.Subscriber("scan", LaserScan, probe_callback)
        rp.init_node("renegade", anonymous=True)
        

        try:
            rp.spin()
        except KeyboardInterrupt:
            print "Shutting down ROS Image feature detector module."