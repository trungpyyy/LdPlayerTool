import cv2
import numpy as np
from utils import AdbProcess

class Detect:
    def __init__(self, adb: AdbProcess):
        self.adb = adb

    def check_object_exists(self, image, template, threshold=0.9):
        """
        Kiểm tra xem đối tượng có tồn tại trong ảnh hay không.
        :param image: Ảnh gốc (numpy array).
        :param template: Mẫu cần tìm (numpy array).
        :param threshold: Ngưỡng tương đồng để xác định sự tồn tại.
        :return: True nếu đối tượng tồn tại, ngược lại False.
        """
        template = cv2.imread(template, cv2.IMREAD_COLOR)
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        return np.any(result >= threshold)

    def check_object_exists_directory(self, image, template_dir, threshold=0.9):
        """
        Kiểm tra xem đối tượng có tồn tại trong ảnh dựa trên các mẫu trong thư mục.
        :param image: Ảnh gốc (numpy array).
        :param template_dir: Thư mục chứa các mẫu (string).
        :param threshold: Ngưỡng tương đồng để xác định sự tồn tại.
        :return: True nếu ít nhất một mẫu tồn tại, ngược lại False.
        """
        import os
        for filename in os.listdir(template_dir):
            if filename.endswith(".png") or filename.endswith(".jpg"):
                template_path = os.path.join(template_dir, filename)
                if self.check_object_exists(image, template_path, threshold):
                    return True
        return False

    def find_object_directory(self, image, template_dir, threshold=0.9):
        """
        Tìm vị trí của đối tượng trong ảnh dựa trên các mẫu trong thư mục.
        :param image: Ảnh gốc (numpy array).
        :param template_dir: Thư mục chứa các mẫu (string).
        :param threshold: Ngưỡng tương đồng để xác định vị trí.
        :return: Vị trí tâm (x, y) tròn chính giữa của đối tượng nếu tìm thấy, ngược lại None.
        """
        import os
        for filename in os.listdir(template_dir):
            if filename.endswith(".png") or filename.endswith(".jpg"):
                template_path = os.path.join(template_dir, filename)
                position = self.find_object_position(image, template_path, threshold)
                if position is not None:
                    return position
        return None

    def find_object_position(self, image, template, threshold=0.9):
        """
        Tìm vị trí của đối tượng trong ảnh dựa trên mẫu.
        :param image: Ảnh gốc (numpy array).
        :param template: Mẫu cần tìm (numpy array).
        :param threshold: Ngưỡng tương đồng để xác định vị trí.
        :return: Vị trí tâm (x, y) tròn chính giữa của đối tượng nếu tìm thấy, ngược lại None.
        """
        if image is None or template is None:
            print("[LỖI] Ảnh hoặc template là None!")
            return None    
        template = cv2.imread(template, cv2.IMREAD_COLOR)
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        yloc, xloc = np.where(result >= threshold)
        if len(xloc) == 0 or len(yloc) == 0:
            return None
        # Tính trung tâm của đối tượng
        x = int(xloc[0] + template.shape[1] / 2)
        y = int(yloc[0] + template.shape[0] / 2)
        return (x, y)
    

    def wait_until_found(self, device, template, threshold=0.9, timeout=10):
        """
        Chờ cho đến khi tìm thấy đối tượng trong ảnh.
        :param image: Ảnh gốc (numpy array).
        :param template: Mẫu cần tìm (numpy array).
        :param threshold: Ngưỡng tương đồng để xác định vị trí.
        :param timeout: Thời gian chờ tối đa (giây).
        :return: Vị trí tâm (x, y) tròn chính giữa của đối tượng nếu tìm thấy, ngược lại None.
        """
        start_time = cv2.getTickCount()
        while True:
            position = self.find_object_position(self.adb.capture(device), template, threshold)
            if position is not None:
                return position
            if (cv2.getTickCount() - start_time) / cv2.getTickFrequency() > timeout:
                return None