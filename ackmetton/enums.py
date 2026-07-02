class SERIAL_VALUES:
    PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE = (
        "N",
        "E",
        "O",
        "M",
        "S",
    )

    STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO = (1, 1.5, 2)
    FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS = (5, 6, 7, 8)

    PARITY_NAMES = {
        PARITY_NONE: "None",
        PARITY_EVEN: "Even",
        PARITY_ODD: "Odd",
        PARITY_MARK: "Mark",
        PARITY_SPACE: "Space",
    }


class FEED_LEVELS:
    NOTSET = 0
    DEBUG = 10
    INFO = 20
    WARNING = 30
    WARN = 30
    ERROR = 40
    CRIT = 50
    CRITICAL = 50
    FATAL = 50
