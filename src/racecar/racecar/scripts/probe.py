#!/usr/bin/env python
import rospy as rp
from sensor_msgs.msg import LaserScan
from sensor_msgs.msg import Image
from matplotlib import pyplot as plt

def callback(data):
    #rp.loginfo(rp.get_caller_id() + "I heard %s", data.data) 
    #print(type(data.ranges))
    #print(len(data.ranges))
    #print(averageRanges(data))
    #print(averageIntensities(data))
    #print(data.ranges)
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
    y = []
    for x in range(0,1080):
        y.append(z)
    plt.subplot(111, projection='polar')
    #plt.scatter(




if __name__ == '__main__':
    lidarListener()
