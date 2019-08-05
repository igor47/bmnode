import logging


def log_config(level: int = logging.DEBUG) -> None:
    stream = logging.StreamHandler()

    root = logging.getLogger()
    root.addHandler(stream)
    root.setLevel(level)
