import time
import picamera
import datetime

# import the necessary packages
from imutils import contours
from skimage import measure
import numpy as np
import argparse
import imutils
import cv2
# Accept repellent name
# Loop on take_pics every 1 min

IMAGE_DIR = '/home/pi/images'

def cnt_ants(image):
	# construct the argument parse and parse the arguments
	#ap = argparse.ArgumentParser()
	#ap.add_argument("-i", "--image", required=True,
	#            help="path to the image file")
	#args = vars(ap.parse_args())
	
	# load the image, convert it to grayscale, and blur it
	image = cv2.imread(image)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	blurred = cv2.GaussianBlur(gray, (11, 11), 0)
	
	# threshold the image to reveal light regions in the
	# blurred image
	thresh = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY_INV)[1]
	#thresh = cv2.threshold(blurred, 80, 255, cv2.THRESH_BINARY_INV)[1]
	
	# perform a series of erosions and dilations to remove
	# any small blobs of noise from the thresholded image
	thresh = cv2.erode(thresh, None, iterations=2)
	thresh = cv2.dilate(thresh, None, iterations=4)
	
	# perform a connected component analysis on the thresholded
	# image, then initialize a mask to store only the "large"
	# components
	labels = measure.label(thresh, neighbors=8, background=0)
	print("labels count: {}".format(len(labels)))
	mask = np.zeros(thresh.shape, dtype="uint8")
	 
	# loop over the unique components
	for label in np.unique(labels):
	    # if this is the background label, ignore it
	    if label == 0:
	        continue
	
	    # otherwise, construct the label mask and count the
	    # number of pixels 
	    labelMask = np.zeros(thresh.shape, dtype="uint8")
	    labelMask[labels == label] = 255
	    numPixels = cv2.countNonZero(labelMask)
	
	    # if the number of pixels in the component is sufficiently
	    # large, then add it to our mask of "large blobs"
	    if numPixels > 100:
	        mask = cv2.add(mask, labelMask)
	
	# find the contours in the mask, then sort them from left to
	# right
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0] if imutils.is_cv2() else cnts[1]
	cnts = contours.sort_contours(cnts)[0]
	
	circle_count = 0
	# loop over the contours
	for (i, c) in enumerate(cnts):
	    # draw the bright spot on the image
	    (x, y, w, h) = cv2.boundingRect(c)
	    ((cX, cY), radius) = cv2.minEnclosingCircle(c)
	    print("radius:{}".format(radius))
	    if radius > 100 or radius < 14:
	        continue
	    circle_count += 1
	
	    cv2.circle(image, (int(cX), int(cY)), int(radius),
	        (0, 0, 255), 3)
	    cv2.putText(image, "#{}".format(i + 1), (x, y - 15),
	    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
	 
	print('Contours {}'.format(circle_count))
	# show the output image
	cv2.imshow("Image", image)
	cv2.waitKey(0)
	# time.sleep(5)

def take_pics():
     with picamera.PiCamera() as camera:
         for ii in range(1,3):
              filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")+".jpeg"
              # camera.resolution = (256, 256)
              camera.resolution = (1920, 1080)
              # camera.resolution = (2592, 1944)
              camera.start_preview()
              # camera.capture('/home/pi/images/image_{}.jpg'.format(ii))
              image_path = IMAGE_DIR + '/' + filename
              camera.capture(image_path)
              print("PiCamera capture returned")

              time.sleep(3)
              cnt_ants(image_path)

if __name__ == '__main__':
     take_pics()
