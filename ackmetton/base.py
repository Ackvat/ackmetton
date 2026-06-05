import os
import logging
from datetime import datetime

from enums import FEED_LEVELS


class Base:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "NONAME")


class Logger(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger_name: str = kwargs.get("logger_name", "nonamelog").strip().lower()
        self.logger = kwargs.get("logger", logging.getLogger(self.logger_name))

        self.logger.setLevel(kwargs.get("log_level", FEED_LEVELS.DEBUG))

        self.log_directory: str = kwargs.get("log_directory", "./logs/")
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)
        self.log_file: str = kwargs.get("log_file", self.logger_name)
        log_FileHandler = logging.FileHandler(
            f"{self.log_directory}{self.log_file}.log", mode="w", encoding="utf-8"
        )
        log_FileHandler.setLevel(FEED_LEVELS.DEBUG)
        # The basic format for the logging.
        log_Formatter = logging.Formatter("%(asctime)s | [%(levelname)s]\t%(message)s")
        log_FileHandler.setFormatter(log_Formatter)
        self.logger.addHandler(log_FileHandler)

        # The deep format for the logger so that object names can be included in the logs per log file.
        self.format = lambda name, msg: f"[{name}] {msg}"

    def debug(self, name, msg):
        self.logger.debug(self.format(name, msg))

    def info(self, name, msg):
        self.logger.info(self.format(name, msg))

    def warn(self, name, msg):
        self.logger.warning(self.format(name, msg))

    def error(self, name, msg):
        self.logger.error(self.format(name, msg))


class LogWrap:
    def __init__(self, logger, name):
        self._logger = logger
        self._name = name

    def __getattr__(self, level):
        if hasattr(self._logger, level):

            def wrapper(msg):
                getattr(self._logger, level)(self._name, msg)

            return wrapper
        raise AttributeError(f"'{type(self).__name__}' has no method '{level}'")


class Printer(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.print_name: str = kwargs.get("print_name", "baseprint").strip().lower()
        self.print_level = kwargs.get("print_level", FEED_LEVELS.DEBUG)
        self.time_now = lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.format = lambda time, level, msg: f"{time} | [{level}] {msg}"

    def debug(self, msg):
        if self.print_level >= FEED_LEVELS.DEBUG:
            print(
                self.format(
                    time=self.time_now(),
                    level="DEBUG",
                    msg=msg,
                )
            )


class Adem(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = kwargs.get("logger", None)
        self.print = kwargs.get("printer", None)

        if self.logger:
            self.log = LogWrap(self.logger, self.name)


test_logger = Logger(logger_name="testlog")
test = Adem(name="TEST", logger=test_logger)
test.log.debug("Hello World!")
test.log.info("Hello World!")
test.log.warn("Hello World!")
test.log.error("Hello World!")
