from platform import is_cpython, is_micropython

if is_cpython():
    import os
    import logging
    from smbus2 import SMBus
    from queue import Queue
    import serial

if is_micropython():
    from machine import UART, I2C, Pin
    from utils import ListQueue as Queue

from datetime import datetime

import enums

FEED_LEVELS = enums.FEED_LEVELS


# The very base class that consist variables and methods that shall be owned by all the other classes in this project library.
class Base:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "NONAME")


# A general logger that can be used by multiple classes at the same time. The classes log with their names through the logger via a wrapper set below.
class Logger(Base):
    def __init__(self, **kwargs):
        if is_micropython():
            raise ImportError(
                "Logger unavailable on MicroPython, requires stdlib 'logging'"
            )

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


# This is the logger wrapper that allows easy calling of the logger functions from classes equal ro higher than Adem.
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
        self.printer_name: str = (
            kwargs.get("printer_name", "nonameprint").strip().lower()
        )
        self.printer_level = kwargs.get("printer_level", FEED_LEVELS.DEBUG)

        # The formattings for the prinings.
        self.time_now = lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.format = lambda time, level, msg: f"{time} | [{level}] {msg}"

    def debug(self, msg):
        if self.printer_level >= FEED_LEVELS.DEBUG:
            print(
                self.format(
                    time=self.time_now(),
                    level="DEBUG",
                    msg=msg,
                )
            )


# The very first class that is capable of printing and logging.
class Logged(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = kwargs.get("logger", None)
        self.print = kwargs.get("printer", None)

        if self.logger and is_python():
            self.log = LogWrap(self.logger, self.name)


# test_logger = Logger(logger_name="testlog")
# test = Logged(name="TEST", logger=test_logger)
# test.log.debug("Hello World!")


# The basic module base class for creating electronic modules.
class Module(Logged):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.open: bool = kwargs.get("open", False)
        self.running: bool = kwargs.get("running", False)

    def Open(self):
        self.open = True

    def Close(self):
        self.open = False

    def Switch(self):
        self.open = not self.open

    def Run(self):
        self.running = True

    def Stop(self):
        self.running = False


# A module class with UART communication protocol.
class UARTBase(Module):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # For virtual FIFO managing.
        self.inQueue = kwargs.get("inQueue", Queue())
        self.outQueue = kwargs.get("outQueue", Queue())

        self.ser = kwargs.get("serial", None)
        self.port = kwargs.get("port", "/dev/ttyAMA0")
        self.baudrate = kwargs.get("baudrate", 9600)
        self.timeout = kwargs.get("timeout", 1)
        self.parity = kwargs.get("parity", None)

    def OpenSerial(self):
        self.log.info("UART interface initiating...")
        if self.ser is None:
            try:
                if is_cpython():
                    self.ser = serial.Serial(
                        port=self.port,
                        baudrate=self.baudrate,
                        timeout=self.timeout,
                        parity=self.parity,
                        stopbits=self.stopbits,
                        bytesize=self.bytesize,
                    )
            except Exception as error:
                self.log.error(
                    f"An error has occured during UART interface initiation! {error}"
                )
                return False
