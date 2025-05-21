import logging
import sys

def init_logger(tool_version: str) -> logging.Logger:
    logger = logging.getLogger("afkjgt")

    logfile = logging.FileHandler("afkjgt.log")
    logfile.setFormatter(logging.Formatter(f"({tool_version}) [%(asctime)s] %(message)s"))

    logger.addHandler(logfile)

    logging.StreamHandler(stream=sys.stderr)
    logging.basicConfig(
        format=f"({tool_version}) [%(asctime)s] %(message)s", datefmt="%H:%M:%S", level=logging.INFO
    )

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.error(
            "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = handle_exception

    return logger