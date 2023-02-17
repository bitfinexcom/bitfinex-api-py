import logging

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

RESET_SEQ = "\033[0m"

COLOR_SEQ = "\033[1;%dm"
ITALIC_COLOR_SEQ = "\033[3;%dm"
UNDERLINE_COLOR_SEQ = "\033[4;%dm"

BOLD_SEQ = "\033[1m"

def formatter_message(message, use_color = True):
    if use_color:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message

COLORS = {
    "DEBUG": CYAN,
    "INFO": BLUE,
    "WARNING": YELLOW,
    "ERROR": RED
}

class _ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color = True):
        logging.Formatter.__init__(self, msg, "%d-%m-%Y %H:%M:%S")
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            record.levelname = levelname_color
        record.name = ITALIC_COLOR_SEQ % (30 + BLACK) + record.name + RESET_SEQ
        return logging.Formatter.format(self, record)

class ColoredLogger(logging.Logger):
    FORMAT = "[$BOLD%(name)s$RESET] [%(asctime)s] [%(levelname)s] %(message)s"
    
    COLOR_FORMAT = formatter_message(FORMAT, True)
    
    def __init__(self, name, level):
        logging.Logger.__init__(self, name, level)                

        colored_formatter = _ColoredFormatter(self.COLOR_FORMAT)
        console = logging.StreamHandler()
        console.setFormatter(colored_formatter)

        self.addHandler(console)