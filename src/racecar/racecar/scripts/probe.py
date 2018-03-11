#!/usr/bin/env python
import rospy as rp
from sensor_msgs.msg import LaserScan
from sensor_msgs.msg import Image
from matplotlib import pyplot as plt

plt.ion
y = []
for x in range(0,1081):
    y.append(x)

def callback(data):
    #rp.loginfo(rp.get_caller_id() + "I heard %s", data.data) 
    #print(type(data.ranges))
    #print(len(data.ranges))
    #print(averageRanges(data))
    #print(averageIntensities(data))
    #print(data.ranges)
    #displayLidar(data.ranges)
    
    print(string(data.ranges[600])+string(data.ranges[500]))


    #plt.subplot(111,projection='polar')
    #plt.scatter(data.ranges, y, color='k', s=4)
    #plt.draw()
    #plt.pause(0.01)
    pass

def lidarListener():
    rp.init_node("lidarListener", anonymous=True)
    rp.Subscriber("scan", LaserScan, callback)
    rp.spin()

def averageRanges(data):
    averageRangesReturn = 0

    for x in range(0,len(data.ranges)):
        averageRangesReturn += data.ranges[x]
    return averageRangesReturn / len(data.ranges)

def averageIntensities(data):
    averageIntensitiesReturn = 0
    for x in range(0,len(data.intensities)):
        averageIntensitiesReturn += data.intensities[x]
    return averageIntensitiesReturn / len(data.intensities)

def displayLidar(ranges):
    plt.subplot(111, projection='polar')
    plt.scatter(ranges, y, color='k', s=4)
    #plt.show()    
    plt.draw()
    plt.pause(0.001)
    
    
    



if __name__ == '__main__':
    lidarListener()
