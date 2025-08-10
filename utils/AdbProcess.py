import subprocess
import cv2
import numpy as np
import logging
import traceback
import time

logger = logging.getLogger(__name__)

class AdbProcess:
    def __init__(self, adb_path="adb/adb.exe"):
        self.adb_path = adb_path
        self._test_adb_connection()

    def _test_adb_connection(self):
        """Test if ADB is accessible and working"""
        try:
            result = subprocess.run([self.adb_path, "version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info(f"ADB initialized successfully: {result.stdout.strip()}")
            else:
                logger.error(f"ADB version check failed: {result.stderr}")
        except FileNotFoundError:
            logger.error(f"ADB executable not found at: {self.adb_path}")
            raise FileNotFoundError(f"ADB executable not found at: {self.adb_path}")
        except subprocess.TimeoutExpired:
            logger.error("ADB version check timed out")
            raise TimeoutError("ADB version check timed out")
        except Exception as e:
            logger.error(f"Failed to test ADB connection: {e}")
            raise

    def tap(self, device_id, x, y):
        """Tap on device screen with error handling and logging"""
        try:
            command = [
                self.adb_path,
                "-s", device_id,
                "shell", "input", "tap", str(x), str(y)
            ]
            
            logger.debug(f"Executing tap command: {' '.join(command)}")
            
            result = subprocess.run(command, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.debug(f"Tap successful at ({x}, {y}) on device {device_id}")
            else:
                error_msg = f"Tap failed on device {device_id} at ({x}, {y}): {result.stderr}"
                logger.error(error_msg)
                raise subprocess.CalledProcessError(result.returncode, command, result.stdout, result.stderr)
                
        except subprocess.TimeoutExpired:
            error_msg = f"Tap command timed out on device {device_id}"
            logger.error(error_msg)
            raise TimeoutError(error_msg)
        except subprocess.CalledProcessError as e:
            logger.error(f"Error tapping on device {device_id}: {e}")
            raise
        except Exception as e:
            error_msg = f"Unexpected error during tap on device {device_id}: {e}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            raise

    def get_connected_devices(self):
        """Get list of connected devices with error handling and logging"""
        try:
            logger.debug("Getting connected devices...")
            
            result = subprocess.run([self.adb_path, "devices"], 
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode != 0:
                error_msg = f"Failed to get devices list: {result.stderr}"
                logger.error(error_msg)
                return []
            
            lines = result.stdout.strip().splitlines()[1:]  # Skip header line
            devices = []
            
            for line in lines:
                if "device" in line and not line.strip().startswith("*"):
                    device_id = line.split()[0]
                    devices.append(device_id)
                    logger.debug(f"Found device: {device_id}")
            
            logger.info(f"Found {len(devices)} connected device(s)")
            return devices
            
        except subprocess.TimeoutExpired:
            error_msg = "Device list command timed out"
            logger.error(error_msg)
            return []
        except subprocess.CalledProcessError as e:
            error_msg = f"Error listing devices: {e}"
            logger.error(error_msg)
            return []
        except Exception as e:
            error_msg = f"Unexpected error getting devices: {e}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return []

    def capture(self, device_id):
        """Capture screenshot from device with error handling and logging"""
        try:
            logger.debug(f"Capturing screenshot from device: {device_id}")
            
            command = [
                self.adb_path,
                "-s", device_id,
                "exec-out", "screencap", "-p"
            ]
            
            start_time = time.time()
            result = subprocess.run(command, capture_output=True, timeout=15)
            capture_time = time.time() - start_time
            
            if result.returncode != 0:
                error_msg = f"Screenshot capture failed on device {device_id}: {result.stderr.decode()}"
                logger.error(error_msg)
                return None
            
            if not result.stdout:
                error_msg = f"Empty screenshot data from device {device_id}"
                logger.error(error_msg)
                return None
            
            # Convert bytes to numpy array
            try:
                img = cv2.imdecode(np.frombuffer(result.stdout, np.uint8), cv2.IMREAD_COLOR)
                
                if img is None:
                    error_msg = f"Failed to decode screenshot from device {device_id}"
                    logger.error(error_msg)
                    return None
                
                # Save screenshot for debugging
                try:
                    cv2.imwrite("screenshot.png", img)
                    logger.debug(f"Screenshot saved successfully in {capture_time:.2f}s")
                except Exception as save_error:
                    logger.warning(f"Could not save screenshot: {save_error}")
                
                return img
                
            except Exception as decode_error:
                error_msg = f"Failed to decode screenshot data from device {device_id}: {decode_error}"
                logger.error(error_msg)
                return None
                
        except subprocess.TimeoutExpired:
            error_msg = f"Screenshot capture timed out on device {device_id}"
            logger.error(error_msg)
            return None
        except subprocess.CalledProcessError as e:
            error_msg = f"Error capturing screenshot on device {device_id}: {e}"
            logger.error(error_msg)
            return None
        except Exception as e:
            error_msg = f"Unexpected error during screenshot capture on device {device_id}: {e}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return None

    def is_device_connected(self, device_id):
        """Check if a specific device is still connected"""
        try:
            devices = self.get_connected_devices()
            return device_id in devices
        except Exception as e:
            logger.error(f"Error checking device connection for {device_id}: {e}")
            return False

    def restart_adb_server(self):
        """Restart ADB server to resolve connection issues"""
        try:
            logger.info("Restarting ADB server...")
            
            # Kill ADB server
            subprocess.run([self.adb_path, "kill-server"], 
                         capture_output=True, timeout=10)
            
            # Wait a moment
            time.sleep(2)
            
            # Start ADB server
            subprocess.run([self.adb_path, "start-server"], 
                         capture_output=True, timeout=10)
            
            # Wait for server to be ready
            time.sleep(3)
            
            logger.info("ADB server restarted successfully")
            return True
            
        except Exception as e:
            error_msg = f"Failed to restart ADB server: {e}"
            logger.error(error_msg)
            return False