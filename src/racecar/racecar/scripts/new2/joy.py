#!/usr/bin/python
# ----------------
# joy controller data can be retrieved from this file
# subscribe to joy controller

import rospy as rp
from sensor_msgs.msg import Joy

class Joy:

    def __init__(self):
        #rp.init_node("mode/manual/joy", anonymous=True)
        rp.Subscriber("vesc/joy", Joy, self.joy_callback)


    def callback(self, data):
        self.data = data


    def getData(self):
        return self.data
