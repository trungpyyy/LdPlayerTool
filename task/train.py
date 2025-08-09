import time
import cv2
from utils import AdbProcess, Detect

class TroopTrainer:
    def __init__(self, adb_process: AdbProcess, detect: Detect, device, houses=None):
        self.adbProcess = adb_process
        self.detect = detect
        self.device = device
        self.houses = houses or []

    def _tap_twice(self, pos: tuple):
        self.adbProcess.tap(self.device, *pos)
        time.sleep(0.8)
        self.adbProcess.tap(self.device, *pos)

    def _tap_template_and_train(self, template_path: str):
        pos_tap = self.detect.wait_until_found(self.device, template=template_path, timeout=10)
        if pos_tap:
            self.adbProcess.tap(self.device, *pos_tap)
        time.sleep(0.5)
        self.adbProcess.tap(self.device, 985, 592)  # Tap on "Train" button
        time.sleep(0.5)

    def _train_unit(self, house_name: str, template_path: str, label: str):
        coords = next((h for h in self.houses if h["name"] == house_name), None)
        if coords:
            print(f"Training {label}...")
            pos = (coords["x"], coords["y"])
            self._tap_twice(pos)
            self._tap_template_and_train(template_path)
        else:
            print(f"Chưa có tọa độ cho {house_name}.")

    def train_bo_binh(self):
        self._train_unit("Doanh trại", "./images/train_bo_binh_3.png", "Doanh trại")

    def train_ky_binh(self):
        self._train_unit("Chuồng ngựa", "./images/train_ky_binh_3.png", "Kỵ Binh")

    def train_cung(self):
        self._train_unit("Trường bắn", "./images/train_cung_3.png", "Cung Pháp")

    def train_xe_phong(self):
        self._train_unit("Nhà xe", "./images/train_xe_3.png", "Xe Phóng")

    def auto_train_units(self, img):
        """Tự động huấn luyện các đơn vị nếu template tương ứng xuất hiện trong ảnh chụp."""

        unit_templates = [
            {
                "name": "Xe Phóng",
                "template_path": "images/train/xe",
                "train_func": self.train_xe_phong
            },
            {
                "name": "Kỵ Binh",
                "template_path": "images/train/ky",
                "train_func": self.train_ky_binh
            },
            {
                "name": "Bộ Binh",
                "template_path": "images/train/bo",
                "train_func": self.train_bo_binh
            },
            {
                "name": "Cung Pháp",
                "template_path": "images/train/cung",
                "train_func": self.train_cung
            }
        ]

        for unit in unit_templates:
            existed = self.detect.check_object_exists_directory(image=img, template_dir=unit["template_path"])
            if existed:
                print(f"Phát hiện {unit['name']} — bắt đầu huấn luyện.")
                unit["train_func"]()