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
            "resource_gather_btn": "./images/resource_gather_button.png",
            "matched": "./images/matched.png",
            "goback": "images/goback.png"
        }

        def tap_wait(image_key):
            coords = self.detect.wait_until_found(self.device_id, image_paths[image_key])
            if coords:
                self.adb_process.tap(self.device_id, *coords)
                time.sleep(delay)
            else:
                return

        # Sequence of actions
        tap_wait("home")
        tap_wait("search")
        tap_wait("resource")
        tap_wait("searching")
        tap_wait("gather_btn")
        tap_wait("resource_gather_btn")
        tap_wait("matched")
        tap_wait("goback")


