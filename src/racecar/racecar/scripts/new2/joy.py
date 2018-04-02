#!/usr/bin/python
# ----------------
# joy controller data can be retrieved from this file
# subscribe to joy controller

import rospy as rp

class Joy:

    def __init__(self):
        pass


    def setData(self, data):
        self.data = data


    def getData(self):
        return self.data
