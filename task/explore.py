import time

from utils.AdbProcess import AdbProcess
from utils.Detect import Detect

ACTION_IMAGES = [
    "./images/dotham_1.png",
    "./images/dotham_2.png",
    "./images/dotham_3.png",
    "./images/send.png",
    "./images/goback.png"
]

ACTION_IMAGES_CAVE_EXPLORE = [
    "./images/dotham_2.png",
    "./images/dotham_3.png",
    "./images/send.png",
    "./images/goback.png"
]

ACTION_IMAGES_CAVE_PROBE = [
    "./images/cave_probe_4.png",
    "./images/send.png",
    "./images/goback.png"
]

class Explore:
    def __init__(self, adb_process: AdbProcess, detect: Detect, device_id=None, houses=None):
        """
        :param adb_process: Instance of AdbProcess to interact with the device.
        :param device_id: ID of the device to perform actions on.
        :param detect: Instance of Detect to find objects on the screen.
        """
        self.detect = detect
        self.adb_process = adb_process
        self.device_id = device_id
        self.houses = houses or []

    def _tap_by_template_list(self, image_list: list):
        """Dò tìm và tap theo danh sách ảnh template."""
        for idx, image_path in enumerate(image_list, start=1):
            pos = self.detect.wait_until_found(self.device_id, image_path)
            if pos:
                self.adb_process.tap(self.device_id, *pos)
                time.sleep(0.3)
            else:
                return

    def perform_action_sequence(self):
        coord = next((h for h in self.houses if h["name"] == "Trinh sát"), None)
        if coord:
            pos_tap = (coord["x"], coord["y"])
            self.adb_process.tap(self.device_id, *pos_tap)
        else:
            print("❌ Không tìm thấy tọa độ Trinh sát, không thể dò mây.")
            return
        time.sleep(0.5)
        self._tap_by_template_list(ACTION_IMAGES)
        time.sleep(0.85)

    def perform_action_cave_probe(self):
        coord = next((h for h in self.houses if h["name"] == "Trinh sát"), None)
        if coord:
            pos_tap = (coord["x"], coord["y"])
            self.adb_process.tap(self.device_id, *pos_tap)
        else:
            print("❌ Không tìm thấy tọa độ Trinh sát, không thể dò mây.")
            return
        time.sleep(0.5)

        cave_probe_pos = self.detect.wait_until_found(self.device_id, "./images/dotham_1.png")
        if cave_probe_pos:
            self.adb_process.tap(self.device_id, *cave_probe_pos)
        else:
            print("❌ Không tìm thấy dotham_1.png")
            return

        # Tap vào 2 tọa độ cố định (nếu cần, bạn có thể tìm template thay vì hardcode)
        self.adb_process.tap(self.device_id, 750, 212)  # CAVE_PROBE 2
        time.sleep(0.85)
        self.adb_process.tap(self.device_id, 993, 605)  # CAVE_PROBE 3
        time.sleep(0.85)

        # Thực hiện các bước còn lại
        self._tap_by_template_list(ACTION_IMAGES_CAVE_PROBE)
        time.sleep(0.85)

    def perform_action_explore_and_cave_probe(self):
        coord = next((h for h in self.houses if h["name"] == "Trinh sát"), None)
        if coord:
            pos_tap = (coord["x"], coord["y"])
            self.adb_process.tap(self.device_id, *pos_tap)
        else:
            print("❌ Không tìm thấy tọa độ Trinh sát, không thể dò mây.")
            return
        time.sleep(0.5)

        cave_probe_pos = self.detect.wait_until_found(self.device_id, "./images/dotham_1.png")
        if cave_probe_pos:
            self.adb_process.tap(self.device_id, *cave_probe_pos)
        else:
            print("❌ Không tìm thấy dotham_1.png")
            return
        time.sleep(0.8)
        cave_explore_pos = self.detect.wait_until_found(self.device_id, "./images/cave_explore.png",timeout=5, threshold=0.98)
        img = self.adb_process.capture(self.device_id)
        cave_d2_pos = self.detect.find_object_position(img, "./images/d2.png", threshold=0.99)
        if cave_explore_pos and cave_d2_pos == None:
            # Tap vào 2 tọa độ cố định (nếu cần, bạn có thể tìm template thay vì hardcode)
            self.adb_process.tap(self.device_id, 750, 212)  # CAVE_PROBE 2
            time.sleep(0.85)
            self.adb_process.tap(self.device_id, 993, 605)  # CAVE_PROBE 3
            time.sleep(0.85)

            # Thực hiện các bước còn lại
            self._tap_by_template_list(ACTION_IMAGES_CAVE_PROBE)
            time.sleep(0.85)
        else:
            self._tap_by_template_list(ACTION_IMAGES_CAVE_EXPLORE)
            time.sleep(0.85)
