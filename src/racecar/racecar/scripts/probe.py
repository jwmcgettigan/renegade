#!/usr/bin/env python
import rospy as rp
from sensor_msgs.msg import LaserScan


def callback(data):
    print(data)


rp.Subscriber("eyes")
