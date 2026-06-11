import logging

_logger_initialized = False


def setup_logger():
    global _logger_initialized
    if _logger_initialized:
        return logging.getLogger("每日故事")
    _logger_initialized = True

    _logger = logging.getLogger("每日故事")
    _logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler("app.log")
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    _logger.addHandler(file_handler)
    _logger.addHandler(console_handler)

    return _logger
