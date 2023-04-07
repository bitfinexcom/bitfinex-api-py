import logging, sys

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

COLOR_SEQ, ITALIC_COLOR_SEQ = "\033[1;%dm", "\033[3;%dm"

COLORS = {
    "DEBUG": CYAN,
    "INFO": BLUE,
    "WARNING": YELLOW,
    "ERROR": RED
}

RESET_SEQ = "\033[0m"

class _ColorFormatter(logging.Formatter):
    def __init__(self, msg, use_color = True):
        logging.Formatter.__init__(self, msg, "%d-%m-%Y %H:%M:%S")

        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            record.name = ITALIC_COLOR_SEQ % (30 + BLACK) + record.name + RESET_SEQ
            record.levelname = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
        return logging.Formatter.format(self, record)

class ColorLogger(logging.Logger):
    FORMAT = "[%(name)s] [%(levelname)s] [%(asctime)s] %(message)s"

    def __init__(self, name, level):
        logging.Logger.__init__(self, name, level)

        colored_formatter = _ColorFormatter(self.FORMAT, use_color=True)
        handler = logging.StreamHandler(stream=sys.stderr)
        handler.setFormatter(fmt=colored_formatter)

        self.addHandler(hdlr=handler)

class FileLogger(logging.Logger):
    FORMAT = "[%(name)s] [%(levelname)s] [%(asctime)s] %(message)s"

    def __init__(self, name, level, filename):
        logging.Logger.__init__(self, name, level)

        formatter = logging.Formatter(self.FORMAT)
        handler = logging.FileHandler(filename=filename)
        handler.setFormatter(fmt=formatter)

        self.addHandler(hdlr=handler)
