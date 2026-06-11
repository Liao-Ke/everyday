import os
import time
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue

from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI, RateLimitError

from config.logger_setup import setup_logger
from core.registry import ModelRegistry
from utils.metadata_utils import process_stream_chunks, save_chat_metadata

# 获取配置好的日志器
logger = setup_logger()


# 可选择禁用的模型列表
EXCLUDED_MODELS: set[str] = {"doubao_think", "kimi", "zhipu_z1_flash"}


def chat_ai(
    api_key: str,
    client_params: dict,
    chat_params: dict,
    session_id: str = str(uuid.uuid4()),
    max_retries=3,
    initial_backoff=1,
    max_backoff=10,
):
    """
    调用 OpenAI API 进行聊天对话并获取响应，同时处理重试逻辑。

    Args:
        api_key (str): 用于访问 AI大模型 的密钥。
        client_params (dict): 初始化 AI大模型 客户端时使用的参数。
        chat_params (dict): 调用聊天完成接口时使用的参数。
        session_id (str, optional): 会话的唯一标识符，默认为一个新生成的 UUID。
        max_retries (int, optional): 最大重试次数，默认为 3 次。
        initial_backoff (int, optional): 初始退避时间（秒），默认为 1 秒。
        max_backoff (int, optional): 最大退避时间（秒），默认为 10 秒。

    Returns:
        dict | None: 包含响应消息的字典，如果请求失败则返回 None。
    """
    # 初始化计时器
    start_time = time.time()
    retries = 0
    is_stream = chat_params.get("stream", False)
    params_copy = chat_params.copy()
    is_retry = params_copy.pop("RETRY", True)

    while retries <= (max_retries if is_retry else 0):
        try:
            if retries > 0:
                logger.info(f"第{retries}次等待结束，开始第 {retries + 1} 次重试")

            client = OpenAI(api_key=api_key, **client_params)

            response = client.chat.completions.create(**chat_params)
            # 记录响应耗时
            response_time = time.time() - start_time
            if not is_stream:
                # 获取响应内容
                response_content = response.choices[0].message.model_dump() or ""

                # 保存完整的对话记录（包含原始响应）
                save_chat_metadata(
                    response_time=response_time,
                    session_id=session_id,
                    response_data=response.to_dict(),
                    client_params=client_params,
                    chat_params=chat_params,
                )

                if not response_content["content"]:
                    raise ValueError("响应内容为空")

                return response_content
            else:
                content_chunks = []
                reasoning_chunks = []
                full_response = []
                for chunk in response:
                    full_response.append(chunk)
                    if chunk.choices:
                        if chunk.choices[0].delta.content:
                            # 确保 content_chunks 是列表类型
                            if not isinstance(content_chunks, list):
                                content_chunks = [content_chunks]
                            content_chunks.append(chunk.choices[0].delta.content)
                        if (
                            hasattr(chunk.choices[0].delta, "reasoning_content")
                            and chunk.choices[0].delta.reasoning_content
                        ):
                            reasoning_chunks.append(chunk.choices[0].delta.reasoning_content)
                response_content = {"content": "".join(content_chunks)}
                if reasoning_chunks:
                    response_content["reasoning_content"] = "".join(reasoning_chunks)
                save_chat_metadata(
                    response_time=response_time,
                    session_id=session_id,
                    response_data=process_stream_chunks(full_response),
                    client_params=client_params,
                    chat_params=chat_params,
                )

                if not response_content["content"]:
                    raise ValueError("响应内容为空")

                return response_content

        # 异常处理（按优先级排序）
        except RateLimitError as e:
            # 专门处理速率限制错误

            backoff_time = min(initial_backoff * (2**retries) * 2, max_backoff)  # 比普通错误等待更久

            logger.warning(f"API速率限制错误，第 {retries + 1} 次重试，将等待 {backoff_time:.2f} 秒: {str(e)}")

            # 尝试从错误信息中提取重试建议时间

            retry_after = getattr(e, "retry_after", None)

            if retry_after and retry_after > backoff_time:
                logger.info(f"使用API建议的重试时间: {retry_after}秒")

                backoff_time = retry_after
        except APITimeoutError as e:
            backoff_time = min(initial_backoff * (2**retries), max_backoff)
            logger.error(f"请求超时，第 {retries + 1} 次重试，将等待 {backoff_time:.2f} 秒: {str(e)}")

        except (APIConnectionError, APIStatusError) as e:
            backoff_time = min(initial_backoff * (2**retries), max_backoff)
            logger.error(f"API错误，第 {retries + 1} 次重试，将等待 {backoff_time:.2f} 秒: {str(e)}")

        except ValueError as e:
            backoff_time = min(initial_backoff * (2**retries), max_backoff)
            logger.error(f"值错误: {str(e)}，第 {retries + 1} 次重试，将等待 {backoff_time:.2f} 秒")

        except Exception as e:
            backoff_time = min(initial_backoff * (2**retries), max_backoff)
            logger.critical(f"严重错误: {str(e)}，第 {retries + 1} 次重试，将等待 {backoff_time:.2f} 秒", exc_info=True)

        retries += 1
        if retries < max_retries:
            time.sleep(backoff_time)  # 使用指数退避计算的时间等待
    logger.error(f"所有 {max_retries} 次重试均失败")
    return None


def story_generator(model_name, config, result_queue=None):
    try:
        logger.info(f"已启动模型 {model_name} 的生成线程")
        params = {"chat_params": config["CHAT_PARAMS"], "client_params": config["CLIENT_PARAMS"]}

        logger.info(f"模型 {model_name} 开始应用前置处理器")
        for preprocessor in config.get("PREPROCESSORS", []):
            logger.info(f"正在应用前置处理器 {preprocessor.__name__}")
            params = preprocessor(params)
            logger.info(f"前置处理器 {preprocessor.__name__} 已应用")
        logger.info(f"模型 {model_name} 前置处理器应用完成")

        logger.info(f"模型 {model_name} 开始调用AI生成故事")
        r = chat_ai(api_key=config["API_KEY"], **params, initial_backoff=60, max_backoff=600, max_retries=5)
        logger.info(f"模型 {model_name} AI生成故事完成")
        if r is None:
            logger.error(f"模型 {model_name} 生成故事失败，跳过后置处理器")
        else:
            logger.info(f"模型 {model_name} 开始应用后置处理器")
            for processor in config.get("POSTPROCESSORS", []):
                logger.info(f"正在应用后置处理器 {processor.__name__}")
                r = processor(r)
                logger.info(f"后置处理器 {processor.__name__} 已应用")
            logger.info(f"模型 {model_name} 后置处理器应用完成")

            logger.info(f"模型 {model_name} 开始应用文件后置处理器")
            for file_processor in config.get("POSTPROCESSOR_FILES", []):
                logger.info(f"正在应用文件后置处理器 {file_processor.__name__}")
                file_processor(r, config["name"])
                logger.info(f"文件后置处理器 {file_processor.__name__} 已应用")
            logger.info(f"模型 {model_name} 文件后置处理器应用完成")

        if result_queue is not None:
            result_queue.put((model_name, r))
        logger.info(f"模型 {model_name} 生成完成")
        return r
    except Exception as e:
        logger.error(f"模型 {model_name} 生成过程中出错: {str(e)}")
        return None


def run_multi_thread(selected_configs: list[tuple[str, dict]], max_workers=4):
    model_names = [name for name, _ in selected_configs]
    result_queue = Queue()
    logger.info(f"开始多线程故事生成，将使用模型: {', '.join(model_names)}，最大并发线程数: {max_workers}")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_model = {
            executor.submit(story_generator, name, config, result_queue): name for name, config in selected_configs
        }

        # 所有任务提交完成后，再处理结果
        for future in as_completed(future_to_model):
            model_name = future_to_model[future]
            try:
                # 获取结果（会重新抛出任务中的异常）
                future.result()
            except Exception as e:
                # 记录详细错误信息
                error_msg = f"模型 {model_name} 生成故事时出错: {str(e)}\n{traceback.format_exc()}"
                logger.error(error_msg)
                # 将错误信息放入结果队列
                result_queue.put((model_name, {"error": error_msg}))
    logger.info("所有模型的生成线程已完成")

    # 收集所有结果
    model_results = {}
    while not result_queue.empty():
        model_name, result = result_queue.get()
        model_results[model_name] = result
    return model_results


if __name__ == "__main__":
    logger.info("应用程序启动")

    configs = ModelRegistry.discover()
    available_models = [name for name in configs if name not in EXCLUDED_MODELS]
    logger.info(f"可用模型: {', '.join(configs.keys())}, 排除后: {', '.join(available_models)}")

    selected_configs = [(name, configs[name]) for name in available_models]

    results = run_multi_thread(selected_configs, max_workers=min(32, (os.cpu_count() or 1) * 4))

    logger.info("应用程序结束")
