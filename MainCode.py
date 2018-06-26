import PyCapture2
from sys import exit
import time
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import cv2
from Utilities.Cam_setup import CamSetup

#############
##Variables##
#############

#set frame rate
framerate = 240


#############
##Main Code##
#############

#goes into camSetup Library and initalizes CAMERA
c = CamSetup()
camera = c.CameraSetup(framerate)

camera.startCapture()

#video loop
while True:
    frame = camera.retrieveBuffer()
    cv_image = np.array(frame.getData(), dtype="uint8").reshape((frame.getRows(), frame.getCols()) );
    print cv_image.shape
    bilateral_filtered_image = cv2.bilateralFilter(cv_image, 5, 175, 175)
    canny = cv2.Canny(bilateral_filtered_image,75,255)
    ret,thresh = cv2.threshold(canny,200,500,0)
    im2, contoursfound, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contour_list = []

    for contour in contoursfound:
        approx = cv2.approxPolyDP(contour,0.02*cv2.arcLength(contour,True),True)
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour,True)

        if (((len(approx) <= 4)) & ((area < 10000)) ):
        #if (((len(approx) < 4) ) & ((area >30) & (area < 6000)) & (perimeter > 1)):
            contour_list.append(contour)

    mask = np.zeros(cv_image.shape,np.uint8)
    mask = cv2.drawContours(mask,contour_list,-1,255,-1)

    #mask &= canny


#    cv2.drawContours(cv_image, contour_list, -1, (255,0,0), 2)
    cv2.imshow('Objects Detected',mask)
    cv2.waitKey(10)
