# import the necessary packages
from os import walk
from imutils import contours
from skimage import measure
import numpy as np
import time
import picamera
import datetime
import argparse
import imutils
import cv2
import sqlite3
import re    

IMAGE_DIR = '/home/pi/ant_images'
DB_TABLE = '/home/pi/bins/ants.db'
SLEEP_TIME = 2

NUM_PIX = 100
GRAY_2ND_ARG = 50
RADIUS_MAX = 100 
RADIUS_MIN = 15 

def count_ants(image):
    print("reading image: {}".format(image))
    image = cv2.imread(image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # blurred = cv2.GaussianBlur(gray, (11, 11), 0)

    thresh = cv2.threshold(gray, GRAY_2ND_ARG, 255, cv2.THRESH_BINARY_INV)[1]
    #thresh = cv2.threshold(blurred, 80, 255, cv2.THRESH_BINARY_INV)[1]
    
    # perform a series of erosions and dilations to remove
    # any small blobs of noise from the thresholded image
    thresh = cv2.erode(thresh, None, iterations=2)
    thresh = cv2.dilate(thresh, None, iterations=4)

    # perform a connected component analysis on the thresholded
    # image, then initialize a mask to store only the "large" components
    labels = measure.label(thresh, neighbors=8, background=0)
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
        if numPixels > NUM_PIX:
            mask = cv2.add(mask, labelMask)
    
    # find the contours in the mask, then sort them from left to
    # right
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    try:
        cnts = contours.sort_contours(cnts)[0]
    except Exception as e:
        print("Sort_contours error: {}".format(e))
        return

    circle_count = 0
    # loop over the contours
    for (i, c) in enumerate(cnts):
        # draw the bright spot on the image
        (x, y, w, h) = cv2.boundingRect(c)
        ((cX, cY), radius) = cv2.minEnclosingCircle(c)
        print("radius:{}".format(radius))
        if radius > RADIUS_MAX or radius < RADIUS_MIN:
            continue
        circle_count += 1
    
        cv2.circle(image, (int(cX), int(cY)), int(radius),
            (0, 0, 255), 3)
        cv2.putText(image, "#{}".format(i + 1), (x, y - 15),
        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
     
    print('Contours {}'.format(circle_count))
    # show the output image
    # cv2.imshow("Image", image)
    # cv2.waitKey(0)
    return circle_count


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return None


def create_ant_count(conn, row):
    sql = 'INSERT INTO ants(solution, image, ants_count) VALUES(?,?,?)'
    cur = conn.cursor()
    cur.execute(sql, row)
    conn.commit()
    return cur.lastrowid


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--solution", required=True, help="path to the image file")
    args = vars(ap.parse_args())

    # Open database
    conn = create_connection(DB_TABLE)

    # Loop through images, counts ants and upload to database 
    for (dirpath, dirname, images) in walk(IMAGE_DIR): 
        print('dirpath: {} dirname: {}, images: {}'.format(dirpath, dirname, images))
        pattern = re.compile(args["solution"])
        # if dirpath != args['solution']:
        m = pattern.search(dirpath) 
        if m is None:
            continue
        images.sort()
        for img in images:
            fp_img = dirpath + '/' + img
            print('Image path: {} from dir: {}'.format(fp_img, dirname)) 
            ct = count_ants(fp_img)
            row = (args['solution'], fp_img, ct)
            row_id = create_ant_count(conn, row)
            time.sleep(SLEEP_TIME)

