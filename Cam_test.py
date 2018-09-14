import os, time

from Cam import Cam

cam = Cam(1, os.getcwd())
cam.capture_and_mark(time.time())

start_time = time.time()
for i in xrange(10):
    cam.capture_and_mark(time.time())
print("taking " + str(time.time() - start_time) + "s to take 10 pics")