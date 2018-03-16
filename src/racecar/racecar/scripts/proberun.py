#!/usr/bin/python

import probe2, probeauto
import rospy as rp
from sensor_msgs.msg import LaserScan, Joy, Image
from ackermann_msgs.msg import AckermannDriveStamped, AckermannDrive
import matplotlib.pyplot as plt

class Renegade:
    global theta
    theta = []

    def __init__(self):
        rp.Subscriber("vesc/joy", Joy, self.joy_callback)
        rp.Subscriber("zed_image", Image, self.probe_callback)
        print("proberun constructor")

    def joy_callback(self, ros_data): # ros_data = joy_msg = Joy()
        self.pilot_Mode = ros_data.buttons[5]

    def probe_callback(self, data):
        theprobe = probe2.Probe(data, theta)
        #print(theprobe.averageAllRanges())
        #print(theprobe.averageRanges(-120,-110))
        print(theprobe.offsetBetweenWalls(90,5))
        probeauto.Pilot(self, pilotMode)
        probeauto.Pilot.controller(2,3,True, True)
        probeauto.Pilot.controller(theprobe.offsetBetweenWalls(90,5),1,True)

    #rp.init_node("controller", anonymous=True)
        pass

    def runThis(self):
        rp.Subscriber("scan", LaserScan, self.probe_callback)

    
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
        rp.Subscriber("scan", LaserScan, self.probe_callback)
        rp.init_node("renegade", anonymous=True)
        probeauto.Pilot(ros_data.buttons[5])
        car = Renegade()
        

        try:
            rp.spin()
        except KeyboardInterrupt:
            print "Shutting down ROS Image feature detector module."