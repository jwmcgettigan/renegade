import numpy as np
import cv2
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import helper as h

def nothing():
    pass


class colorFilter:

    def __init__(self, color):
        functions = h.Functions()
        cap = cv2.VideoCapture('C:/Users/jmcgettigan/Desktop/renegade_videos/crazyCones.avi')
        #image = cv2.imread('C:\Users\jmcgettigan\Pictures\serpentineSlow.png')
        placeholder = cv2.imread('C:/Users/jmcgettigan/Pictures/trackbarPlaceholder.jpg')
        self.createWindowsAndSliders(color, placeholder, cap, functions)
        cap.release()


    def createWindowsAndSliders(self, color, placeholder, cap, functions):
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
        self.display(cap, functions, window, values)


    def display(self, cap, functions, window, values):
        while cap.isOpened() and cv2.getWindowProperty('Slider', 0) >= 0 and cv2.getWindowProperty('Image', 0) >= 0 :
            ret, image = cap.read()
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

            gray = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)
            imgray = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)
            ret, thresh = cv2.threshold(imgray, 127, 255, 0)
            image2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            cnt = contours[0]
            M = cv2.moments(cnt)
            print M
            #final_image = cv2.drawContours(img, [cnt], 0, (0,255,0), 3)
            final_image = cv2.drawContours(image, contours, -1, (0,255,0), 3)

            #final_image = functions.canny_detector(masked_image)

            cv2.imshow('Image', final_image)
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break


if __name__ == '__main__':
    red = [0, 0, 0], [0, 0, 0]
    blue = [0, 80, 0], [17, 255, 255]
    yellow = [93, 190, 77], [106, 255, 255]
    orange = [104, 209, 0], [122, 255, 255]
    colorFilter(yellow)
    cv2.destroyAllWindows()
