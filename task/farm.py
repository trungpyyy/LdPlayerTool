import threading
import time
from utils.AdbProcess import AdbProcess
from utils.Detect import Detect

class Farm:
    def __init__(self, adb_process: AdbProcess, detect: Detect, device_id=None):
        self.adb_process = adb_process
        self.detect = detect
        self.device_id = device_id
    
        """
        Perform search farm action by detecting and tapping on the search icon.
        This method is similar to perform_farm_action but specifically for searching farms.
        Parameters:
        resource (str): The type of resource to search for, e.g., "food", "wood", "stone", gold.
        """
    def perform_action_using_up(self):
        image_paths = {
            "bag": "images/bag.png",
            "up": "images/farm/up.png",
            "farm_8": "images/farm/farm_8.png",
            "farm_24": "images/farm/farm_24.png",
            "using": "images/farm/using.png",
            "close": "images/always_check/close.png"
        }
        def tap_wait(image_key):
            coords = self.detect.wait_until_found(self.device_id, image_paths[image_key])
            if not coords:
                return None
            self.adb_process.tap(self.device_id, *coords)
            return True
        for key in ["bag", "up"]:
            if tap_wait(key) is None:
                return
        stop_event = threading.Event()
        def find_8():
            if self.detect.wait_until_found(self.device_id, image_paths["farm_8"]):
                if not stop_event.is_set():
                    stop_event.set()
                    for key in ["farm_8", "using", "close"]:
                        if tap_wait(key) is None:
                            return

        def find_24():
            if self.detect.wait_until_found(self.device_id, image_paths["farm_24"]):
                if not stop_event.is_set():
                    stop_event.set()
                    for key in ["farm_24", "using", "close"]:
                        if tap_wait(key) is None:
                            return

        t1 = threading.Thread(target=find_8)
        t2 = threading.Thread(target=find_24)

        t1.start()
        t2.start()

        t1.join()
        t2.join()        
        
        
    def perform_action_farm(self, resource="food", delay=0.8):
        """Perform search farm action by detecting and tapping on specific icons."""
        
        image_paths = {
            "home": "images/home.png",
            "search": "images/search.png",
            "resource": f"images/farm/{resource}.png",
            "searching": "images/searching.png",
            "gather_btn": "images/farm/GatherButton.png",
            "matching": "images/matching.png",
            "resource_gather_btn": "images/resource_gather_button.png",
            "matched": "images/matched.png",
            "goback": "images/goback.png"
        }

        def tap_wait(image_key):
            coords = self.detect.wait_until_found(self.device_id, image_paths[image_key])
            if not coords:
                return None
            if image_key == "matching":
                self.adb_process.tap(self.device_id, 640, 360)
            else:
                self.adb_process.tap(self.device_id, *coords)
            time.sleep(delay)
            return True

        # --- các bước ban đầu ---
        for key in ["home", "search", "resource", "searching", "gather_btn"]:
            if tap_wait(key) is None:
                return

        # --- chạy matching và resource_gather_btn song song ---
        stop_event = threading.Event()

        def find_matching():
            if self.detect.wait_until_found(self.device_id, image_paths["matching"]):
                if not stop_event.is_set():
                    stop_event.set()
                    self.adb_process.tap(self.device_id, 640, 360)
                    time.sleep(delay)
                    tap_wait("goback")
                    self.detect.wait_until_found(self.device_id, "images/home.png")

        def find_gather_btn():
            if self.detect.wait_until_found(self.device_id, image_paths["resource_gather_btn"]):
                if not stop_event.is_set():
                    stop_event.set()
                    tap_wait("resource_gather_btn")
                    coords = self.detect.wait_until_found(self.device_id, "./images/farm/rm_farm.png")
                    if coords is not None:
                        self.adb_process.tap(self.device_id, *coords)
                    if tap_wait("matched") is not None:
                        tap_wait("goback")
                        self.detect.wait_until_found(self.device_id, "images/home.png")

        t1 = threading.Thread(target=find_matching)
        t2 = threading.Thread(target=find_gather_btn)

        t1.start()
        t2.start()

        t1.join()
        t2.join()




