import sys


def is_micropython() -> bool:
    return hasattr(sys, "implementation") and sys.implementation.name == "micropython"


def is_python() -> bool:
    return not is_micropython() and sys.platform.startswith("linux")
