import subprocess
import cv2
import numpy as np
class AdbProcess:
    def __init__(self, adb_path="adb/adb.exe"):
        self.adb_path = adb_path

    def tap(self, device_id, x, y):
        command = [
            self.adb_path,
            "-s", device_id,
            "shell", "input", "tap", str(x), str(y)
        ]
        try:
            subprocess.check_output(command)
        except subprocess.CalledProcessError as e:
            print(f"Error tapping on device {device_id}: {e}")
            
    def get_connected_devices(self):
        try:
            output = subprocess.check_output([self.adb_path, "devices"], encoding="utf-8")
            lines = output.strip().splitlines()[1:]
            devices = []
            for line in lines:
                if "device" in line:
                    device_id = line.split()[0]
                    devices.append(device_id)
            return devices
        except subprocess.CalledProcessError as e:
            print(f"Error listing devices: {e}")
            return []    
    def capture(self, device_id):
        command = [
            self.adb_path,
            "-s", device_id,
            "exec-out", "screencap", "-p"
        ]
        try:
            img = subprocess.check_output(command)
            img = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_COLOR)
            cv2.imwrite("screenshot.png", img)  # Save screenshot for debugging
            return img
        except subprocess.CalledProcessError as e:
            print(f"Error capturing screenshot on device {device_id}: {e}")
            return None