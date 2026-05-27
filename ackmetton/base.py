import logging


class Base:
    def __init__(self, **kwargs):
        self.name = "Base"
        self.logname = str.strip(str.lower(self.name))
        self.printname = str.strip(str.lower(self.name))

        self.logger = kwargs.get("logger", logging.getLogger(self.logname))
        self.logger.setLevel(kwargs.get("loggingLevel", logging.DEBUG))
        log_FileHandler = logging.FileHandler(
            f"{self.logname}.log", mode="w", encoding="utf-8"
        )
        log_FileHandler.setLevel(logging.INFO)
        log_Formatter = logging.Formatter("%(asctime)s | [%(levelname)s] | %(message)s")
        log_FileHandler.setFormatter(log_Formatter)

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
            case "DEBUG":
                self.logger.debug(message)
            case "INFO":
                self.logger.info(message)
            case "WARN":
                self.logger.warn(message)
            case "ERROR":
                self.logger.error(message)
            case "CRIT":
                self.logger.critical(message)


test = Base()
test.Log(level="DEBUG", msg="Hello World!")
