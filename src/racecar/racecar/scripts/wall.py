#!/usr/bin/python

from item import Item
import cv2, numpy as np
import math

class Wall(Item):
    

    def __init__(self):
        pass

    def run(self, lidar):
        self.data = lidar.getData()
        getWall()

    def getWall(self):
        tempRanges = self.data.ranges #Place holder until object is filtered out which will reduce list size
        divisor = []
        for x in range(0, len(tempRanges)): divisor.append(x) #Filling divisor with list 0 to len(ranges)-1. Essentially the spacing on the x coordinate on a graph.polyfitlinearRegression = np.polyfit(divisor, ranges, 1) #result from polyfit is line of best fit's formula, [2,3] is y = 2x+3
        angleOfWall = math.atan(np.polyfit(divisor, tempRanges, 1)[0]) #result from polyfit is line of best fit's formula, [2,3] is y = 2x+3
        averageDistanceToWall = np.average(ranges)
        return angleOfWall, averageDistanceToWall


