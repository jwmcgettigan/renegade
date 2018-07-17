#!/usr/bin/python
# ----------------
#

from item import Item
import cv2, numpy as np

class Sign(Item):

    def __init__(self, center, area):
        super(Sign, self).__init__()
        self.center = center
        self.area = area


    def getCenter(self):
        return self.center


    def getArea(self):
        return self.area
