#!/usr/bin/python
# ----------------
#

from item import Item
import cv2, numpy as np

class Cube:
    # color (hsv)
    # size (radius)
    # boundingBox (box around object)
    # center
    # weight (significance/priority of object)

    def __init__(self, contour, image, distance, angle):
        self.center = self.calculateCenter(contour)
        self.bounds = self.calculateBounds(contour)
        self.contour = contour
        self.image = image
        self.distance = distance
        self.angle = angle


    def getCenter(self):
        return self.center


    def getDistance(self):
        return self.distance


    def getAngle(self):
        return self.angle


    def getImage(self):
        return self.image


    def getContourArea(self):
        return self.contour.contourArea()


    def getIsCube(self):
        return True


    def getBounds(self):
        return self.bounds


    def draw(self):
        c = self.contour
        self.drawRectangle(c, self.image)
        self.drawCenter(c, self.image)
        return self.image


    def drawRectangle(self, c, image):
        x,y,w,h = self.bounds
        print "%.2f %.2f %.2f %.2f" % (x, y, w, h)
        cv2.rectangle(image, (x,y), (x+w,y+h),(0,255,0),2)
        cv2.putText(image, "CUBE", (self.center[0] - w/2, self.center[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)


    def drawCenter(self, c, image):
        cv2.circle(image, self.center, 5, (0, 0, 255), -1)


    def calculateCenter(self, c):
        M = cv2.moments(c)
        if M["m00"] > 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else: cX, cY = 0, 0
        return cX, cY


    def calculateBounds(self, c):
        x,y,w,h = cv2.boundingRect(c)
        print "%.2f %.2f %.2f %.2f" % (x, y, w, h)
        return x, y, w, h
