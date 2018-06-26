import PyCapture2
import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
##Tutorials
#possible FPS increase: https://www.pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/
#video loop: https://www.pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/

#Variables
bus = PyCapture2.BusManager()
numCams = bus.getNumOfCameras()
camera = PyCapture2.Camera()
uid = bus.getCameraFromIndex(0)

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



print "Number of cameras detected: ", numCams
if not numCams:
	print "Insufficient number of cameras. Exiting..."
	exit()


camera.connect(uid)
camera.startCapture()

#video loop
while True:
    image = camera.retrieveBuffer()
    row_bytes = float(len(image.getData())) / float(image.getRows());
    cv_image = np.array(image.getData(), dtype="uint8").reshape((image.getRows(), image.getCols()) );
    #keypoints = detector.detect(cv_image)
    #im_with_keypoints = cv2.drawKeypoints(cv_image, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    cv2.imshow("Image", cv_image)
	#ms to wait
    cv2.waitKey(1)
