#!/usr/bin/python

import probe
import rospy as rp
from sensor_msgs.msg import LaserScan, Joy, Image
from ackermann_msgs.msg import AckermannDriveStamped, AckermannDrive
import matplotlib.pyplot as plt

global theta
theta = []
global theprobe

DEBUG = False
VERBOSE = True
WALLANGLE = 90 #90 degrees is parallel to car

def probe_callback(data):
    global theprobe
    theprobe = probe.Probe(data, theta)
    turningAngle(data)
    pass

def turningAngle(data):
    offset = theprobe.offsetBetweenWalls(WALLANGLE,5)
    slope = theprobe.theWalls()
    if True: print("Wall offset:\t" + str(offset))
    if True: print("Wall slope:\t" + str(slope))


    return slope
    #theprobe.theWalls()
    
def offsetBetweenWalls(data):
    if VERBOSE: print("\n\n\n\n\n")
    
    FOV = 5 #amount of angle of which to see
    leftWallDistance = theprobe.distanceToWall(-WALLANGLE,FOV)
    rightWallDistance = theprobe.distanceToWall(WALLANGLE,FOV)
    offsetBetweenWalls = theprobe.offsetBetweenWalls(WALLANGLE,FOV)

    if VERBOSE:
        print("Left Wall: " + str(leftWallDistance))
        print("Right Wall: " + str(rightWallDistance))
        print("\nWall offset" + str(offsetBetweenWalls)+"\n")
    return offsetBetweenWalls

# def getWallSlope():
#     theprobe.theWalls()

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