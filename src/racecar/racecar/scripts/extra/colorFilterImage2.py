import numpy as np
import cv2
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import helper as h

def nothing():
    pass

VIDEO=True

class colorFilter:

    def __init__(self, color):
        functions = h.Functions()
        self.cap = cv2.VideoCapture('C:/Users/jmcgettigan/Desktop/renegade_videos/slowBlueLaneFull.avi')
        self.image = cv2.imread('C:\Users\jmcgettigan\Pictures\serpentineSlow.png')
        placeholder = cv2.imread('C:/Users/jmcgettigan/Pictures/trackbarPlaceholder.jpg')
        self.createWindowsAndSliders(color, placeholder, functions)
        self.cap.release()


    def createWindowsAndSliders(self, color, placeholder, functions):
        cv2.namedWindow('Slider', cv2.WINDOW_NORMAL)
        cv2.namedWindow('Image', cv2.WINDOW_KEEPRATIO)

        H_l = 'H Low'
        S_l = 'S Low'
        V_l = 'V Low'
        H_h = 'H High'
        S_h = 'S High'
        V_h = 'V High'
        window = 'Slider'
        cv2.imshow(window, placeholder)
        cv2.resizeWindow(window, 300, 280)

        cv2.createTrackbar(H_l, window, color[0][0], 180, nothing)
        cv2.createTrackbar(S_l, window, color[0][1], 255, nothing)
        cv2.createTrackbar(V_l, window, color[0][2], 255, nothing)
        cv2.createTrackbar(H_h, window, color[1][0], 180, nothing)
        cv2.createTrackbar(S_h, window, color[1][1], 255, nothing)
        cv2.createTrackbar(V_h, window, color[1][2], 255, nothing)
        values = [H_l, S_l, V_l, H_h, S_h, V_h]
        self.display(functions, window, values)


    def display(self, functions, window, values):

        while cv2.getWindowProperty('Slider', 0) >= 0 and cv2.getWindowProperty('Image', 0) >= 0 :
            if VIDEO:
                ret, image = self.cap.read()
            else: image = self.image.copy()
            # read trackbar positions for each trackbar
            Hl = cv2.getTrackbarPos(values[0], window)
            Sl = cv2.getTrackbarPos(values[1], window)
            Vl = cv2.getTrackbarPos(values[2], window)
            Hh = cv2.getTrackbarPos(values[3], window)
            Sh = cv2.getTrackbarPos(values[4], window)
            Vh = cv2.getTrackbarPos(values[5], window)


            converted_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            lower_threshold = np.uint8([Hl, Sl, Vl])
            upper_threshold = np.uint8([Hh, Sh, Vh])
            mask = cv2.inRange(converted_image, lower_threshold, upper_threshold)

            masked_image = cv2.bitwise_and(image, image, mask=mask)

            imgray = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(imgray, (5,5), 0)
            thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY)[1]
            contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
            if len(contours) > 0:
                print "List isn't empty"
                self.process(contours, masked_image, image)
                #self.process2(contours, masked_image)
            else:
                print "List empty"
                cv2.imshow('Image', masked_image)
            #final_image = cv2.drawContours(image, contours, -1, (0,255,0), 3)
            #final_image = functions.canny_detector(masked_image)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def process(self, contours, mi, image):
        # loop over the contours
        for c in contours:
            if cv2.contourArea(c) >= 5000:
                #cv2.drawContours(image, [c], -1, (0, 255, 0), 1)

                #cv2.convexHull(c)
                #self.drawRotatedRectangle(c, image)
                self.drawRectangle(c, image)
                self.drawCenter(c, image)
                cv2.imshow('Image', image)
                cv2.waitKey(1)


    def drawCenter(self, c, image):
        M = cv2.moments(c)
        if M["m00"] > 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else: cX, cY = 0, 0
        cv2.circle(image, (cX, cY), 5, (0, 0, 255), -1)
        #cv2.putText(image, "center", (cX - 20, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)


    def drawRotatedRectangle(self, c, image):
        rect = cv2.minAreaRect(c)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(image,[box],0,(0,0,255),2)


    def drawRectangle(self, c, image):
        x,y,w,h = cv2.boundingRect(c)
        cv2.rectangle(image, (x,y), (x+w,y+h),(0,255,0),2)


    def drawLargestContour(self, contours, image):
        if len(contours) != 0:
            # draw in the contours
            cv2.drawContours(image, contours, -1, 255, 3)

            #find the biggest area
            c = max(contours, key = cv2.contourArea)

            x,y,w,h = cv2.boundingRect(c)
            #draw the contour
            cv2.rectangle(image, (x,y), (x+w,y+h),(0,255,0),3)

        cv2.imshow("Image", np.hstack([self.image, image]))


if __name__ == '__main__':
    red = [0, 0, 0], [0, 0, 0]
    blue = [0, 80, 0], [17, 255, 255]
    yellow = [93, 190, 77], [106, 255, 255]
    orange = [104, 209, 0], [122, 255, 255]
    colorFilter(yellow)
    cv2.destroyAllWindows()
