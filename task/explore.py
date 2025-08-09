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

ACTION_IMAGES_CAVE_PROBE = [
    "./images/cave_probe_4.png",
    "./images/send.png",
    "./images/goback.png"
]

class Explore:
    def __init__(self, adb_process: AdbProcess, detect: Detect, device_id=None, tap_point=None):
        """
        :param adb_process: Instance of AdbProcess to interact with the device.
        :param device_id: ID of the device to perform actions on.
        :param detect: Instance of Detect to find objects on the screen.
        :param tap_point: Optional tuple (x, y) to specify a tap point.
        """
        self.detect = detect
        self.adb_process = adb_process
        self.device_id = device_id
        self.tap_point = tap_point  # ✅ Fix: phải gán giá trị vào

    def _tap_by_template_list(self, image_list: list):
        """Dò tìm và tap theo danh sách ảnh template."""
        for idx, image_path in enumerate(image_list, start=1):
            pos = self.detect.wait_until_found(self.device_id, image_path)
            if pos:
                self.adb_process.tap(self.device_id, *pos)
                time.sleep(0.3)
            else:
                break

    def perform_action_sequence(self):
        if self.tap_point is None:
            print("❌ No tap point selected, skipping action sequence.")
            return
        self.adb_process.tap(self.device_id, *self.tap_point)
        time.sleep(0.5)
        self._tap_by_template_list(ACTION_IMAGES)
        time.sleep(0.85)

    def perform_action_cave_probe(self):
        if self.tap_point is None:
            print("❌ No tap point selected, skipping cave probe sequence.")
            return
        self.adb_process.tap(self.device_id, *self.tap_point)
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
