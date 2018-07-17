#!/usr/bin/python

from item import Item
import cv2, numpy as np, math

class Wall(Item):

    def __init__(self, angle, distance):
        super(Wall, self).__init__()
        self.angle = angle
        self.distance = distance


    def getAngle(self):
        return self.angle

    def getDistance(self):
        return self.distance
