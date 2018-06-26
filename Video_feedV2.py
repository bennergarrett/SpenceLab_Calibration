#=============================================================================
# Copyright 2017 FLIR Integrated Imaging Solutions, Inc. All Rights Reserved.
#
# This software is the confidential and proprietary information of FLIR
# Integrated Imaging Solutions, Inc. ("Confidential Information"). You
# shall not disclose such Confidential Information and shall use it only in
# accordance with the terms of the license agreement you entered into
# with FLIR Integrated Imaging Solutions, Inc. (FLIR).
#
# FLIR MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE
# SOFTWARE, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE, OR NON-INFRINGEMENT. FLIR SHALL NOT BE LIABLE FOR ANY DAMAGES
# SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING OR DISTRIBUTING
# THIS SOFTWARE OR ITS DERIVATIVES.
#=============================================================================
#http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_contours/py_table_of_contents_contours/py_table_of_contents_contours.html
import PyCapture2
from sys import exit
import time
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import cv2


def printBuildInfo():
	libVer = PyCapture2.getLibraryVersion()
	print "PyCapture2 library version: ", libVer[0], libVer[1], libVer[2], libVer[3]
	print

def printCameraInfo(cam):
	camInfo = cam.getCameraInfo()
	print "\n*** CAMERA INFORMATION ***\n"
	print "Serial number - ", camInfo.serialNumber
	print "Camera model - ", camInfo.modelName
	print "Camera vendor - ", camInfo.vendorName
	print "Sensor - ", camInfo.sensorInfo
	print "Resolution - ", camInfo.sensorResolution
	print "Firmware version - ", camInfo.firmwareVersion
	print "Firmware build time - ", camInfo.firmwareBuildTime
	print

def printFormat7Capabilities(fmt7info):
	print "Max image pixels: ({}, {})".format(fmt7info.maxWidth, fmt7info.maxHeight)
	print "Image unit size: ({}, {})".format(fmt7info.imageHStepSize, fmt7info.imageVStepSize)
	print "Offset unit size: ({}, {})".format(fmt7info.offsetHStepSize, fmt7info.offsetVStepSize)
	print "Pixel format bitfield: 0x{}".format(fmt7info.pixelFormatBitField)
	print

def enableEmbeddedTimeStamp(cam, enableTimeStamp):
	embeddedInfo = cam.getEmbeddedImageInfo()
	if embeddedInfo.available.timestamp:
		cam.setEmbeddedImageInfo(timestamp = enableTimeStamp)
		if(enableTimeStamp):
			print "\nTimeStamp is enabled.\n"
		else:
			print "\nTimeStamp is disabled.\n"

def grabImages(cam, numImagesToGrab):
	prevts = None
	start = time.time()
	for i in xrange(numImagesToGrab):
		try:
			image = cam.retrieveBuffer()
		except PyCapture2.Fc2error as fc2Err:
			print "Error retrieving buffer : ", fc2Err
			continue

		ts = image.getTimeStamp()
		if(prevts):
			diff = (ts.cycleSeconds - prevts.cycleSeconds) * 8000 + (ts.cycleCount - prevts.cycleCount)
			print "Timestamp [", ts.cycleSeconds, ts.cycleCount, "] -", diff
		prevts = ts
		stop =time.time()
		dt = stop - start
		print "Frame grab took: %0.04f which is %.0f FPS" % (dt,1./dt)
		start = stop
	print "Saving the last image to fc2CustomImageEx.png"
	image.save("fc2CustomImageEx.png", PyCapture2.IMAGE_FILE_FORMAT.PNG)


# Setup SimpleBlobDetector parameters.
params = cv2.SimpleBlobDetector_Params()

# Change thresholds
params.minThreshold = 10;
params.maxThreshold = 200;

# Filter by Area.
params.filterByArea = True
params.minArea = 1500

# Filter by Circularity
params.filterByCircularity = True
params.minCircularity = 0.1

# Filter by Convexity
params.filterByConvexity = True
params.minConvexity = 0.87

# Filter by Inertia
params.filterByInertia = True
params.minInertiaRatio = 0.01

# Create a detector with the parameters
ver = (cv2.__version__).split('.')
if int(ver[0]) < 3 :
    detector = cv2.SimpleBlobDetector(params)
else :
    detector = cv2.SimpleBlobDetector_create(params)





#
# Example Main
#

# Print PyCapture2 Library Information
printBuildInfo()

# Ensure sufficient cameras are found
bus = PyCapture2.BusManager()
numCams = bus.getNumOfCameras()
print "Number of cameras detected: ", numCams
if not numCams:
	print "Insufficient number of cameras. Exiting..."
	exit()

# Select camera on 0th index
c = PyCapture2.Camera()
c.connect(bus.getCameraFromIndex(0))

# Print camera details
printCameraInfo(c)
fmt7info, supported = c.getFormat7Info(0)
printFormat7Capabilities(fmt7info)

# See the pdf, use PROPERTY, and PROPERTY_TYPE, to set shutter.
# Set video mode to format 7, raw8
# Set height to reduced that is acceptable
# Ensure frame rate if FORMAT7
# go to town.
# test by reseting camera and ensure code resets it, not flycap.

if 0:
	# Check whether pixel format mono8 is supported
	if PyCapture2.PIXEL_FORMAT.MONO8 & fmt7info.pixelFormatBitField == 0:
		print "Pixel format is not supported\n"
		exit()

	# Configure camera format7 settings
	fmt7imgSet = PyCapture2.Format7ImageSettings(0, 0, 0, fmt7info.maxWidth, fmt7info.maxHeight, PyCapture2.PIXEL_FORMAT.MONO8)
	fmt7pktInf, isValid = c.validateFormat7Settings(fmt7imgSet)
	if not isValid:
		print "Format7 settings are not valid!"
		exit()
	c.setFormat7ConfigurationPacket(fmt7pktInf.recommendedBytesPerPacket, fmt7imgSet)
else:
	# spence go for speed. somewhere need to update frame rate option to turn off and free run
	# Check whether pixel format raw8 is supported
	if PyCapture2.PIXEL_FORMAT.RAW8 & fmt7info.pixelFormatBitField == 0:
		print "Pixel format is not supported\n"
		exit()

	# Configure camera format7 settings
	fmt7imgSet = PyCapture2.Format7ImageSettings(0, 0, 0, fmt7info.maxWidth, 512, PyCapture2.PIXEL_FORMAT.RAW8)
	fmt7pktInf, isValid = c.validateFormat7Settings(fmt7imgSet)
	if not isValid:
		print "Format7 settings are not valid!"
		exit()
	c.setFormat7ConfigurationPacket(fmt7pktInf.recommendedBytesPerPacket, fmt7imgSet)
#control frame rate
c.setProperty(type = PyCapture2.PROPERTY_TYPE.FRAME_RATE, autoManualMode = False)
c.setProperty(type = PyCapture2.PROPERTY_TYPE.FRAME_RATE, absValue = 240)
print "Getting camera frame rate"
print c.getVideoModeAndFrameRate()
print "enumerated rates are"
#print PyCapture2.FRAME_RATE

print
'''
In [9]: foo=PyCapture2.FRAMERATE

In [10]: foo
Out[10]: PyCapture2.FRAMERATE

In [11]: foo.
foo.FORMAT7   foo.FR_15     foo.FR_240    foo.FR_3_75   foo.FR_7_5
foo.FR_120    foo.FR_1_875  foo.FR_30     foo.FR_60     foo.mro

In [11]: foo.FORMAT7
Out[11]: 8
'''

'''
how to get and set properties?
In [2]: PyCapture2.Property(PyCapture2.PROPERTY_TYPE.SHUTTER)
Out[2]: <PyCapture2.Property instance at 0x7f0cfdb129e0>

In [3]: PyCapture2.Property(PyCapture2.PROPERTY_TYPE.SHUTTER).present
Out[3]: False
'''
'''
# Enable camera embedded timestamp
enableEmbeddedTimeStamp(c, True)

print "Starting image capture..."
c.startCapture()
grabImages(c, 10)
c.stopCapture()

# Disable camera embedded timestamp
enableEmbeddedTimeStamp(c, False)
'''
c.startCapture()

#video loop
while True:
    frame = c.retrieveBuffer()
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



c.disconnect()

raw_input("Done! Press Enter to exit...\n")
