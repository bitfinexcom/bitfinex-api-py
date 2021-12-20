from ..utils.custom_logger import CustomLogger


def handle_failure(func):
    def inner_function(*args, **kwargs):
        logger = CustomLogger('BfxWebsocket', logLevel="DEBUG")
        try:
            func(*args, **kwargs)
        except Exception as exception_message:
            logger.error(exception_message)

    return inner_function
