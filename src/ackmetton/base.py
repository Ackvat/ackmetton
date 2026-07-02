from ackmetton.platform import is_cpython, is_micropython

if is_cpython():
    import os
    import logging
    import serial as UART
    from smbus2 import SMBus as I2C
    from queue import Queue

if is_micropython():
    from machine import UART, I2C, Pin
    from utils import ListQueue as Queue

from datetime import datetime

from ackmetton.enums import FEED_LEVELS, SERIAL_ENUMS


# The very base class that consist variables and methods that shall be owned by all the other classes in this project library.
class Base:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "NONAME")

        # This is here to keep conditioning to have as less steps as possible later on.
        self.is_cpython = is_cpython()


# A general logger that can be used by multiple classes at the same time. The classes log with their names through the logger via a wrapper set below.
class Logger(Base):
    def __init__(self, **kwargs):
        if not self.is_cpython:
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

    def info(self, msg):
        if self.printer_level >= FEED_LEVELS.INFO:
            print(
                self.format(
                    time=self.time_now(),
                    level="INFO",
                    msg=msg,
                )
            )

    def warn(self, msg):
        if self.printer_level >= FEED_LEVELS.WARNING:
            print(
                self.format(
                    time=self.time_now(),
                    level="WARN",
                    msg=msg,
                )
            )

    def error(self, msg):
        if self.printer_level >= FEED_LEVELS.ERROR:
            print(
                self.format(
                    time=self.time_now(),
                    level="ERROR",
                    msg=msg,
                )
            )


# The very first class that is capable of printing and logging.
class Logged(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = kwargs.get("logger", None)

        if self.logger and self.is_cpython:
            self.log = LogWrap(self.logger, self.name)

        self.print = kwargs.get("printer", Printer(printer_name=self.name))


# test_logger = Logger(logger_name="testlog")
# test = Logged(name="TEST", logger=test_logger)
# test.log.debug("Hello World!")


# The basic module base class for creating electronic modules.
class Module(Logged):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.open: bool = kwargs.get("open", False)
        self.running: bool = kwargs.get("running", False)

    def Open(self) -> bool:
        self.open = True
        return True

    def Close(self) -> bool:
        self.open = False
        return True

    # NOTE: This one returns a boolean with respect to the current state of the module.
    def Switch(self) -> bool:
        self.open = not self.open
        if self.open:
            return True
        else:
            return False

    def Run(self):
        self.running = True
        return True

    def Stop(self):
        self.running = False
        return True


# A module class with UART communication protocol.
class UARTBase(Module):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # For virtual FIFO managing.
        self.in_queue = kwargs.get("inQueue", Queue())
        self.out_queue = kwargs.get("outQueue", Queue())

        self.serial_open: bool = False
        self.ser = kwargs.get("serial", None)
        self.port = kwargs.get("port", "/dev/ttyAMA0")
        self.baudrate = kwargs.get("baudrate", 9600)
        self.timeout = kwargs.get("timeout", 1)
        self.parity = kwargs.get("parity", SERIAL_ENUMS.PARITY_NONE)
        self.stopbits = kwargs.get("stopbits", SERIAL_ENUMS.STOPBITS_ONE)
        self.bytesize = kwargs.get("bytesize", SERIAL_ENUMS.EIGHTBITS)

        self.tx = kwargs.get("tx", 0)
        self.rx = kwargs.get("rx", 1)

    def Show_Port(self, show_method):
        msg = f"Adress: {self.port} | TX: {self.tx} | RX: {self.rx} with {self.baudrate} baudrate."
        if show_method == "log" and self.is_cpython:
            self.log.info(msg)
        elif show_method == "print":
            self.print.info(msg)

    def Open_Serial(self) -> bool:
        self.log.info("UART interface opening...")
        if self.ser is None:
            try:
                if self.is_cpython:
                    self.ser = UART.Serial(
                        port=self.port,
                        baudrate=self.baudrate,
                        timeout=self.timeout,
                        parity=self.parity,
                        stopbits=self.stopbits,
                        bytesize=self.bytesize,
                    )
                else:
                    self.ser = UART(
                        1,
                        baudrate=self.baudrate,
                        tx=self.tx,
                        rx=self.rx,
                        bits=self.bytesize,
                        parity=SERIAL_ENUMS.GetMicroParity(self.parity),
                        stop=self.stopbits,
                    )
                self.log.info("UART interface initiated successfully.")
                self.Show_Port("log")
                self.serial_open = True
                return True
            except Exception as error:
                self.log.error(
                    f"An error has occured during UART interface initiation! {error}"
                )
                self.serial_open = False
                return False
        else:
            if not self.serial_open:
                try:
                    if self.is_cpython:
                        self.ser.open()
                    else:
                        pass
                    self.ser.flush()
                    self.log.info("UART interface was found and started.")
                    self.Show_Port("log")
                    self.serial_open = True
                    return True
                except Exception as error:
                    self.log.error(
                        f"UART interface was found but an error has occured while starting it! {error}"
                    )
                    return False
            else:
                self.log.warn("UART interface already exists and is open.")
                self.Show_Port("log")
                self.serial_open = True
                return True

    def Close_Serial(self):
        self.log.info("UART interface is closing...")
        if self.ser is None:
            self.log.warn("There were no UART interface found to close.")
            self.serial_open = False
            return True
        else:
            try:
                if self.is_cpython:
                    self.ser.close()
                else:
                    self.ser.deinit()
                self.ser = None
                self.log.info("UART interface was found and closed.")

                self.serial_open = False
                return True
            except Exception as error:
                self.log.error(
                    f"UART interface was found but an error occured while closing it! {error}"
                )
                return False

    def Change_Serial(self):
        self.log.info("UART interface is getting changed...")
        if self.Close_Serial():
            # TODO: To be added.
            pass

    def Write(self, data, new_line=True):
        if new_line:
            data += "\n"
        self.ser.write(data.encode("utf-8"))
        return True

    def Read(self, size=1):
        data = self.ser.read(size)
        if data:
            return data
        else:
            return None

    def ReadLine(self, size=1):
        data = self.ser.read(size).decode("utf-8").strip()
        if data:
            return data
        else:
            return None


class I2CBase(Module):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.queue = Queue()

        # TODO: Add specific pins and ports as dynamic and enumerated values.
        if self.is_cpython:
            self.i2c = I2C(1)
        else:
            self.i2c = I2C(0, 1, 2)
