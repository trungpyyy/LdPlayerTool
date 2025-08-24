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
from utils.state_manager import StateManager
from task.train import TroopTrainer
from task.explore import Explore
from task.farm import Farm
from task.built import Built
from task.recruitment import Recruitment

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
            
            # Update UI state after initialization
            self._update_pause_button_state()
            
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
            
            # Initialize state manager
            self.state_manager = StateManager()
            
            # Initialize device-related variables
            self.device_tasks = {}
            self.current_device = None
            self.device_threads = {}
            self.device_paused = {}
            self.farm_priority = {}
            self.current_farm_index = {}
            
            # Load saved states for known devices
            self._load_saved_device_states()
            
            logger.info("Core components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize core components: {e}")
            raise
    
    def _load_saved_device_states(self):
        """Load saved states for known devices"""
        try:
            # Load saved device states
            for device_id in self.state_manager.get_all_devices():
                device_state = self.state_manager.get_device_state(device_id)
                
                # Load tasks
                if device_state.get("tasks"):
                    self.device_tasks[device_id] = device_state["tasks"]
                
                # Don't load pause state - always start with not paused (show "Bắt đầu")
                # self.device_paused[device_id] will be initialized when device is selected
                
                # Load farm priority and index
                if device_state.get("farm_priority"):
                    self.farm_priority[device_id] = device_state["farm_priority"]
                if device_state.get("current_farm_index") is not None:
                    self.current_farm_index[device_id] = device_state["current_farm_index"]
            
            logger.info(f"Loaded saved states for {len(self.state_manager.get_all_devices())} devices")
            
        except Exception as e:
            logger.error(f"Failed to load saved device states: {e}")
            logger.error(traceback.format_exc())

    def get_current_device_pause_state(self):
        """Get current device's pause state"""
        if self.current_device and self.current_device in self.device_paused:
            return self.device_paused[self.current_device]
        return True  # Default to paused (show "Bắt đầu")

    def _update_pause_button_state(self):
        """Update pause button state based on current device"""
        try:
            if self.current_device and self.current_device in self.device_paused:
                paused = self.device_paused[self.current_device]
                if paused:
                    self.pause_button.config(text="▶️ Bắt đầu")
                else:
                    self.pause_button.config(text="⏸ Tạm dừng")
                self.log_message(f"Updated button state for {self.current_device}: {'Paused' if paused else 'Running'}")
            else:
                # Default state when no device is selected or device state is missing
                if self.current_device:
                    # Device exists but no pause state, initialize it
                    self.device_paused[self.current_device] = True
                    self.pause_button.config(text="▶️ Bắt đầu")
                    self.log_message(f"Initialized pause state for {self.current_device}: Paused")
                else:
                    # No device selected
                    self.pause_button.config(text="▶️ Bắt đầu")
        except Exception as e:
            logger.error(f"Failed to update pause button state: {e}")
            # Fallback: always show "Bắt đầu" on error
            self.pause_button.config(text="▶️ Bắt đầu")

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
                "built": tk.BooleanVar(),
                "recruitment": tk.BooleanVar(),
                "army_count": tk.IntVar(value=1),
            }
            self.checkbox_recruitment = tk.Checkbutton(self, text="Tuyển dụng", variable=self.tasks["recruitment"], command=self.on_task_changed)
            self.checkbox_built = tk.Checkbutton(self, text="Xây dựng", variable=self.tasks["built"], command=self.on_task_changed)
            self.checkbox_farm = tk.Checkbutton(self, text="Thu hoạch", variable=self.tasks["farm"], command=self.on_task_changed)
            self.checkbox_explore = tk.Checkbutton(self, text="Dò mây", variable=self.tasks["explore"], command=self.on_task_changed)
            self.checkbox_cave = tk.Checkbutton(self, text="Dò hang", variable=self.tasks["cave"], command=self.on_task_changed)
            self.checkbox_train = tk.Checkbutton(self, text="Huấn luyện lính", variable=self.tasks["train"], command=self.on_task_changed)
            """UI with 
            Thu hoạch
            Food Wood Stone Gold
            """
            self.checkbox_built.pack(anchor="w", padx=20)
            self.checkbox_recruitment.pack(anchor="w", padx=20)
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

            # State management buttons
            state_frame = tk.Frame(self)
            state_frame.pack(pady=5)
            
            self.state_info_button = tk.Button(state_frame, text="ℹ️ Thông tin trạng thái", command=self.show_state_info)
            self.state_info_button.pack(side="left", padx=5)
            
            self.clear_state_button = tk.Button(state_frame, text="🗑️ Xóa trạng thái", command=self.clear_current_device_state)
            self.clear_state_button.pack(side="left", padx=5)
            
            # Debug button
            self.debug_button = tk.Button(state_frame, text="🐛 Debug", command=self.debug_device_states)
            self.debug_button.pack(side="left", padx=5)
            
            # Reset button
            self.reset_button = tk.Button(state_frame, text="🔄 Reset States", command=self.reset_device_states)
            self.reset_button.pack(side="left", padx=5)

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
                messagebox.showwarning("Warning", "Vui lòng chọn device trước")
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
                
                # Try to select the last used device, otherwise select first
                last_device = self.state_manager.get_last_device()
                if last_device and last_device in devices:
                    self.device_combo.set(last_device)
                    self.log_message(f"Restored last used device: {last_device}")
                else:
                    self.device_combo.current(0)
                
                self.status_label.config(text=f"✔ Found {len(devices)} device(s).", fg="green")
                self.log_message(f"Found {len(devices)} device(s): {', '.join(devices)}")
                
                # After refreshing, update the current device selection and button state
                if self.current_device:
                    # If current device still exists in new list, keep its state
                    if self.current_device in devices:
                        # Device still exists, update button to reflect current state
                        self._update_pause_button_state()
                    else:
                        # Current device no longer exists, clear selection
                        self.current_device = None
                        self.pause_button.config(text="▶️ Bắt đầu")
                else:
                    # No device was selected, trigger device selection
                    self.on_device_selected()
                
        except Exception as e:
            error_msg = f"Failed to refresh devices: {e}"
            self.log_message(error_msg, "ERROR")
            logger.error(traceback.format_exc())
            self.status_label.config(text="❌ Error refreshing devices", fg="red")
            messagebox.showerror("Error", error_msg)

    def reset_device_states(self):
        """Reset and synchronize all device states"""
        try:
            self.log_message("Resetting device states...", "INFO")
            
            # Clear all device states
            self.device_paused.clear()
            self.device_tasks.clear()
            self.device_threads.clear()
            self.farm_priority.clear()
            self.current_farm_index.clear()
            
            # Reset current device
            if self.current_device:
                # Initialize fresh state for current device
                self.device_paused[self.current_device] = True  # Default to paused
                self.device_tasks[self.current_device] = self.state_manager.get_default_tasks()
                self.farm_priority[self.current_device] = ["food", "wood", "stone", "gold"]
                self.current_farm_index[self.current_device] = 0
                
                # Update button to reflect reset state
                self.pause_button.config(text="▶️ Bắt đầu")
                
                self.log_message(f"Reset completed for device: {self.current_device}", "INFO")
            else:
                self.log_message("No device selected for reset", "WARNING")
                
        except Exception as e:
            self.log_message(f"Reset failed: {e}", "ERROR")

    def debug_device_states(self):
        """Debug method to show current device states"""
        try:
            debug_info = f"Debug Info:\n"
            debug_info += f"Current Device: {self.current_device}\n"
            debug_info += f"Button Text: {self.pause_button.cget('text')}\n"
            debug_info += f"Device Paused States: {self.device_paused}\n"
            debug_info += f"Device Tasks: {self.device_tasks}\n"
            debug_info += f"Device Threads: {list(self.device_threads.keys())}\n"
            
            self.log_message(debug_info, "INFO")
            messagebox.showinfo("Debug Info", debug_info)
        except Exception as e:
            self.log_message(f"Debug failed: {e}", "ERROR")

    def toggle_pause(self):
        """Toggle pause state for current device"""
        try:
            device = self.current_device
            if not device:
                messagebox.showwarning("Warning", "Vui lòng chọn device trước")
                return
                
            # Get current pause state for this specific device
            paused = self.device_paused.get(device, True)  # Default to True (paused, show "Bắt đầu")
            self.device_paused[device] = not paused
            
            # Don't save pause state to persistent storage - only keep in memory
            
            if self.device_paused[device]:
                # Pausing tasks for this device only
                self.pause_button.config(text="▶️ Bắt đầu")
                self.log_message(f"Tạm dừng tasks cho device: {device}")
                
                # Stop task thread for this device only
                if device in self.device_threads:
                    del self.device_threads[device]
                    self.log_message(f"Đã dừng task thread cho device: {device}")
            else:
                # Starting tasks for this device only
                self.pause_button.config(text="⏸ Tạm dừng")
                self.log_message(f"Bắt đầu tasks cho device: {device}")
                
                # Start task thread for this device only if not already running and has active tasks
                active_tasks = [task for task, var in self.tasks.items() if var.get()]
                if active_tasks and device not in self.device_threads:
                    t = threading.Thread(target=self.run_device_tasks, args=(device,), daemon=True)
                    self.device_threads[device] = t
                    t.start()
                    self.log_message(f"Đã khởi động task thread cho device: {device}")
                elif not active_tasks:
                    self.log_message(f"Không có task nào được chọn cho device: {device}")
                    # Keep the button as "Tạm dừng" but don't start thread
                    # User can still pause if they want
                
        except Exception as e:
            error_msg = f"Failed to toggle pause: {e}"
            self.log_message(error_msg, "ERROR")
            logger.error(traceback.format_exc())
            messagebox.showerror("Error", error_msg)

    def _save_current_device_state(self):
        """Save current device state before switching"""
        try:
            if self.current_device:
                # Save current device state before switching
                current_tasks = {task: var.get() for task, var in self.tasks.items()}
                self.device_tasks[self.current_device] = current_tasks
                self.state_manager.save_device_tasks(self.current_device, current_tasks)
                
                # Don't save pause state - only keep in memory
                    
                self.log_message(f"Đã lưu trạng thái cho device: {self.current_device}")
        except Exception as e:
            logger.error(f"Failed to save current device state: {e}")

    def on_device_selected(self, event=None):
        """Handle device selection with error handling"""
        try:
            # Save current device state before switching
            self._save_current_device_state()

            device = self.device_combo.get()
            self.current_device = device
            
            if device:
                self.log_message(f"Device selected: {device}")
                # Save as last used device
                self.state_manager.set_last_device(device)

            if device in self.device_tasks:
                # Load saved tasks for this device
                for task, var in self.tasks.items():
                    var.set(self.device_tasks[device].get(task, False))
                
                # Load saved pause state for this device, default to True (paused) if not exists
                if device not in self.device_paused:
                    self.device_paused[device] = True
                paused = self.device_paused[device]
                
                self.log_message(f"Loaded existing state for {device}: {'Paused' if paused else 'Running'}")
            else:
                # Initialize with default state (all tasks disabled)
                for var in self.tasks.values():
                    var.set(False)
                # Initialize device state
                self.device_tasks[device] = self.state_manager.get_default_tasks()
                self.device_paused[device] = True  # Default to paused (show "Bắt đầu") for new devices
                self.farm_priority[device] = ["food", "wood", "stone", "gold"]
                self.current_farm_index[device] = 0
                
                # Save initial state for new device
                self.state_manager.save_device_tasks(device, self.device_tasks[device])
                # Don't save pause state - only keep in memory
                self.state_manager.save_device_farm_state(device, self.farm_priority[device], 0)
                    
                paused = True
                self.log_message(f"Initialized new device {device}: Paused")
            
            # Update button to reflect the actual device state
            self._update_pause_button_state()
                
        except Exception as e:
            error_msg = f"Failed to handle device selection: {e}"
            self.log_message(error_msg, "ERROR")
            logger.error(traceback.format_exc())
            messagebox.showerror("Error", error_msg)

    def on_task_changed(self):
        """Handle task changes with error handling"""
        try:
            device = self.current_device
            if device:
                current_tasks = {task: var.get() for task, var in self.tasks.items()}
                self.device_tasks[device] = current_tasks
                
                # Save task state to persistent storage
                self.state_manager.save_device_tasks(device, current_tasks)
                
                # Log task changes
                active_tasks = [task for task, var in self.tasks.items() if var.get()]
                if active_tasks:
                    self.log_message(f"Tasks updated for {device}: {', '.join(active_tasks)}")
                else:
                    self.log_message(f"No active tasks for {device}")

                # Don't automatically start task thread - only start when pause button is pressed
                # Task thread management is handled in toggle_pause method
                if device not in self.device_threads and not self.device_paused.get(device, True):
                    self.log_message(f"Starting task thread for device: {device}")
                    t = threading.Thread(target=self.run_device_tasks, args=(device,), daemon=True)
                    self.device_threads[device] = t
                    t.start()
                elif device in self.device_threads and self.device_paused.get(device, True):
                    # Stop task thread if device is paused
                    if device in self.device_threads:
                        del self.device_threads[device]
                        self.log_message(f"Stopped task thread for paused device: {device}")
                    
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
        
        # Save farm state to persistent storage
        self.state_manager.save_device_farm_state(
            device, 
            self.farm_priority[device], 
            self.current_farm_index[device]
        )

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
            built = Built(adb_process=adb_process, detect=detect)
            recruitment = Recruitment(adb_process=adb_process, detect=detect)
            
            while any(self.device_tasks.get(device, {}).values()):
                try:   
                    if self.device_paused.get(device, True):  # Default to True (paused)
                        time.sleep(0.5)
                        continue

                    # Update device references
                    houses = load_data().get(device, {}).get("houses", [])
                    
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
                    pos_always = detect.find_object_directory(img, "./images/always_check")
                    if pos_always:
                        adb_process.tap(device, *pos_always)
                        detect.wait_until_found(device, "./images/home.png")
                        time.sleep(0.5)
                        continue
                    goback_pos = detect.find_object_position(img, "./images/goback.png")
                    if goback_pos:
                        adb_process.tap(device, *goback_pos)
                        detect.wait_until_found(device, "./images/home.png")
                        time.sleep(0.5)
                        continue

                    tasks = self.device_tasks[device]           
                    # Recruitment
                    if tasks.get("recruitment"):
                        recruitment.houses = houses
                        recruitment.device_id = device
                        recruitment.perform_action_recruitment(img)

                    # Training
                    if tasks.get("train"):
                        train.device = device
                        train.houses = houses
                        train.auto_train_units(img)
                    if tasks.get("built"):
                        built.houses = houses
                        built.device_id = device
                        built_check = detect.check_object_exists(img, "images/built/check_build.png")
                        if built_check:
                            built.perform_action_build()
                    # Explore / Cave
                    if tasks.get("explore") or tasks.get("cave"):
                        # Explorer setup
                        explorer.houses = houses
                        explorer.device_id = device
                        if detect.check_object_exists_directory(img, "./images/explore_check"):
                            if tasks.get("explore") and tasks.get("cave"):
                                explorer.perform_action_explore_and_cave_probe()
                            elif tasks.get("explore"):
                                explorer.perform_action_sequence()
                            elif tasks.get("cave"):
                                explorer.perform_action_cave_probe()

                    # Farming
                    if tasks.get("farm"):
                        farm_check = detect.check_object_exists_directory(img, "./images/farm/check")
                        farm.device_id = device
                        
                        if farm_check is False:
                            farm.perform_action_using_up()
                        army_count = tasks.get("army_count")
                        next_resource = self.get_next_farm_type(device, tasks)

                        if not next_resource:
                            pass
                        else:
                            army_pos_1 = detect.find_object_position(img, "./images/armies/army_1.png")
                            army_pos_2 = detect.find_object_position(img, "./images/armies/army_2.png")
                            army_pos_3 = detect.find_object_position(img, "./images/armies/army_3.png")
                            army_pos_4 = detect.find_object_position(img, "./images/armies/army_4.png")
                            if army_pos_1 is None and army_count == 1:
                                farm.perform_action_farm(next_resource)
                            elif army_pos_2 is None and army_count == 2:
                                farm.perform_action_farm(next_resource)
                            elif army_pos_3 is None and army_count == 3:
                                farm.perform_action_farm(next_resource)
                            elif army_pos_4 is None and army_count == 4:
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

    def show_state_info(self):
        """Show information about saved states"""
        try:
            summary = self.state_manager.get_state_summary()
            
            info_text = f"Thông tin trạng thái:\n\n"
            info_text += f"Tổng số device: {summary['total_devices']}\n"
            info_text += f"Cập nhật lần cuối: {summary['last_updated']}\n\n"
            
            if summary['devices']:
                info_text += "Chi tiết device:\n"
                for device_id, device_info in summary['devices'].items():
                    status = "⏸ Tạm dừng" if device_info['is_paused'] else "▶️ Đang chạy"
                    has_tasks = "✅ Có task" if device_info['has_tasks'] else "❌ Không có task"
                    info_text += f"• {device_id}: {status} | {has_tasks}\n"
            else:
                info_text += "Chưa có device nào được lưu trạng thái.\n"
            
            messagebox.showinfo("Thông tin trạng thái", info_text)
            
        except Exception as e:
            error_msg = f"Failed to show state info: {e}"
            self.log_message(error_msg, "ERROR")
            logger.error(traceback.format_exc())
            messagebox.showerror("Error", error_msg)

    def clear_current_device_state(self):
        """Clear state for current device"""
        try:
            if not self.current_device:
                messagebox.showwarning("Warning", "Vui lòng chọn device trước")
                return
            
            result = messagebox.askyesno(
                "Xác nhận", 
                f"Bạn có chắc muốn xóa trạng thái của device '{self.current_device}'?\n"
                "Hành động này không thể hoàn tác."
            )
            
            if result:
                # Clear from state manager
                self.state_manager.clear_device_state(self.current_device)
                
                # Clear from local variables
                if self.current_device in self.device_tasks:
                    del self.device_tasks[self.current_device]
                if self.current_device in self.device_paused:
                    del self.device_paused[self.current_device]
                if self.current_device in self.farm_priority:
                    del self.farm_priority[self.current_device]
                if self.current_device in self.current_farm_index:
                    del self.current_farm_index[self.current_device]
                
                # Reset UI to defaults
                for var in self.tasks.values():
                    var.set(False)
                
                # Always set to not paused state (show "Bắt đầu") - only in memory
                self.device_paused[self.current_device] = False
                self.pause_button.config(text="⏸ Tạm dừng")
                
                self.log_message(f"Đã xóa trạng thái của device: {self.current_device}")
                messagebox.showinfo("Thành công", f"Đã xóa trạng thái của device '{self.current_device}'")
                
        except Exception as e:
            error_msg = f"Failed to clear device state: {e}"
            self.log_message(error_msg, "ERROR")
            logger.error(traceback.format_exc())
            messagebox.showerror("Error", error_msg)

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
