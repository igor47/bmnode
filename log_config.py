import logging

class BMNodeFormatter(logging.Formatter):
    def formatMessage(self, record):
        prefix = "%(levelname)s %(name)s" % record.__dict__
        return f"{prefix} : {record.message}"

def log_config(level: int = logging.DEBUG) -> None:
    root = logging.getLogger()
    root.setLevel(level)

    # configure default handler as a stream handler
    stream = logging.StreamHandler()
    stream.setFormatter(BMNodeFormatter())
    root.addHandler(stream)
