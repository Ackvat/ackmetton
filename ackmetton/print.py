from enums import PRINT_LEVELS


class Printer:
    def __init__(self, **kwargs):
        self.level = kwargs.get("level", PRINT_LEVELS.DEBUG)
