from logging import Logger

from metadata.module import Metadata
from utility import utils_log
from automation import device

def main() -> None:
    metadata = Metadata()
    logger: Logger = utils_log.init_logger(metadata.version)
    logger.info("Tool started.")
    bot = device.DeviceClient(logger)
    bot.connect_device()
if __name__ == "__main__":
    main()
