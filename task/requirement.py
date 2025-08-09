import time

from utils.AdbProcess import AdbProcess
from utils.Detect import Detect

class Recruitment:
    def __init__(self, adb_process: AdbProcess, detect: Detect, device_id=None, houses=None):
        self.adb_process = adb_process
        self.detect = detect
        self.device_id = device_id
        self.houses = houses or []
    
    def perform_action_requirement(self, img):
        requirement_pos = self.detect.find_object_position(img, "./images/recruitment/recruitment_1.png")
        if requirement_pos:
            coords = next((h for h in self.houses if h["name"] == "Nhà tuyển dụng"), None)
            if coords:
                pos = (coords["x"], coords["y"])
                self.adb_process.tap(self.device_id, *pos)
                time.sleep(0.5)
                self.adb_process.tap(self.device_id, *self.detect.wait_until_found(self.device_id, "./images/recruitment/recruitment_2.png"))
                time.sleep(0.5)
                self.adb_process.tap(self.device_id, *self.detect.wait_until_found(self.device_id, "./images/recruitment/open.png"))
                time.sleep(2)
                confirm_1 = self.detect.wait_until_found(self.device_id, "./images/recruitment/confirm_1.png")
                if confirm_1:
                    self.adb_process.tap(self.device_id, *confirm_1)
                time.sleep(0.5)
                confirm_2 = self.detect.wait_until_found(self.device_id, "./images/recruitment/confirm_2.png")
                if confirm_2:
                    self.adb_process.tap(self.device_id, *confirm_2)
                time.sleep(0.5)
                self.adb_process.tap(self.device_id, *self.detect.wait_until_found(self.device_id, "./images/always_check/back.png"))
                
        else:
            pass