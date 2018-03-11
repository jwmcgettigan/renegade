import cv2

cap=cv2.VideoCapture(1)

if cap.isOpened():
    while True:
        ret,img = cap.read()
        print img.shape
        cv2.imshow("Video", img)
        if cv2.waitKey(20) & 0xFF == ord('q'):
      	    break
else:
    print "Unable to capture Camera";
    exit(-1)
