#!/usr/bin/python
import rospy as rp
from sensor_msgs.msg import LaserScan
from sensor_msgs.msg import Image
import matplotlib.pyplot as plt

rate = 8 #1 = 40 Hz, 2 = 20 Hz, 4 == 10 Hz, 8 = 5 Hz, 20 == 2 Hz, 40 == 1 Hz, 80 == 0.5 Hz
reducingFactor = 10
#plt.ion
#plt.polar()

plt.subplot(111,projection='polar')
plt.show()
#plt.figure().show()
#plt.figure().canvas.draw()
theta = []
q = 0

reduced = True
debug = False

if reduced:
    for x in xrange(0,1081,reducingFactor):
        theta.append(x*0.00436332309619) 
else:
    for x in range(0,1081):
        theta.append(x*0.00436332309619) #data.angle_increment == PI/(4*180) == 0.00436332309619



def callback(data):
#    plt.close()    
#    plt.figure().clear()
    global q
    q += 1

    if ((q%rate)==0):
        if debug print("Z") else pass
        ranges = []  
        if reduced:  
            for x in xrange(0,1081,reducingFactor):
                ranges.append(data.ranges[x] if data.ranges[x] < 10 else 10)
        else:
            for x in range(0,1081):
                ranges.append(data.ranges[x] if data.ranges[x] < 10 else 10)
    
        if debug print(q) else pass
        if debug print("A") else pass
        plt.subplot(111,projection='polar')
        if debug print("B") else pass
        plt.scatter(theta, ranges, s=1)
        if debug print("C") else pass
        plt.draw()
        if debug print("D") else pass
#        plt.pause(rate/float(80)) #one of these has to be a float otherwise value becomes 0 if rate < 40
        plt.pause(0.00000001) 
        if debug print("E") else pass
        #plt.figure().clear()
        plt.clf()
        if debug print("F") else pass
        #plt.close()
    

def angle(desiredAngle): #Input = angle normal people use. Counter clockwise from -135 to 135
    desiredAngle += 135
    return int(desiredAngle*(1081/270)) #Output = closest point where desired angle matches up within the LiDAR's sweep

def lidarListener(): #Subscriber be here!
    rp.init_node("lidarListener", anonymous=True)
    rp.Subscriber("scan", LaserScan, callback)
    rp.spin()

def averageRanges(data, desiredAngleLow, desiredAngleHigh): #Finds the average distance in meters of the LiDAR responses within the specified range
    angleLow = angle(desiredAngleLow)
    angleHigh = angle(desiredAngleHigh)
    averageRangesReturn = 0

    for x in range(angleLow,angleHigh):
        averageRangesReturn += data.ranges[x]
    return averageRangesReturn / (angleHigh-angleLow)

def averageAllRanges(data): #Finds the average distance of the LiDAR to the full 270 degree FOV
    return averageRanges(data, -135, 135)

def averageIntensities(data): #May not be necessary
    averageIntensitiesReturn = 0
    for x in range(0,len(data.intensities)):
        averageIntensitiesReturn += data.intensities[x]
    return averageIntensitiesReturn / len(data.intensities)

def displayLidar(ranges): #Incomplete
    plt.subplot(111, projection='polar')
    plt.scatter(ranges, y, color='k', s=4)
    #plt.show()    
    plt.draw()
    plt.pause(0.001)
    
    
if __name__ == '__main__':
    lidarListener()
