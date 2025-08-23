import os
import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import cv2

# --- Cấu hình ---
DATA_FILE = "data/houses.json"

HOUSE_TYPES = [
    "Trinh sát",
    "Doanh trại",
    "Chuồng ngựa",
    "Trường bắn",
    "Nhà xe",
    "Nhà tuyển dụng",
    "Xây dựng"
]

# --- Hàm xử lý file JSON ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- Mở ảnh bằng OpenCV để lấy tọa độ ---
def open_image_and_get_coords(img, window_name="Chọn tọa độ"):

    coords = []

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            coords.append((x, y))
            cv2.destroyWindow(window_name)

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, img.shape[1], img.shape[0])  # width, height
    cv2.setMouseCallback(window_name, click_event)
    cv2.imshow(window_name, img)


    while not coords:
        if cv2.waitKey(10) == 27:
            break

    return coords[0] if coords else (None, None)

# --- Giao diện chính ---
class HouseManager(tk.Toplevel):
    def __init__(self, parent=None, adb_process=None, device_id=None):
        super().__init__(parent)
        self.withdraw()
        self.title("Ghi tọa độ nhà")
        self.geometry("400x300")

        self.data = load_data()
        self.device_id = device_id
        self.adb_process = adb_process

        self.coord_labels = {}

        ttk.Label(self, text="Danh sách nhà và tọa độ:").pack(pady=10)

        self.table_frame = tk.Frame(self)
        self.table_frame.pack(pady=5)

        self.build_table()
        self.update_display()
    def run(self):
        self.deiconify()
        self.lift()
        self.focus_force()
    def build_table(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        for i, name in enumerate(HOUSE_TYPES):
            # Tên nhà
            tk.Label(self.table_frame, text=name, width=15, anchor="w").grid(row=i, column=0, padx=5, pady=3)

            # Nhãn tọa độ
            coord_label = tk.Label(self.table_frame, text="(chưa có)", width=15)
            coord_label.grid(row=i, column=1, padx=5)
            self.coord_labels[name] = coord_label

            # Nút chọn tọa độ từ ảnh
            btn = ttk.Button(self.table_frame, text="Chọn từ ảnh", command=lambda n=name: self.pick_coords(n))
            btn.grid(row=i, column=2, padx=5)

    def update_display(self):
        house_data = self.data.get(self.device_id, {}).get("houses", [])
        house_map = {h["name"]: (h["x"], h["y"]) for h in house_data}

        for name in HOUSE_TYPES:
            if name in house_map:
                x, y = house_map[name]
                self.coord_labels[name].config(text=f"({x}, {y})")
            else:
                self.coord_labels[name].config(text="(chưa có)")

    def pick_coords(self, house_name):

        x, y = open_image_and_get_coords(self.adb_process.capture(self.device_id), window_name=f"Chọn tọa độ cho {house_name}")
        if x is None or y is None:
            messagebox.showwarning("Không có tọa độ", "Bạn chưa chọn vị trí nào.")
            return

        house = {"name": house_name, "x": x, "y": y}

        if self.device_id not in self.data:
            self.data[self.device_id] = {"houses": [], "last_updated": ""}

        updated = False
        for h in self.data[self.device_id]["houses"]:
            if h["name"] == house_name:
                h["x"] = x
                h["y"] = y
                updated = True
                break

        if not updated:
            self.data[self.device_id]["houses"].append(house)

        self.data[self.device_id]["last_updated"] = datetime.now().isoformat()
        save_data(self.data)
        self.update_display()
        self.data = load_data()
