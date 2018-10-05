import cv2
import os
import errno

class Cam(object):
    def __init__(self, cam_id = 1, path_to_save = ""):
        self.cap = cv2.VideoCapture(cam_id)
        self.path_to_save = path_to_save
        if not os.path.exists(os.path.dirname(path_to_save)):
            try:
                os.makedirs(os.path.dirname(path_to_save))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
    def capture_and_mark(self, image_file_name):
        ret, frame = self.cap.read()
        cv2.imwrite(os.path.join(self.path_to_save, image_file_name), frame)