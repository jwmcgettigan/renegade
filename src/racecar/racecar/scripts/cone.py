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

    def __init__(self, contour, image):
        self.contour = contour
        self.image = image


    def getCenter(self):
        return self.center


    def draw(self):
        c = self.contour
        self.drawRectangle(c, self.image)
        self.drawCenter(c, self.image)
        return self.image


    def drawRectangle(self, c, image):
        x,y,w,h = cv2.boundingRect(c)
        cv2.rectangle(image, (x,y), (x+w,y+h),(0,255,0),2)


    def drawCenter(self, c, image):
        M = cv2.moments(c)
        if M["m00"] > 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else: cX, cY = 0, 0
        self.center = cX, cY
        cv2.circle(image, (cX, cY), 5, (0, 0, 255), -1)
        #cv2.putText(image, "center", (cX - 20, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
