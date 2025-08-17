import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import logging
import traceback
import os
from datetime import datetime

import cv2

import config
from utils.HouseManager import HouseManager, load_data  
from utils.AdbProcess import AdbProcess
from utils.Detect import Detect
from task.train import TroopTrainer
from task.explore import Explore
from task.farm import Farm
from task.requirement import Recruitment

# ---------------- LOGGING SETUP ------------------
def setup_logging():
    """Setup logging configuration with file and console output"""
    # Create logs directory if it doesn't exist
    if not os.path.exists(config.LOG_DIRECTORY):
        os.makedirs(config.LOG_DIRECTORY)
    
    # Configure logging
    log_filename = f'{config.LOG_DIRECTORY}/{config.LOG_FILENAME_PREFIX}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    
    # Convert string log level to logging constant
    log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format=config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# ---------------- GUI ------------------

class AdbApp(tk.Tk):
    def __init__(self, adb_path="adb/adb.exe"):
        try:
            super().__init__()
            self.title(config.WINDOW_TITLE)
            self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
            self.resizable(False, False)
            
            # Try to set icon, but don't crash if it fails
            try:
                self.iconbitmap("./images/icons/favicon.ico")
            except Exception as e:
                logger.warning(f"Could not load icon: {e}")
            
            self.configure(bg=config.WINDOW_BACKGROUND)
            
            # Initialize components with error handling
            self._init_components(adb_path)
            self._init_ui()
            
            logger.info("AdbApp initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AdbApp: {e}")
            logger.error(traceback.format_exc())
            messagebox.showerror("Initialization Error", f"Failed to start application: {e}")
            raise

    def _init_components(self, adb_path):
        """Initialize core components with error handling"""
        try:
            self.adbProcess = AdbProcess(adb_path=adb_path)
            self.home_manager = HouseManager(adb_process=self.adbProcess)
            self.device_tasks = {}
            self.current_device = None
            self.device_threads = {}
            self.device_paused = {}
            self.farm_priority = {}
            self.current_farm_index = {}
            logger.info("Core components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize core components: {e}")
            raise

    def _init_ui(self):
        """Initialize UI components with error handling"""
        try:
            # Device selection
            self.device_label = tk.Label(self, text="Select Device:")
            self.device_label.pack(pady=5)

            self.device_combo = ttk.Combobox(self, state="readonly", width=40)
            self.device_combo.pack(pady=5)
            self.device_combo.bind("<<ComboboxSelected>>", self.on_device_selected)

            self.refresh_button = tk.Button(self, text="🔄 Refresh Devices", command=self.refresh_devices)
            self.refresh_button.pack(pady=5)

            self.status_label = tk.Label(self, text="", fg="green")
            self.status_label.pack()

            # Task checkboxes
            self.tasks = {
                "farm": tk.BooleanVar(),
                "explore": tk.BooleanVar(),
                "train": tk.BooleanVar(),
                "cave": tk.BooleanVar(),
                "food": tk.BooleanVar(),
                "wood": tk.BooleanVar(),
                "stone": tk.BooleanVar(),
                "gold": tk.BooleanVar(),
                "army_count": tk.IntVar(value=1),
            }
            self.checkbox_farm = tk.Checkbutton(self, text="Thu hoạch", variable=self.tasks["farm"], command=self.on_task_changed)
            self.checkbox_explore = tk.Checkbutton(self, text="Dò mây", variable=self.tasks["explore"], command=self.on_task_changed)
            self.checkbox_cave = tk.Checkbutton(self, text="Dò hang", variable=self.tasks["cave"], command=self.on_task_changed)
            self.checkbox_train = tk.Checkbutton(self, text="Huấn luyện lính", variable=self.tasks["train"], command=self.on_task_changed)
            """UI with 
            Thu hoạch
            Food Wood Stone Gold
            """
            self.checkbox_farm.pack(anchor="w", padx=20)
            resources_frame = tk.Frame(self)
            resources_frame.pack(anchor="w", padx=20)

            # Create resource checkboxes with resources_frame as parent
            self.checkbox_food = tk.Checkbutton(resources_frame, text="Food", variable=self.tasks["food"], command=self.on_task_changed)
            self.checkbox_wood = tk.Checkbutton(resources_frame, text="Wood", variable=self.tasks["wood"], command=self.on_task_changed)
            self.checkbox_stone = tk.Checkbutton(resources_frame, text="Stone", variable=self.tasks["stone"], command=self.on_task_changed)
            self.checkbox_gold = tk.Checkbutton(resources_frame, text="Gold", variable=self.tasks["gold"], command=self.on_task_changed)
            # spin task 1-5 with self.tasks["army_count"]
            self.spin = tk.Spinbox(from_=1, to=5,
                    font=("Arial", 14),
                    textvariable=self.tasks["army_count"],
                    width=5)
            self.spin.bind("<Return>", self.on_task_changed)
            self.spin.pack(padx=20, pady=5)
            self.checkbox_food.pack(side="left", padx=20)
            self.checkbox_wood.pack(side="left", padx=5)
            self.checkbox_stone.pack(side="left", padx=5)
            self.checkbox_gold.pack(side="left", padx=5)
            self.checkbox_explore.pack(anchor="w", padx=20)
            self.checkbox_cave.pack(anchor="w", padx=20)
            self.checkbox_train.pack(anchor="w", padx=20)

            # Control buttons
            self.pause_button = tk.Button(self, text="⏸ Tạm dừng", command=self.toggle_pause)
            self.pause_button.pack(pady=10)

            self.home_manager_button = tk.Button(self, text="🏠 Quản lý nhà", command=self.open_house_manager)
            self.home_manager_button.pack(pady=10)

            # Log display
            self.log_text = tk.Text(self, height=config.LOG_DISPLAY_HEIGHT, width=config.LOG_DISPLAY_WIDTH)
            self.log_text.pack(pady=5, padx=10)
            
            # Scrollbar for log
            scrollbar = tk.Scrollbar(self, command=self.log_text.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.log_text.config(yscrollcommand=scrollbar.set)

            logger.info("UI components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize UI: {e}")
            logger.error(traceback.format_exc())
            raise

    def log_message(self, message, level="INFO"):
        """Add message to log display and logging system"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {level}: {message}\n"
            
            # Add to GUI log display
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)
            
            # Limit log display size
            if self.log_text.index(tk.END).split('.')[0] > str(config.MAX_LOG_ENTRIES):
                self.log_text.delete('1.0', '2.0')
            
            # Add to file logging
            if level == "ERROR":
                logger.error(message)
            elif level == "WARNING":
                logger.warning(message)
            else:
                logger.info(message)
                
        except Exception as e:
            print(f"Error in log_message: {e}")

    def open_house_manager(self):
        """Open house manager with error handling"""
        try:
            if not self.current_device:
                self.log_message("No device selected for house management", "WARNING")
                messagebox.showwarning("Warning", "Please select a device first")
                return
                
            self.log_message(f"Opening house manager for device: {self.current_device}")
            house_manager = HouseManager(parent=self, adb_process=self.adbProcess, device_id=self.current_device)
            house_manager.run()
            
        except Exception as e:
            error_msg = f"Failed to open house manager: {e}"
            self.log_message(error_msg, "ERROR")
            logger.error(traceback.format_exc())
            messagebox.showerror("Error", error_msg)

    def refresh_devices(self):
        """Refresh connected devices with error handling"""
        try:
            self.log_message("Refreshing device list...")
            devices = self.adbProcess.get_connected_devices()
            
            if not devices:
                self.device_combo['values'] = []
                self.device_combo.set("")
                self.status_label.config(text="⚠️ No devices found.", fg="red")
                self.log_message("No devices found", "WARNING")
                return
            else:
                # Filter out localhost devices
                if config.FILTER_LOCALHOST_DEVICES:
                    devices = [d for d in devices if not any(pattern in d for pattern in config.LOCALHOST_PATTERNS)]
                
                if not devices:
                    self.device_combo['values'] = []
                    self.device_combo.set("")
                    self.status_label.config(text="⚠️ No valid devices found.", fg="red")
                    self.log_message("No valid devices found (filtered out localhost)", "WARNING")
                    return
                    
                self.device_combo['values'] = devices
                self.device_combo.current(0)
                self.status_label.config(text=f"✔ Found {len(devices)} device(s).", fg="green")
                self.log_message(f"Found {len(devices)} device(s): {', '.join(devices)}")
                self.on_device_selected()
                
        except Exception as e:
            error_msg = f"Failed to refresh devices: {e}"
            self.log_message(error_msg, "ERROR")
            logger.error(traceback.format_exc())
            self.status_label.config(text="❌ Error refreshing devices", fg="red")
            messagebox.showerror("Error", error_msg)

    def toggle_pause(self):
        """Toggle pause state with error handling"""
        try:
            device = self.current_device
            if not device:
                self.log_message("No device selected for pause toggle", "WARNING")
                return
                
            paused = self.device_paused.get(device, False)
            self.device_paused[device] = not paused
            
            if self.device_paused[device]:
                self.pause_button.config(text="▶️ Bắt đầu")
                self.log_message(f"Paused tasks for device: {device}")
            else:
                self.pause_button.config(text="⏸ Tạm dừng")
                self.log_message(f"Resumed tasks for device: {device}")
                self.on_task_changed()
                
        except Exception as e:
            error_msg = f"Failed to toggle pause: {e}"
            self.log_message(error_msg, "ERROR")
            logger.error(traceback.format_exc())

    def on_device_selected(self, event=None):
        """Handle device selection with error handling"""
        try:
            if self.current_device:
                self.device_tasks[self.current_device] = {task: var.get() for task, var in self.tasks.items()}

            device = self.device_combo.get()
            self.current_device = device
            
            if device:
                self.log_message(f"Device selected: {device}")

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
                
        except Exception as e:
            error_msg = f"Failed to handle device selection: {e}"
            self.log_message(error_msg, "ERROR")
            logger.error(traceback.format_exc())

    def on_task_changed(self):
        """Handle task changes with error handling"""
        try:
            device = self.current_device
            if device:
                self.device_tasks[device] = {task: var.get() for task, var in self.tasks.items()}
                
                # Log task changes
                active_tasks = [task for task, var in self.tasks.items() if var.get()]
                if active_tasks:
                    self.log_message(f"Tasks activated for {device}: {', '.join(active_tasks)}")
                else:
                    self.log_message(f"No active tasks for {device}")

                if device not in self.device_threads and not self.device_paused.get(device, False):
                    self.log_message(f"Starting task thread for device: {device}")
                    t = threading.Thread(target=self.run_device_tasks, args=(device,), daemon=True)
                    self.device_threads[device] = t
                    t.start()
                    
        except Exception as e:
            error_msg = f"Failed to handle task change: {e}"
            self.log_message(error_msg, "ERROR")
            logger.error(traceback.format_exc())

    def ensure_device_farm_state(self, device):
        """Ensure device has farm priority and current index initialized"""
        if device not in self.farm_priority:
            self.farm_priority[device] = ["food", "wood", "stone", "gold"]
        if device not in self.current_farm_index:
            self.current_farm_index[device] = 0

    def get_next_farm_type(self, device, tasks):
        """
        Lấy loại tài nguyên tiếp theo theo thứ tự ưu tiên của device.
        Nếu loại hiện tại không bật trong `tasks`, nó sẽ nhảy sang loại tiếp theo.
        Trả về None nếu không có loại nào bật.
        """
        self.ensure_device_farm_state(device)
        priority = self.farm_priority.get(device, ["food", "wood", "stone", "gold"])
        start_index = self.current_farm_index.get(device, 0)

        n = len(priority)
        for i in range(n):
            idx = (start_index + i) % n
            res_type = priority[idx]
            if tasks.get(res_type):
                # set next start index to the following resource
                self.current_farm_index[device] = (idx + 1) % n
                return res_type
        return None

    def run_device_tasks(self, device):
        """Run device tasks with comprehensive error handling"""
        try:
            self.log_message(f"Starting task execution for device: {device}")
            
            adb_process = AdbProcess(adb_path="adb/adb.exe")
            detect = Detect(adb=adb_process)
            train = TroopTrainer(adb_process=adb_process, detect=detect, device=device)
            explorer = Explore(adb_process=adb_process, detect=detect)
            farm = Farm(adb_process=adb_process, detect=detect)
            recruitment = Recruitment(adb_process=adb_process, detect=detect)
            
            while any(self.device_tasks.get(device, {}).values()):
                try:   
                    if self.device_paused.get(device, False):
                        time.sleep(0.5)
                        continue

                    # Update device references
                    train.device = device
                    houses = load_data().get(device, {}).get("houses", [])
                    train.houses = houses
                    farm.device_id = device
                    
                    # Capture screenshot
                    img = adb_process.capture(device)
                    if img is None:
                        self.log_message(f"Failed to capture screenshot from {device}", "ERROR")
                        time.sleep(2)
                        continue
                    
                    # Check for disconnection
                    disconnected_pos = detect.find_object_position(img, "./images/disconnected.png")
                    if disconnected_pos:
                        self.log_message(f"Disconnection detected on {device}, attempting to reconnect")
                        adb_process.tap(device, 638, 471)
                        detect.wait_until_found(device, "./images/home.png", timeout=100)
                        time.sleep(0.5)
                        continue
                    # Check for login
                    other_login = detect.find_object_position(img, "./images/other_login.png")
                    if other_login:
                        self.log_message(f"'Other Login' screen detected on {device}, attempting to log in")
                        confirm = detect.wait_until_found(device, "./images/confirm.png")
                        time.sleep(300)
                        adb_process.tap(device, *confirm)
                        continue
                    # Always check
                    pos = detect.find_object_directory(img, "./images/always_check")
                    if pos:
                        adb_process.tap(device, *pos)
                        time.sleep(0.5)
                        continue
                    goback_pos = detect.find_object_position(img, "./images/goback.png")
                    if goback_pos:
                        adb_process.tap(device, *goback_pos)
                        detect.wait_until_found(device, "./images/home.png")
                        time.sleep(0.5)
                        continue
                    # Recruitment
                    recruitment.houses = houses
                    recruitment.device_id = device
                    recruitment.perform_action_requirement(img)

                    # Explorer setup
                    explorer.houses = houses
                    explorer.device_id = device

                    tasks = self.device_tasks[device]           

                    # Training
                    if tasks.get("train"):
                        train.auto_train_units(img)

                    # Explore / Cave
                    if tasks.get("explore") or tasks.get("cave"):
                        if detect.check_object_exists_directory(img, "./images/explore_check"):
                            if tasks.get("explore") and tasks.get("cave"):
                                explorer.perform_action_explore_and_cave_probe()
                            elif tasks.get("explore"):
                                explorer.perform_action_sequence()
                            elif tasks.get("cave"):
                                explorer.perform_action_cave_probe()

                    # Farming
                    if tasks.get("farm"):
                        army_count = tasks.get("army_count")
                        next_resource = self.get_next_farm_type(device, tasks)

                        if not next_resource:
                            pass
                        else:
                            army_pos_1 = detect.find_object_position(img, "./images/armies/army_1.png")
                            army_pos_2 = detect.find_object_position(img, "./images/armies/army_2.png")
                            army_pos_3 = detect.find_object_position(img, "./images/armies/army_3.png")
                            if army_pos_1 is None and army_count == 1:
                                farm.perform_action_farm(next_resource)
                            elif army_pos_2 is None and army_count == 2:
                                farm.perform_action_farm(next_resource)
                            elif army_pos_3 is None and army_count == 3:
                                farm.perform_action_farm(next_resource)
                            else:
                                # nếu cả 2 đều có army hoặc army_count khác (>2) -> bạn có thể mở rộng logic ở đây
                                # ví dụ: khi army_count > 2 tìm các ảnh army_3.png... (nếu cần)
                                pass
                    time.sleep(config.IMAGE_CAPTURE_DELAY)
                    
                except Exception as e:
                    logger.error(traceback.format_exc())
                    time.sleep(config.ERROR_RETRY_DELAY)  # Wait before retrying
            self.log_message(f"All tasks stopped for device {device}")
            del self.device_threads[device]
            
        except Exception as e:
            error_msg = f"Critical error in device task execution for {device}: {e}"
            self.log_message(error_msg, "ERROR")
            logger.error(traceback.format_exc())
            
            # Clean up thread reference
            if device in self.device_threads:
                del self.device_threads[device]

# ---- Chạy ứng dụng GUI ----
if __name__ == "__main__":
    try:
        # Validate configuration first
        config_errors = config.validate_config()
        if config_errors:
            error_msg = "Configuration errors found:\n" + "\n".join(f"• {error}" for error in config_errors)
            print(error_msg)
            if config.SHOW_ERROR_DIALOGS:
                messagebox.showerror("Configuration Error", error_msg)
            exit(1)
        
        logger.info("Starting Rise of Kingdoms Tool...")
        logger.info("Configuration loaded successfully")
        
        app = AdbApp(adb_path=config.ADB_PATH)
        logger.info("Application started successfully")
        app.mainloop()
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        logger.error(traceback.format_exc())
        if config.SHOW_ERROR_DIALOGS:
            messagebox.showerror("Critical Error", f"Application failed to start: {e}")
