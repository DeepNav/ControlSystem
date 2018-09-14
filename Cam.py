import cv2
import os
class Cam(object):
    def __init__(self, cam_id = 1, path_to_save = ""):
        self.cap = cv2.VideoCapture(cam_id)
        self.path_to_save = path_to_save
    def capture_and_mark(self, ts):
        ret, frame = self.cap.read()
        cv2.imwrite(os.path.join(self.path_to_save, str(ts) + ".png"), frame)