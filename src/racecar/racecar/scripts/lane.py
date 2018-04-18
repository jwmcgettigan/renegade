#!/usr/bin/python
# ----------------
#

from item import Item
import cv2, numpy as np

class Lane(Item):

    def __init__(self, walls, centers, slope, area):
        super(Lane, self).__init__()
        self.walls = walls
        self.centers = centers
        self.slope = slope
        self.area = area


    def getWalls(self):
        return self.walls


    def getCenters(self):
        return self.centers


    def getSlope(self):
        return self.slope


    def getArea(self):
        return self.area
