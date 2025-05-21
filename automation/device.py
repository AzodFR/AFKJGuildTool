from logging import Logger
from ppadb.client import Client
from typing import Any
from subprocess import Popen, PIPE
import os
import sys
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
            self.logger.info("Taking screenshot...")
            result = self.device.screencap()
            with open("screen.png", "wb") as fp:
                fp.write(result)
            self.logger.info("Disconnecting from: "+self.device.serial)
            self.adb.remote_disconnect("127.0.0.1", port)
