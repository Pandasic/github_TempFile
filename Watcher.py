import cv2
from datetime import *
import time
cap = cv2.VideoCapture(0)

while 1:
    ret,im = cap.read()
    im = cv2.resize(im,(240,180))
    cv2.imshow("im",im)
    cv2.imwrite(datetime.now().strftime("%Y_%m_%d_%H_%M_%S")+".jpg",im)
    if cv2.waitKey(1000) == ord('q'):
        break