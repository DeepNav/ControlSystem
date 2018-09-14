import csv
import os

class DataLogger(object):
    def __init__(self, file_name="default.csv"):
        self.unflushed_write_count = 0
        self.file_name = file_name
        self.spliter = "\n"
        self.log_file = open(file_name, "a+")
        self.column_names = [
            "timestamp",
            "lat",
            "lng",
            "alt",
            "ground_speed",
            "heading",
            "lidar_distance",
            "acc_x",
            "acc_y",
            "acc_z",
            "ang_x",
            "ang_y",
            "ang_z",
            "mag_x",
            "mag_y",
            "mag_z",
            "compass_bearing",
            "pitch_angle",
            "roll_angle",
            "water_speed_forward",
            "water_speed_backward",
            "water_speed_left",
            "water_speed_right",
            "wind_direction",
            "wind_speed",
            "is_manual_mode",
            "is_cruise_mode",
            "direction",
            "throttle",
            ]
        self.writer = csv.DictWriter(self.log_file, self.column_names)
        self.writer.writeheader()

    def write(self, data_chunk):
        self.writer.writerow(data_chunk)
        self.unflushed_write_count += 1
        if self.unflushed_write_count >= 20:
            self.log_file.flush()
            os.fsync(self.log_file.fileno())
    
    def __del__(self):
        self.log_file.close()
