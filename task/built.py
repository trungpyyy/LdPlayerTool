import time
from utils.AdbProcess import AdbProcess
from utils.Detect import Detect

class Built:
    def __init__(self, adb_process: AdbProcess, detect: Detect, device_id=None, houses=None):
        self.adb_process = adb_process
        self.detect = detect
        self.device_id = device_id
        self.houses = houses or []
    
        """
        Perform search built action by detecting and tapping on the search icon.
        This method is similar to perform_built_action but specifically for searching builts.
        """

    def perform_action_build(self,  delay=0.8):
        """Perform search built action by detecting and tapping on specific icons."""
        
        image_paths = {
            "home": "./images/home.png",
            "build_1": "./images/built/build_1.png",
            "build_2": "./images/built/build_2.png",
            "build_3": "./images/built/build_3.png",
            "build_4": "./images/built/build_4.png",
            "goback": "images/goback.png",
            "help": "images/built/help.png"
        }

        def tap_wait(image_key):
            coords = self.detect.wait_until_found(self.device_id, image_paths[image_key])
            if not coords:
                return None
            self.adb_process.tap(self.device_id, *coords)
            time.sleep(delay)
            return True
        coords = next((h for h in self.houses if h["name"] == "Xây dựng"), None)
        if coords is None:
            print(f"Chưa có tọa độ cho Xây dựng.")
            return None
        else:
            print(f"Xây dựng...")
            pos = (coords["x"], coords["y"])
            self.adb_process.tap(self.device_id, *pos)
        # --- các bước ban đầu ---
        for key in ["build_1", "build_2", "build_3", "build_4","help", "home", "goback"]:
            if tap_wait(key) is None:
                return




