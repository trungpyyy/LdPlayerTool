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

    def perform_action_farm(self, resource="food", delay=0.8):
        """Perform search farm action by detecting and tapping on specific icons."""
        
        image_paths = {
            "home": "./images/home.png",
            "search": "./images/search.png",
            "resource": f"./images/farm/{resource}.png",
            "searching": "./images/searching.png",
            "gather_btn": "./images/farm/GatherButton.png",
            "matching": "./images/matching.png",
            "resource_gather_btn": "./images/resource_gather_button.png",
            "matched": "./images/matched.png",
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
                    self.detect.wait_until_found(self.device_id, "./images/home.png")

        def find_gather_btn():
            if self.detect.wait_until_found(self.device_id, image_paths["resource_gather_btn"]):
                if not stop_event.is_set():
                    stop_event.set()
                    tap_wait("resource_gather_btn")
                    if tap_wait("matched") is not None:
                        tap_wait("goback")
                        self.detect.wait_until_found(self.device_id, "./images/home.png")

        t1 = threading.Thread(target=find_matching)
        t2 = threading.Thread(target=find_gather_btn)

        t1.start()
        t2.start()

        t1.join()
        t2.join()




