import os, time

from Cam import Cam

def get_image_file_name ():
    return ('%.6f' % time.time()) + ".jpg"

cam = Cam(1, os.getcwd())
cam.capture_and_mark(get_image_file_name())

start_time = time.time()
for i in xrange(10):
    cam.capture_and_mark(get_image_file_name())
print("taking " + str(time.time() - start_time) + "s to take 10 pics")