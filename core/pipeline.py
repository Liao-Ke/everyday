import logging

from core.chat import chat_ai

logger = logging.getLogger("每日故事")


def run_model(config: dict, *, chat_fn=None) -> dict | None:
    model_name = config.get("name", "unknown")

    params = {"chat_params": config["CHAT_PARAMS"], "client_params": config["CLIENT_PARAMS"]}

    for pre in config.get("PREPROCESSORS", []):
        logger.debug(f"[{model_name}] 前置处理器: {pre.__name__}")
        params = pre(params)

    chat_func = chat_fn or chat_ai
    response = chat_func(
        api_key=config["API_KEY"],
        model_name=model_name,
        **params,
        initial_backoff=60,
        max_backoff=600,
        max_retries=5,
    )

    if response is None:
        logger.error(f"[{model_name}] 生成失败")
        return None

    for post in config.get("POSTPROCESSORS", []):
        logger.debug(f"[{model_name}] 后置处理器: {post.__name__}")
        response = post(response)

    for file_fn in config.get("POSTPROCESSOR_FILES", []):
        logger.debug(f"[{model_name}] 文件处理器: {file_fn.__name__}")
        file_fn(response, config)

    return response
