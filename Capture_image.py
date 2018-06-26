import PyCapture2

#Variables
image_name = "test.png"

#Cam Info
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


############################################
##Commands

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
	for i in xrange(numImagesToGrab):
		try:
			image = cam.retrieveBuffer()
		except PyCapture2.Fc2error as fc2Err:
			print "Error retrieving buffer : ", fc2Err
			continue

		ts = image.getTimeStamp()
		if (prevts):
			diff = (ts.cycleSeconds - prevts.cycleSeconds) * 8000 + (ts.cycleCount - prevts.cycleCount)
			print "Timestamp [", ts.cycleSeconds, ts.cycleCount, "] -", diff
		prevts = ts

	newimg = image.convert(PyCapture2.PIXEL_FORMAT.BGR)
	print "Saving the last image to {}".format(image_name)
	newimg.save(image_name, PyCapture2.IMAGE_FILE_FORMAT.PNG)

#manage cameras
bus = PyCapture2.BusManager()
numCams = bus.getNumOfCameras()
print "Number of cameras detected: ", numCams
if not numCams:
	print "Insufficient number of cameras. Exiting..."
	exit()

#########################################
##MAIN CODE

# Select camera on 0th index
c = PyCapture2.Camera()
uid = bus.getCameraFromIndex(0)
c.connect(uid)
printCameraInfo(c)

# Enable camera embedded timestamp
enableEmbeddedTimeStamp(c, True)

print "Starting image capture..."
c.startCapture()
grabImages(c, 100)
c.stopCapture()

# Disable camera embedded timestamp
enableEmbeddedTimeStamp(c, False)
c.disconnect()

raw_input("Done! Press Enter to exit...\n")
