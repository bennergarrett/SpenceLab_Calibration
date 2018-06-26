# Standard imports
import cv2
import numpy as np;
from sys import exit
# Read image

im = cv2.imread('test.png')
imgray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
ret,thresh = cv2.threshold(imgray,127,255,0)
image, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
#print(contours)


contour_list = []

for contour in contours:
    approx = cv2.approxPolyDP(contour,0.01*cv2.arcLength(contour,True),True)
    area = cv2.contourArea(contour)
    if ((len(approx) > 10) & ((area >500) & (area < 10000))):
        contour_list.append(contour)


mask = np.zeros(imgray.shape,np.uint8)
mask = cv2.drawContours(mask,contour_list,0,255,-1)
#imgray &= mask
#pixelpoints = cv2.findNonZero(mask)
imgray = cv2.drawContours(imgray, contour_list, 1, (0,255,0), 3)
#cv2.imshow('Objects Detected',imgray)
cv2.imshow('mask', mask)
cv2.imshow('gray image', imgray)
cv2.imshow('pixel', pixelpoints)
cv2.waitKey(0)
