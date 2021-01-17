import time
import picamera
import datetime

# Accept repellent name
# Loop on take_pics every 1 min

def take_pics():
     with picamera.PiCamera() as camera:
         # Create datetime stamp formatted 3let_repllent_YYYYMMDD_HHMMSS.jpeg
         # lim_20190224_1721919.jpb
         for ii in range(2019021731, 2019021736):
              # camera.resolution = (256, 256)
              camera.resolution = (1920, 1080)
              # camera.resolution = (2592, 1944)
              camera.start_preview()
              time.sleep(5)
              # camera.capture('/home/pi/images/image_{}.jpg'.format(ii))
              camera.capture('/home/pi/images/image_{}.jpeg'.format(ii))
  
if __name__ == '__main__':
     take_pics()
