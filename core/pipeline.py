import logging

from core.chat import chat_ai

logger = logging.getLogger("每日故事")


def run_model(config: dict, *, chat_fn=None) -> dict | None:
    model_name = config.get("name", "unknown")
    logger.info(f"开始处理模型: {model_name}")

    params = {"chat_params": config["CHAT_PARAMS"], "client_params": config["CLIENT_PARAMS"]}

    for pre in config.get("PREPROCESSORS", []):
        logger.info(f"前置处理器: {pre.__name__}")
        params = pre(params)

    chat_func = chat_fn or chat_ai
    response = chat_func(
        api_key=config["API_KEY"],
        **params,
        initial_backoff=60,
        max_backoff=600,
        max_retries=5,
    )

    if response is None:
        logger.error(f"模型 {model_name} 生成失败")
        return None

    for post in config.get("POSTPROCESSORS", []):
        logger.info(f"后置处理器: {post.__name__}")
        response = post(response)

    for file_fn in config.get("POSTPROCESSOR_FILES", []):
        logger.info(f"文件处理器: {file_fn.__name__}")
        file_fn(response, config)

    logger.info(f"模型 {model_name} 处理完成")
    return response
