from enum import Enum, IntEnum


class FEED_LEVELS(IntEnum):
    NOTSET = 0
    DEBUG = 10
    INFO = 20
    WARNING = 30
    WARN = 30
    ERROR = 40
    CRIT = 50
    CRITICAL = 50
    FATAL = 50
