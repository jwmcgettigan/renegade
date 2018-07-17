import numpy as np
import cv2


def nothing():
    pass

image = cv2.imread('C:\Users\jmcgettigan\Pictures\simpleColor.png')
placeholder = cv2.imread('C:\Users\jmcgettigan\Pictures\\trackbarPlaceholder.jpg')

"""The coordinates of vertices of the triangle."""
triangle = np.array([[120, 540], [480, 290], [940, 540]])

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

cv2.createTrackbar(H_l, window, 0, 180, nothing)
cv2.createTrackbar(S_l, window, 0, 255, nothing)
cv2.createTrackbar(V_l, window, 0, 255, nothing)
cv2.createTrackbar(H_h, window, 0, 180, nothing)
cv2.createTrackbar(S_h, window, 0, 255, nothing)
cv2.createTrackbar(V_h, window, 0, 255, nothing)

while cv2.getWindowProperty('Slider', 0) >= 0 and cv2.getWindowProperty('Image', 0) >= 0 :
    # read trackbar positions for each trackbar
    Hl = cv2.getTrackbarPos(H_l, window)
    Sl = cv2.getTrackbarPos(S_l, window)
    Vl = cv2.getTrackbarPos(V_l, window)
    Hh = cv2.getTrackbarPos(H_h, window)
    Sh = cv2.getTrackbarPos(S_h, window)
    Vh = cv2.getTrackbarPos(V_h, window)

    converted_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    lower_threshold = np.uint8([Hl, Sl, Vl])
    upper_threshold = np.uint8([Hh, Sh, Vh])
    mask = cv2.inRange(converted_image, lower_threshold, upper_threshold)

    masked_image = cv2.bitwise_and(image, image, mask=mask)

    cv2.imshow('Image', masked_image)
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break


cv2.destroyAllWindows()
