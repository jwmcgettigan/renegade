#!/usr/bin/python
# ----------------
#

import cv2, numpy as np

class Cone:
    # color (hsv)
    # size (radius)
    # boundingBox (box around object)
    # center
    # weight (significance/priority of object)

    def __init__(self, contour, image, distance, angle):
        self.center = self.calculateCenter(contour)
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


    def draw(self):
        c = self.contour
        self.drawRectangle(c, self.image)
        self.drawCenter(c, self.image)
        return self.image


    def drawRectangle(self, c, image):
        x,y,w,h = cv2.boundingRect(c)
        cv2.rectangle(image, (x,y), (x+w,y+h),(0,255,0),2)


    def drawCenter(self, c, image):
        cv2.circle(image, self.center, 5, (0, 0, 255), -1)
        #cv2.putText(image, "center", (cX - 20, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)


    def calculateCenter(self, c):
        M = cv2.moments(c)
        if M["m00"] > 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else: cX, cY = 0, 0
        return cX, cY
