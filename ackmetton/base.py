import os
import logging


class Base:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "Base")
        self.log_name = kwargs.get("log_name", str.strip(str.lower(self.name)))
        self.print_name = kwargs.get("print_name", str.strip(str.lower(self.name)))

        self.log_directory = kwargs.get("log_directory", "./logs/")
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)

        self.logger = kwargs.get("logger", logging.getLogger(self.log_name))
        self.logger.setLevel(kwargs.get("logging_level", logging.DEBUG))
        log_FileHandler = logging.FileHandler(
            f"{self.log_directory}{self.logger.name}.log", mode="w", encoding="utf-8"
        )
        log_FileHandler.setLevel(logging.DEBUG)
        log_Formatter = logging.Formatter("%(asctime)s | [%(levelname)s] | %(message)s")
        log_FileHandler.setFormatter(log_Formatter)
        self.logger.addHandler(log_FileHandler)

        # HACK: The below method is a global settings for all the loggers.
        # self.logger.basicConfig(
        # filename=f"{self.logname}.log",
        # filemode="w",
        # level=logging.DEBUG,
        # format="%(asctime)s | [%(levelname)s] | %(message)s",
        # datefmt="%Y/%m/%d %H:%M:%S",
        # )

    def Log(self, **kwargs):
        level = kwargs.get("level", "DEBUG")
        message = kwargs.get("msg", "Empty Log.")
        match level:
            case "DEBUG" | 4:
                self.logger.debug(message)
            case "INFO" | 3:
                self.logger.info(message)
            case "WARN" | 2:
                self.logger.warn(message)
            case "ERROR" | 1:
                self.logger.error(message)
            case "CRIT" | 0:
                self.logger.critical(message)
            case _:
                self.logger.warn(f"[WRONG LOG LEVEL] {message}")

    def Set_Log_Level(self, **kwargs):
        level = kwargs.get("level", "DEBUG")
        match level:
            case "DEBUG" | 4:
                self.logger.setLevel(logging.DEBUG)
            case "INFO" | 3:
                self.logger.setLevel(logging.INFO)
            case "WARN" | 2:
                self.logger.setLevel(logging.WARN)
            case "ERROR" | 1:
                self.logger.setLevel(logging.ERROR)
            case "CRIT" | 0:
                self.logger.setLevel(logging.CRITICAL)
            case _:
                self.logger.setLevel(logging.DEBUG)

    def Print(self, **kwargs):
        pass


test = Base(name="Test A")
testa = Base(name="Test B")
test.Log(level="DEBUG", msg="Hello World!")
testa.Log(level="DEBUG", msg="Hello World Too!")
