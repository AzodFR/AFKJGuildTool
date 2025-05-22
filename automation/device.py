import os
import sys
import easyocr
import numpy as np
import cv2

from logging import Logger
from ppadb.client import Client
from typing import Any
from subprocess import Popen, PIPE

class DeviceClient:

    def __init__(self, logger: Logger) -> None:
        self.device: Any | None = None
        self.adb: Client = Client(host="127.0.0.1", port=5037)
        self.adb_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "adbins", "adb.exe")
        self.logger: Logger = logger

    def __adb_server(self) -> bool:
        self.logger.info("Check if adb is installed and running")
        try:
            self.adb.devices()
            return True
        except Exception:
            self.logger.warning("adb server is not running, starting it")
            Popen([self.adb_path, "start-server"], stderr=PIPE).communicate()[0]
            try:
                self.adb.devices()
                return True
            except Exception:
                return False

    def connect_device(self, port=5556) -> Any | None:
       
        if not self.__adb_server():
            self.logger.critical("Could not run adb server")
            sys.exit(1)

        self.logger.info("Connecting to device")
        if not self.adb.remote_connect("127.0.0.1", port):
            self.logger.critical("Connection failed.")
            sys.exit(1)
        else:
            for device in self.adb.devices():
                if device.serial[-4:] == str(port):
                    self.device = device
                    break
            if self.device == None:
                self.logger.critical("Could not find connected device")
                sys.exit(1)
            self.logger.info("Connected to: "+self.device.serial)
        return self.device
    
    def get_device(self) -> Any | None:
        return self.device

    def disconnect_device(self, port=5556) -> None:
            self.logger.info("Disconnecting from: "+ self.device.serial)
            self.adb.remote_disconnect("127.0.0.1", port)

    def get_frame(self):
        screencap = self.device.screencap()
        img_array = np.frombuffer(screencap, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    def click_first_user(self):
        self.locate_and_click("assets/guild/members/power.png", x_modifier=-75)

    def click_power(self):
        self.locate_and_click("assets/guild/members/power_2.png", y_modifier=-5)

    def locate_and_click(self,
        target_path,
        x_modifier=0,
        y_modifier=0
    ):
        target = cv2.imread(target_path, cv2.IMREAD_GRAYSCALE)
        screenshot = self.get_frame()
        result = cv2.matchTemplate(screenshot, target, cv2.TM_CCOEFF_NORMED)
        cv2.imwrite("debug.png", screenshot)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        threshold = 0.8
        if max_val >= threshold:
            self.logger.info(f"Found match with confidence: {max_val:.2f}")
            h, w = target.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2

            self.device.shell(f"input tap {center_x+x_modifier} {center_y+y_modifier}")
        else:
            self.logger.info("Image not found.")
        

    def ocr(self, image):
        reader = easyocr.Reader(['fr','en'], gpu=True)
        result = reader.readtext(image, detail=0)
        self.logger.info(result)
