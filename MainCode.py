import PyCapture2
from sys import exit
import time
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import cv2
from Utilities.Cam_setup import*
from Utilities.Motor_Class import*
import matplotlib.pyplot as plt
import time

#############
##Variables##
#############

#set frame rate
framerate = 200
exposure = 1

#value of transparency for FPS and such
alpha = 0.75
#variables for Trackbars
miS = 'Minimum Number of Sides'
maS = 'Maximum Number of Sides'
miA = 'Minimum Area Size'
maA = 'Maximum Area Size'
wnd = 'test'

#############
##Functions##
#############

#You shall not pass
def nothing(self):
    pass


def grab_frame(f):
    #retreive image
    frame = f
    #convert data into image
    cv_image = np.array(frame.getData(), dtype="uint8").reshape((frame.getRows(), frame.getCols()) );
    #make into 3 channels
    grey_3_channel = cv2.cvtColor(cv_image, cv2.COLOR_BAYER_BG2BGR)
    #make grey
    #return grey_3_channel
    return cv2.cvtColor(grey_3_channel, cv2.COLOR_RGB2GRAY)


def filter_frame(grey,minSide, maxSide, minArea, maxArea):
    #smooth edges
    #bilateral_filtered_image = cv2.bilateralFilter(grey, 11, 17, 17)
    #edge detection
    canny = cv2.Canny(grey,75,255, cv2.THRESH_BINARY)
    ret,thresh = cv2.threshold(canny,200,500,0)
    #find contours
    im2, contoursfound, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contour_list = []
    #filtering contours
    for contour in contoursfound:
        approx = cv2.approxPolyDP(contour,0.02*cv2.arcLength(contour,True),True)
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour,True)

        if (((len(approx) >= minSide) & (len(approx) <= maxSide)) & ((area >= minArea) & (area <= maxArea)) ):
        #if (((len(approx) < 4) ) & ((area >30) & (area < 6000)) & (perimeter > 1)):
            contour_list.append(contour)
    #masking to only show filtered image
    # loop over the contours


    mask = np.zeros(grey.shape,np.uint8)
    mask = cv2.drawContours(mask,contour_list,-1,255,-1)

    try:
        for c in contour_list:
	         # compute the center of the contour
	        M = cv2.moments(c)
	        cX = int(M["m10"] / M["m00"])
	        cY = int(M["m01"] / M["m00"])

	        # draw the contour and center of the shape on the image
	        cv2.drawContours(mask, [c], -1, (0, 255, 0), 2)
	        cv2.circle(mask, (cX, cY), 7, (255, 255, 255), -1)
	        cv2.putText(mask, "center", (cX - 20, cY - 20),
		        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    ####EXCEPT
    except:
        print("error:no object detected")
    try:
        #square seems to be always last one in contour list
        #puts boundary on square
        rect = cv2.minAreaRect(contour_list[-1])
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        #print(box.shape)
        im = cv2.drawContours(mask,[box],0,(255,0,0),-1)
        return im
    except:
        return mask
def filter_frame_V2(grey):
    #smooth edges
    #bilateral_filtered_image = cv2.bilateralFilter(grey, 11, 17, 17)
    #edge detection
    canny = cv2.Canny(grey,75,255, cv2.THRESH_BINARY)
    ret,thresh = cv2.threshold(canny,200,500,0)
    #find contours
    im2, contoursfound, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contour_list = []
    mask = np.zeros(grey.shape,np.uint8)
    try:
        mask = cv2.drawContours(mask,contour_list[-1],-1,255,-1)
        return mask
    except:
        return canny

def combineImages(img1, img2):
    return np.concatenate((img1, img2), axis=0) #change axis to =1 to stack horizontally


def capIm(cam):
    try:
        img = cam.retrieveBuffer()
    except PyCapture2.Fc2error as fc2Err:
        print("Error retrieving buffer :", fc2Err)
        return False, []


  # data = np.array(img.getData(), dtype=np.uint8)
  # data = data.reshape((img.getRows(), img.getCols()))


       #img.save('tmp.bmp'.encode("utf-8"), PyCapture2.IMAGE_FILE_FORMAT.BMP)
       #data = cv2.imread('tmp.bmp', 0)
    return True, img


#ffmpeg-python instead?
#video skips and breaks up
def saveAviHelper(cam, fileFormat, fileName, frameRate):
    i = 0
    avi = PyCapture2.AVIRecorder()
	#for i in range(numImages):
    while(1):
        try:
            try:
                ret, image = capIm(cam)
                if not ret:
                    print("no image")
                    break
            except PyCapture2.Fc2error as fc2Err:
                print "Error retrieving buffer : ", fc2Err
                continue

            print "Grabbed image {}".format(i)

            if (i == 0):
                if fileFormat == "AVI":
                    avi.AVIOpen(fileName, frameRate)
                elif fileFormat == "MJPG":
                    avi.MJPGOpen(fileName, frameRate, 75)
                elif fileFormat == "H264":
                    avi.H264Open(fileName, frameRate, image.getCols(), image.getRows(), 1000000)
                else:
                    print "Specified format is not available."
                    return
            avi.append(image)
            print "Appended image {}...".format(i)
            i = 1+ i
            #print i
        except KeyboardInterrupt:
            break
    print "Appended {} images to {} file: {}...".format(i, fileFormat, fileName)
    avi.close()


#############
##Main Code##
#############

#goes into camSetup Library from the Utilities Folder and initalizes CAMERA
c = CamSetup()
motor = motor()
#try:
#ch = motor.motorConnect()
#print(ch)
#motor.motorTrial(ch)
#except:
    #print("Motor Connection failed")

camera = c.CameraSetup(framerate, exposure)
c.FrameRate(camera)
camera.startCapture()
fRateProp = camera.getProperty(PyCapture2.PROPERTY_TYPE.FRAME_RATE)
frameRate = fRateProp.absValue
print "Using frame rate of {}".format(frameRate)

fileFormat = "AVI"
#fileName = "SaveImageToAviEx_{}.avi".format(fileFormat)
fileName = "SaveImageToAviEx.avi".format(fileFormat)
saveAviHelper(camera, fileFormat, fileName, frameRate)
print "Stopping capture..."
camera.stopCapture()




#name of window
cv2.namedWindow(wnd)
#creating Trackbars
cv2.createTrackbar(miS, 'test', 0, 20, nothing)
cv2.createTrackbar(maS, 'test', 4, 20, nothing)
cv2.createTrackbar(miA, 'test', 0, 20000, nothing)
cv2.createTrackbar(maA, 'test', 20000, 20000, nothing)

camera.startCapture()
print('press Escape to Exit Program')

#to make faster:
#external triggering mode
#exposure reduction

start = time.time()
frame = 0
#video loop
while True:
    frame = frame + 1
    timestamp = time.time()
    fps = frame/(timestamp-start)
    minSide = cv2.getTrackbarPos(miS,wnd)
    maxSide = cv2.getTrackbarPos(maS, wnd)
    minArea = cv2.getTrackbarPos(miA, wnd)
    maxArea = cv2.getTrackbarPos(maA, wnd)

    #grabs image and converts to greyscale
    grey = grab_frame(camera.retrieveBuffer())
    #calls mask function and masks image
    #takes a lot of time...
    mask = filter_frame(grey, minSide, maxSide, minArea, maxArea)
    #mask = filter_frame_V2(grey)
    #combines images to compare
    ##frameOut = combineImages(grey, mask)
    res = cv2.resize(mask, (640,512))
    ##res = cv2.resize(frameOut, (1280/2, 1024/2 ))

    overlay = res
    output = res

    cv2.putText(overlay, "FPS: {}".format(fps),
	    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 5, 0), 3)

	#apply the overlay
    cv2.addWeighted(overlay, alpha, output, 1 - alpha,
        0, output)

    #shows final product
    cv2.imshow(wnd,output)
    #cv2.imshow('unfiltered', grey)
    #cv2.imshow('Objects Detected',mask)
    #delay time before updating
    Key = cv2.waitKey(1)
    if(Key == 27):
        break #press escape to end

print("Goodbye!")
camera.stopCapture()
camera.disconnect()
cv2.destroyAllWindows()
quit()
