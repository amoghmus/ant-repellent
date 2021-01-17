import time
import picamera
import datetime
import argparse
import cv2

IMAGE_DIR = '/home/pi/ant_images'
NUM_OF_PIC = 40 
SLEEP_TIME = 60 


if __name__ == '__main__':
    # Solution used for experiment
    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--solution", required=True, help="path to the image file")
    args = vars(ap.parse_args())

    # Take pictures at certain intervals
    with picamera.PiCamera() as camera:
        for ii in range(0, NUM_OF_PIC):
             filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")+".jpeg"
             # camera.resolution = (256, 256)
             camera.resolution = (1920, 1080)
             # camera.resolution = (2592, 1944)
             camera.start_preview()
             # camera.capture('/home/pi/images/image_{}.jpg'.format(ii))
             image_path = IMAGE_DIR + '/' + args['solution'] + '/' + filename
             camera.capture(image_path)
             time.sleep(SLEEP_TIME)

