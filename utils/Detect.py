import cv2
import numpy as np
import logging
import traceback
import os
import time
from utils import AdbProcess

logger = logging.getLogger(__name__)

class Detect:
    def __init__(self, adb: AdbProcess):
        self.adb = adb
        logger.info("Detect class initialized successfully")

    def check_object_exists(self, image, template, threshold=0.9):
        """
        Kiểm tra xem đối tượng có tồn tại trong ảnh hay không.
        :param image: Ảnh gốc (numpy array).
        :param template: Mẫu cần tìm (numpy array).
        :param threshold: Ngưỡng tương đồng để xác định sự tồn tại.
        :return: True nếu đối tượng tồn tại, ngược lại False.
        """
        start_time = time.time()
        try:
            if image is None:
                logger.error("Input image is None")
                return False
                
            if template is None:
                logger.error("Template path is None")
                return False
            
            # Check if template file exists
            if not os.path.exists(template):
                logger.error(f"Template file not found: {template}")
                return False
            
            # Load template image
            template_img = cv2.imread(template, cv2.IMREAD_COLOR)
            if template_img is None:
                logger.error(f"Failed to load template image: {template}")
                return False
            
            # Perform template matching
            result = cv2.matchTemplate(image, template_img, cv2.TM_CCOEFF_NORMED)
            max_val = np.max(result)
            
            logger.debug(f"Template matching result for {template}: max_val={max_val:.3f}, threshold={threshold}")
            
            exists = np.any(result >= threshold)
            inference_time = time.time() - start_time
            if exists:
                logger.debug(f"Object found in template {template} with confidence {max_val:.3f}, time={inference_time:.4f}s")
                logger.info(f"Object found in template {template} with confidence {max_val:.3f}, time={inference_time:.4f}s")
            else:
                logger.debug(f"Object not found in template {template}, best match: {max_val:.3f}")         
            return exists
            
        except Exception as e:
            error_msg = f"Error in check_object_exists for template {template}: {e}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return False

    def check_object_exists_directory(self, image, template_dir, threshold=0.9):
        """
        Kiểm tra xem đối tượng có tồn tại trong ảnh dựa trên các mẫu trong thư mục.
        :param image: Ảnh gốc (numpy array).
        :param template_dir: Thư mục chứa các mẫu (string).
        :param threshold: Ngưỡng tương đồng để xác định sự tồn tại.
        :return: True nếu ít nhất một mẫu tồn tại, ngược lại False.
        """
        try:
            if not os.path.exists(template_dir):
                logger.error(f"Template directory not found: {template_dir}")
                return False
            
            if not os.path.isdir(template_dir):
                logger.error(f"Template path is not a directory: {template_dir}")
                return False
            
            logger.debug(f"Checking objects in directory: {template_dir}")
            
            for filename in os.listdir(template_dir):
                if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                    template_path = os.path.join(template_dir, filename)
                    try:
                        if self.check_object_exists(image, template_path, threshold):
                            logger.debug(f"Object found using template: {filename}")
                            return True
                    except Exception as e:
                        logger.warning(f"Error checking template {filename}: {e}")
                        continue
            
            logger.debug(f"No objects found in directory: {template_dir}")
            return False
            
        except Exception as e:
            error_msg = f"Error in check_object_exists_directory for {template_dir}: {e}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return False

    def find_object_directory(self, image, template_dir, threshold=0.9):
        """
        Tìm vị trí của đối tượng trong ảnh dựa trên các mẫu trong thư mục.
        :param image: Ảnh gốc (numpy array).
        :param template_dir: Thư mục chứa các mẫu (string).
        :param threshold: Ngưỡng tương đồng để xác định vị trí.
        :return: Vị trí tâm (x, y) tròn chính giữa của đối tượng nếu tìm thấy, ngược lại None.
        """
        try:
            if not os.path.exists(template_dir):
                logger.error(f"Template directory not found: {template_dir}")
                return None
            
            if not os.path.isdir(template_dir):
                logger.error(f"Template path is not a directory: {template_dir}")
                return None
            
            logger.debug(f"Finding objects in directory: {template_dir}")
            
            for filename in os.listdir(template_dir):
                if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                    template_path = os.path.join(template_dir, filename)
                    try:
                        position = self.find_object_position(image, template_path, threshold)
                        if position is not None:
                            logger.debug(f"Object found using template {filename} at position {position}")
                            return position
                    except Exception as e:
                        logger.warning(f"Error finding object with template {filename}: {e}")
                        continue
            
            logger.debug(f"No objects found in directory: {template_dir}")
            return None
            
        except Exception as e:
            error_msg = f"Error in find_object_directory for {template_dir}: {e}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return None

    def find_object_position(self, image, template, threshold=0.9):
        """
        Tìm vị trí của đối tượng trong ảnh dựa trên mẫu.
        :param image: Ảnh gốc (numpy array).
        :param template: Mẫu cần tìm (numpy array).
        :param threshold: Ngưỡng tương đồng để xác định vị trí.
        :return: Vị trí tâm (x, y) tròn chính giữa của đối tượng nếu tìm thấy, ngược lại None.
        """
        start_time = time.time()
        try:
            if image is None:
                logger.error("Input image is None")
                return None
                
            if template is None:
                logger.error("Template path is None")
                return None
            
            # Check if template file exists
            if not os.path.exists(template):
                logger.error(f"Template file not found: {template}")
                return None
            
            # Load template image
            template_img = cv2.imread(template, cv2.IMREAD_COLOR)
            if template_img is None:
                logger.error(f"Failed to load template image: {template}")
                return None
            
            # Check image dimensions
            if image.shape[0] < template_img.shape[0] or image.shape[1] < template_img.shape[1]:
                logger.warning(f"Image too small for template {template}. Image: {image.shape}, Template: {template_img.shape}")
                return None
            
            # Perform template matching
            result = cv2.matchTemplate(image, template_img, cv2.TM_CCOEFF_NORMED)
            yloc, xloc = np.where(result >= threshold)
            
            if len(xloc) == 0 or len(yloc) == 0:
                max_val = np.max(result)
                logger.debug(f"No match found for template {template}. Best match: {max_val:.3f}, threshold: {threshold}")
                return None
            
            # Find the best match (highest confidence)
            best_idx = np.argmax(result)
            best_y, best_x = np.unravel_index(best_idx, result.shape)
            confidence = result[best_y, best_x]
            
            # Calculate center position
            x = int(best_x + template_img.shape[1] / 2)
            y = int(best_y + template_img.shape[0] / 2)
            inference_time = time.time() - start_time
            logger.info(f"Found {template.split('/')[-1]}: conf={confidence:.3f}, time={inference_time:.4f}s")
            return (x, y)
            
        except Exception as e:
            error_msg = f"Error in find_object_position for template {template}: {e}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return None

    def wait_until_found(self, device, template, threshold=0.9, timeout=10):
        """
        Chờ cho đến khi tìm thấy đối tượng trong ảnh.
        :param device: Device ID.
        :param template: Mẫu cần tìm (string).
        :param threshold: Ngưỡng tương đồng để xác định vị trí.
        :param timeout: Thời gian chờ tối đa (giây).
        :return: Vị trí tâm (x, y) tròn chính giữa của đối tượng nếu tìm thấy, ngược lại None.
        """
        try:
            logger.info(f"Waiting for object {template} on device {device} (timeout: {timeout}s)")
            
            start_time = cv2.getTickCount()
            attempts = 0
            
            while True:
                attempts += 1
                
                try:
                    # Capture screenshot
                    img = self.adb.capture(device)
                    if img is None:
                        logger.warning(f"Failed to capture screenshot on attempt {attempts}")
                        time.sleep(0.5)
                        continue
                    
                    # Try to find object
                    position = self.find_object_position(img, template, threshold)
                    if position is not None:
                        elapsed = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
                        logger.info(f"Object {template} found after {elapsed:.2f}s ({attempts} attempts)")
                        return position
                    
                    # Check timeout
                    elapsed = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
                    if elapsed > timeout:
                        logger.warning(f"Timeout waiting for object {template} after {elapsed:.2f}s")
                        return None
                    
                    # Wait before next attempt
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.warning(f"Error in attempt {attempts}: {e}")
                    time.sleep(0.5)
                    continue
                    
        except Exception as e:
            error_msg = f"Error in wait_until_found for template {template}: {e}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return None

    def get_image_info(self, image):
        """Get basic information about an image for debugging"""
        try:
            if image is None:
                return "Image is None"
            
            height, width = image.shape[:2]
            channels = image.shape[2] if len(image.shape) > 2 else 1
            dtype = str(image.dtype)
            
            return f"Size: {width}x{height}, Channels: {channels}, Type: {dtype}"
            
        except Exception as e:
            return f"Error getting image info: {e}"