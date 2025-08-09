import tkinter as tk
from tkinter import ttk
import threading
import time

from utils.HouseManager import HouseManager, load_data  
from utils.AdbProcess import AdbProcess
from utils.Detect import Detect
from task.train import TroopTrainer
from task.explore import Explore
from task.farm import Farm
from task.requirement import Recruitment
# ---------------- GUI ------------------

class AdbApp(tk.Tk):
    def __init__(self, adb_path="adb/adb.exe"):
        super().__init__()
        self.title("Rise of Kingdoms Tool")
        self.geometry("350x700")
        self.resizable(False, False)
        self.iconbitmap("./images/icons/favicon.ico")
        self.configure(bg="#f0f0f0")

        self.adbProcess = AdbProcess(adb_path=adb_path)
        self.home_manager = HouseManager(adb_process=self.adbProcess)
        self.detect = Detect(adb=self.adbProcess)
        self.device_label = tk.Label(self, text="Select Device:")
        self.device_label.pack(pady=5)

        self.device_combo = ttk.Combobox(self, state="readonly", width=40)
        self.device_combo.pack(pady=5)
        self.device_combo.bind("<<ComboboxSelected>>", self.on_device_selected)

        self.refresh_button = tk.Button(self, text="🔄 Refresh Devices", command=self.refresh_devices)
        self.refresh_button.pack(pady=5)

        self.status_label = tk.Label(self, text="", fg="green")
        self.status_label.pack()

        self.tasks = {
            "explore": tk.BooleanVar(),
            "train": tk.BooleanVar(),
            "cave": tk.BooleanVar()
        }
        self.checkbox_explore = tk.Checkbutton(self, text="Dò mây", variable=self.tasks["explore"], command=self.on_task_changed)
        self.checkbox_cave = tk.Checkbutton(self, text="Dò hang", variable=self.tasks["cave"], command=self.on_task_changed)
        self.checkbox_train = tk.Checkbutton(self, text="Huấn luyện lính", variable=self.tasks["train"], command=self.on_task_changed)
        self.checkbox_explore.pack(anchor="w", padx=20)
        self.checkbox_cave.pack(anchor="w", padx=20)
        self.checkbox_train.pack(anchor="w", padx=20)

        self.device_tasks = {}

        self.current_device = None
        self.device_threads = {}

        self.device_paused = {}

        self.pause_button = tk.Button(self, text="⏸ Tạm dừng", command=self.toggle_pause)
        self.pause_button.pack(pady=10)

        self.home_manager_button = tk.Button(self, text="🏠 Quản lý nhà", command=self.open_house_manager)
        self.home_manager_button.pack(pady=10)

        self.train = TroopTrainer(adb_process=self.adbProcess, detect=self.detect, device=self.current_device)
        self.explorer = Explore(adb_process=self.adbProcess, detect=self.detect)
        self.task_farm = Farm(adb_process=self.adbProcess, detect=self.detect)
        self.task_recruitment = Recruitment(adb_process=self.adbProcess, detect=self.detect)

        self.refresh_devices()
    def open_house_manager(self):
        house_manager = HouseManager(parent=self, adb_process=self.adbProcess, device_id=self.current_device)
        house_manager.run()
    def refresh_devices(self):
        devices = self.adbProcess.get_connected_devices()
        if not devices:
            self.device_combo['values'] = []
            self.device_combo.set("")
            self.status_label.config(text="⚠️ No devices found.", fg="red")
        else:
            # check start with 127.0.0.1 and remove it
            devices = [d for d in devices if not d.startswith("127.0.0.1")]
            if not devices:
                self.device_combo['values'] = []
                self.device_combo.set("")
                self.status_label.config(text="⚠️ No valid devices found.", fg="red")
                return
            self.device_combo['values'] = devices
            self.device_combo.current(0)
            self.status_label.config(text=f"✔ Found {len(devices)} device(s).", fg="green")
            self.on_device_selected()

    def toggle_pause(self):
        device = self.current_device
        if not device:
            return
        paused = self.device_paused.get(device, False)
        self.device_paused[device] = not paused
        if self.device_paused[device]:
            self.pause_button.config(text="▶️ Bắt đầu")
        else:
            self.pause_button.config(text="⏸ Tạm dừng")
            self.on_task_changed()

    def on_device_selected(self, event=None):
        if self.current_device:
            self.device_tasks[self.current_device] = {task: var.get() for task, var in self.tasks.items()}

        device = self.device_combo.get()
        self.current_device = device

        if device in self.device_tasks:
            for task, var in self.tasks.items():
                var.set(self.device_tasks[device].get(task, False))
        else:
            for var in self.tasks.values():
                var.set(False)
        paused = self.device_paused.get(self.current_device, False)
        if paused:
            self.pause_button.config(text="▶️ Bắt đầu")
        else:
            self.pause_button.config(text="⏸ Tạm dừng")

    # def on_task_changed(self):
    #     device = self.current_device
    #     if device:
    #         self.device_tasks[device] = {task: var.get() for task, var in self.tasks.items()}
    #         for task, enabled in self.device_tasks[device].items():
    #             if enabled and (device, task) not in self.device_threads and not self.device_paused.get(device, False):
    #                 t = threading.Thread(target=self.run_task, args=(device, task), daemon=True)
    #                 self.device_threads[(device, task)] = t
    #                 t.start()
    #             elif not enabled and (device, task) in self.device_threads:
    #                 del self.device_threads[(device, task)]
    # def run_task(self, device, task):
    #     while self.device_tasks.get(device, {}).get(task, False):
    #         if self.device_paused.get(device, False):
    #             time.sleep(0.5)
    #             continue
    #         self.train.device = device
    #         self.train.houses = load_data().get(device, {}).get("houses", [])
    #         img = self.process.capture(device)
    #         print(f"Running task {task}")
    #         if task == "train":
    #             template = cv2.imread("images/train_xe_1.png", cv2.IMREAD_COLOR)
    #             if template is None:
    #                 print(f"[LỖI] Không đọc được template: {template}")
    #                 return False
    #             existed_xe = self.detect.check_object_exists(image=img, template=template)
    #             if existed_xe:
    #                 self.train.train_xe_phong() 
    #     print(f"Task {task} trên thiết bị {device} đã dừng.")

    def on_task_changed(self):
        device = self.current_device
        if device:
            self.device_tasks[device] = {task: var.get() for task, var in self.tasks.items()}

            if device not in self.device_threads and not self.device_paused.get(device, False):
                t = threading.Thread(target=self.run_device_tasks, args=(device,), daemon=True)
                self.device_threads[device] = t
                t.start()

    def run_device_tasks(self, device):
        while any(self.device_tasks.get(device, {}).values()):
            if self.device_paused.get(device, False):
                time.sleep(0.5)
                continue
            self.train.device = device
            houses = load_data().get(device, {}).get("houses", [])
            self.train.houses = houses
            self.task_farm.device_id = device
            img = self.adbProcess.capture(device)
            disconnected_pos = self.detect.find_object_position(img, "./images/disconnected.png")
            if disconnected_pos:
                self.adbProcess.tap(device, 638, 471)

            pos = self.detect.find_object_directory(img, "./images/always_check")
            if pos:
                self.adbProcess.tap(device, *pos)
            # farm_pos = self.detect.find_object_position(img, "./images/AllArmies.png")
            # if farm_pos is None:
            #     self.task_farm.perform_action_farm()
            
            self.task_recruitment.houses = houses
            self.task_recruitment.device_id = device
            self.task_recruitment.perform_action_requirement(img)
            
            
            for task, enabled in self.device_tasks[device].items():
                if not enabled:
                    continue
                if task == "train":
                    self.train.auto_train_units(img)
                elif task == "explore":
                    if self.detect.check_object_exists_directory(img, "./images/explore_check"):
                        coord = next((h for h in houses if h["name"] == "Trinh sát"), None)
                        if coord:
                            pos_tap = (coord["x"], coord["y"])
                            self.explorer.tap_point = pos_tap
                        else:
                            print("❌ Không tìm thấy tọa độ Trinh sát, không thể dò mây.")
                            continue
                        self.explorer.device_id = device
                        self.explorer.perform_action_sequence()
                elif task == "cave":
                    if self.detect.check_object_exists_directory(img, "./images/explore_check"):
                        coord = next((h for h in houses if h["name"] == "Trinh sát"), None)
                        if coord:
                            pos_tap = (coord["x"], coord["y"])
                            self.explorer.tap_point = pos_tap
                        else:
                            print("❌ Không tìm thấy tọa độ Dò hang, không thể dò hang.")
                            continue
                        self.explorer.device_id = device
                        self.explorer.perform_action_cave_probe()
            time.sleep(1)
        print(f"Tất cả task trên thiết bị {device} đã dừng.")
        del self.device_threads[device]

# ---- Chạy ứng dụng GUI ----
if __name__ == "__main__":
    app = AdbApp(adb_path="adb/adb.exe")
    app.mainloop()
