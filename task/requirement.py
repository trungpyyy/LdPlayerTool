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
        requirement_pos = self.detect.find_object_directory(img, "./images/recruitment/check")
        if not requirement_pos:
            return

        coords = next((h for h in self.houses if h["name"] == "Nhà tuyển dụng"), None)
        if not coords:
            return

        self.adb_process.tap(self.device_id, coords["x"], coords["y"])
        time.sleep(0.5)

        pos = self.detect.wait_until_found(self.device_id, "./images/recruitment/recruitment_2.png")
        if pos:
            self.adb_process.tap(self.device_id, *pos)
        else:
            return
        time.sleep(0.5)

        # open
        pos = self.detect.wait_until_found(self.device_id, "./images/recruitment/open.png")
        if pos:
            self.adb_process.tap(self.device_id, *pos)
        else:
            return
        time.sleep(2)

        # confirm_1
        pos = self.detect.wait_until_found(self.device_id, "./images/recruitment/confirm_1.png")
        if pos:
            self.adb_process.tap(self.device_id, *pos)
            time.sleep(0.5)

        # confirm_2
        pos = self.detect.wait_until_found(self.device_id, "./images/recruitment/confirm_2.png")
        if pos:
            self.adb_process.tap(self.device_id, *pos)
            time.sleep(0.5)

        # back
        pos = self.detect.wait_until_found(self.device_id, "./images/always_check/back.png")
        if pos:
            self.adb_process.tap(self.device_id, *pos)
        time.sleep(1)
