import logging


def setup_logger():
    # 创建日志器
    _logger = logging.getLogger('每日故事')
    _logger.setLevel(logging.DEBUG)  # 设置日志级别为DEBUG，这样所有级别的日志都会被处理

    # 创建文件处理器，用于将日志写入文件
    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.INFO)  # 文件处理器只记录INFO及以上级别的日志

    # 创建控制台处理器，用于将日志输出到控制台
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # 控制台处理器记录DEBUG及以上级别的日志

    # 创建日志格式器并添加到处理器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 将处理器添加到日志器
    _logger.addHandler(file_handler)
    _logger.addHandler(console_handler)

    return _logger
