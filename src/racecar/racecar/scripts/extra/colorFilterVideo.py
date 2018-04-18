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
        #cap = cv2.VideoCapture('C:/Users/jmcgettigan/Desktop/renegade_videos/slowBlueLaneFull.avi')
        cap = cv2.VideoCapture(1)
        #image = cv2.imread('C:\Users\jmcgettigan\Pictures\serpentineSlow.png')
        placeholder = cv2.imread('trackbarPlaceholder.jpg')
        self.createWindowsAndSliders(color, placeholder, cap, functions)
        cap.release()


    def createWindowsAndSliders(self, color, placeholder, cap, functions):
        cv2.namedWindow('Slider', cv2.WINDOW_NORMAL)
        cv2.namedWindow('Image', cv2.WINDOW_NORMAL)

        H_l = 'H Low'
        S_l = 'S Low'
        V_l = 'V Low'
        H_h = 'H High'
        S_h = 'S High'
        V_h = 'V High'
        window = 'Slider'
        #cv2.imshow(window, placeholder)
        cv2.resizeWindow(window, 300, 280)

        cv2.createTrackbar(H_l, window, color[0][0], 255, nothing)
        cv2.createTrackbar(S_l, window, color[0][1], 255, nothing)
        cv2.createTrackbar(V_l, window, color[0][2], 255, nothing)
        cv2.createTrackbar(H_h, window, color[1][0], 255, nothing)
        cv2.createTrackbar(S_h, window, color[1][1], 255, nothing)
        cv2.createTrackbar(V_h, window, color[1][2], 255, nothing)
        values = [H_l, S_l, V_l, H_h, S_h, V_h]
        self.display(cap, functions, window, values)


    def display(self, cap, functions, window, values):
        while cap.isOpened() and cv2.getWindowProperty('Slider', 0) >= 0 and cv2.getWindowProperty('Image', 0) >= 0 :
            ret, img = cap.read()
            height, width = img.shape[:2]
            #image = image[height/3:height/2, :width/2]
            #image = img[:height, :width/2]
            images = [img[:height, :width/2], img[:height, width/2:width]]
            height, width = img.shape[:2]
            #image = image[height/3:height/3+15, :width/2]
            #image = image[height/3:height/2, :width/2]
            # read trackbar positions for each trackbar
            Hl = cv2.getTrackbarPos(values[0], window)
            Sl = cv2.getTrackbarPos(values[1], window)
            Vl = cv2.getTrackbarPos(values[2], window)
            Hh = cv2.getTrackbarPos(values[3], window)
            Sh = cv2.getTrackbarPos(values[4], window)
            Vh = cv2.getTrackbarPos(values[5], window)

            """
            imageStrips = [img[int((2/9.0)*height):int((3/9.0)*height), :width],
                           #np.zeros((2,width,3), np.uint8),
                           img[int((3/9.0)*height):int((4/9.0)*height), :width]]
            """
            """
            images = [img[int((3/10.0)*height):int((4/10.0)*height), :width],
                           #np.zeros((2,width,3), np.uint8),
                           img[int((4/10.0)*height):int((5/10.0)*height), :width]]
            """
            for image in images:
                converted_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                #converted_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
                #converted_image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
                lower_threshold = np.uint8([Hl, Sl, Vl])
                upper_threshold = np.uint8([Hh, Sh, Vh])
                mask = cv2.inRange(converted_image, lower_threshold, upper_threshold)

                masked_image = cv2.bitwise_and(image, image, mask=mask)

                imgray = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)
                #ret, thresh = cv2.threshold(imgray, 127, 255, 0)
                blurred = cv2.GaussianBlur(imgray, (5,5), 0)
                thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY)[1]
                contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
                cv2.drawContours(masked_image, contours, -1, (0,255,0), 3)
                #cv2.line(image, (width/3, 0), (width/3, height), [0, 0, 255], 3)

                if len(contours) > 0:
                    c = max(contours, key = cv2.contourArea)
                    M = cv2.moments(c)
                    if M["m00"] > 0:
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])
                    else: cX, cY = 0, 0

                    cv2.circle(masked_image, (cX, cY), 5, (0, 0, 255), -1)
                else:
                    pass

                cv2.imshow('Image', masked_image)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            #cv2.imshow('Image', np.vstack(imageStrips))


if __name__ == '__main__':
    """
    #red = [110, 185, 0], [180, 255, 255]
    red = [110, 185, 0], [130, 255, 255]
    blue = [0, 80, 0], [17, 255, 255]
    greyBlue = [0, 0, 87], [96, 255, 174]
    lane = [0, 120, 120], [30, 255, 255]
    lane2 = [0, 120, 100], [30, 255, 255]
    #greyBlue = [0, 10, 110], [30, 255, 255]
    yellow = [93, 190, 77], [106, 255, 255]
    orange = [104, 209, 0], [122, 255, 255]
    #green = [20, 40, 0], [90, 180, 180]
    green = [20, 40, 0], [90, 255, 180]
    blueLAB = [71, 109, 109], [161, 133, 141]
    """
    redLAB = [0, 150, 140], [255, 190, 160]
    greenLAB = [0, 110, 0], [60, 120, 255]
    blueLABdark = [71, 109, 109], [161, 133, 141]
    blueLABlight = [0, 90, 80], [255, 140, 125]
    colorFilter(blueLABlight)
    cv2.destroyAllWindows()


"""
cv2.line(image, (int((4/9.0)*width), 0), (int((4/9.0)*width), height), [255, 0, 255], 3)
cv2.line(image, (int((5/9.0)*width), 0), (int((5/9.0)*width), height), [255, 0, 255], 3)
cv2.line(image, (0, int((4/9.0)*height)), (width, int((4/9.0)*height)), [0, 0, 255], 3)
cv2.line(image, (0, int((5/9.0)*height)), (width, int((5/9.0)*height)), [0, 0, 255], 3)
cv2.line(image, (0, int((2/9.0)*height)), (width, int((2/9.0)*height)), [0, 255, 255], 3)
cv2.line(image, (0, int((3/9.0)*height)), (width, int((3/9.0)*height)), [0, 255, 255], 3)


imageStrips = [image[int((2/9.0)*height):int((3/9.0)*height), :width],
               np.zeros((2,width,3), np.uint8),
               image[int((3/9.0)*height):int((4/9.0)*height), :width]]#,
               #np.zeros((height/20,width,3), np.uint8),
               #image[int((4/9.0)*height):int((5/9.0)*height), :width]]

imageStrips = [image[int((5/18.0)*height):int((6/18.0)*height), :width],
               np.zeros((2,width,3), np.uint8),
               image[int((6/18.0)*height):int((7/18.0)*height), :width],
               np.zeros((2,width,3), np.uint8),
               image[int((7/18.0)*height):int((8/18.0)*height), :width]]
"""
#final_image = cv2.drawContours(img, [cnt], 0, (0,255,0), 3)
#final_image = cv2.drawContours(image, contours, -1, (0,255,0), 3)

#final_image = functions.canny_detector(masked_image)
