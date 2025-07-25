import importlib
import re
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

from openai import APIConnectionError, APITimeoutError, APIStatusError, RateLimitError
from openai import OpenAI

from config.logger_setup import setup_logger
from utils.metadata_utils import save_chat_metadata, process_stream_chunks

# 获取配置好的日志器
logger = setup_logger()


def chat_ai(api_key: str, client_params: dict, chat_params: dict, session_id: str = str(uuid.uuid4()),
            max_retries=3, initial_backoff=1, max_backoff=10):
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
    is_stream = chat_params.get('stream', False)

    while retries <= max_retries:
        try:
            client = OpenAI(api_key=api_key, **client_params)

            response = client.chat.completions.create(
                **chat_params
            )
            # 记录响应耗时
            response_time = time.time() - start_time
            if not is_stream:
                # 获取响应内容
                response_content = response.choices[0].message.model_dump() or ""

                # 保存完整的对话记录（包含原始响应）
                save_chat_metadata(response_time=response_time, session_id=session_id, response_data=response.to_dict(),
                                   client_params=client_params, chat_params=chat_params)

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
                        if (hasattr(chunk.choices[0].delta, 'reasoning_content')
                                and chunk.choices[0].delta.reasoning_content):
                            reasoning_chunks.append(chunk.choices[0].delta.reasoning_content)
                response_content = {"content": "".join(content_chunks)}
                if reasoning_chunks:
                    response_content["reasoning_content"] = "".join(reasoning_chunks)
                save_chat_metadata(response_time=response_time, session_id=session_id,
                                   response_data=process_stream_chunks(full_response),
                                   client_params=client_params, chat_params=chat_params)

                return response_content

        # 异常处理（按优先级排序）
        except RateLimitError as e:

            # 专门处理速率限制错误

            backoff_time = min(initial_backoff * (2 ** retries) * 2, max_backoff)  # 比普通错误等待更久

            logger.warning(f"API速率限制错误，第 {retries + 1} 次重试，将等待 {backoff_time:.2f} 秒: {str(e)}")

            # 尝试从错误信息中提取重试建议时间

            retry_after = getattr(e, 'retry_after', None)

            if retry_after and retry_after > backoff_time:
                logger.info(f"使用API建议的重试时间: {retry_after}秒")

                backoff_time = retry_after
        except APITimeoutError as e:
            backoff_time = min(initial_backoff * (2 ** retries), max_backoff)
            logger.error(f"请求超时，第 {retries + 1} 次重试，将等待 {backoff_time:.2f} 秒: {str(e)}")

        except (APIConnectionError, APIStatusError, RateLimitError) as e:
            backoff_time = min(initial_backoff * (2 ** retries), max_backoff)
            logger.error(f"API错误，第 {retries + 1} 次重试，将等待 {backoff_time:.2f} 秒: {str(e)}")

        except Exception as e:
            backoff_time = min(initial_backoff * (2 ** retries), max_backoff)
            logger.critical(f"严重错误: {str(e)}，第 {retries + 1} 次重试，将等待 {backoff_time:.2f} 秒", exc_info=True)

        retries += 1
        if retries < max_retries:
            time.sleep(backoff_time)  # 使用指数退避计算的时间等待
    logger.error(f"所有 {max_retries} 次重试均失败")
    return None


# 动态导入模型配置
def load_model_config(model_name: str) -> dict | None:
    """动态加载模型配置文件

    Args:
        model_name: 模型名称（如 'gpt-4', 'claude-3'）

    Returns:
        包含配置的字典，或 None（加载失败时）
    """
    # 1. 安全处理模块名
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '', model_name)  # 移除非字母数字字符
    module_name = f"{safe_name}_config"
    try:
        # 2. 动态导入配置模块
        module = importlib.import_module(f"model_configs.{module_name}")

        # 3. 安全获取配置项（带默认值）
        config = {
            "api_key": getattr(module, "API_KEY", None),
            "client_params": getattr(module, "CLIENT_PARAMS", {}),
            "chat_params": getattr(module, "CHAT_PARAMS", {}),
            "preprocessors": getattr(module, "PREPROCESSORS", []),
            "postprocessors": getattr(module, "POSTPROCESSORS", []),
            "postprocessor_files": getattr(module, "POSTPROCESSOR_FILES", []),
        }

        # 4. 验证必要配置
        if not config["api_key"]:
            logger.error(f"模型 {model_name} 缺少 API_KEY 配置")
            return None

        # 5. 返回配置字典
        return config

    except ImportError:
        logger.warning(f"未找到模型 {model_name} 的配置文件")
        return None
    except Exception as e:
        logger.error(f"加载模型 {model_name} 配置时出错: {str(e)}", exc_info=True)
        return None


def story_generator(model_name, result_queue=None):
    """故事生成器函数 - 现在可以作为线程执行体"""
    try:
        if model_name not in config_map:
            logger.warning(f"模型 {model_name} 未配置，将跳过")
            return None
        logger.info(f"已启动模型 {model_name} 的生成线程")
        model_config = config_map[model_name]
        params = {
            "chat_params": model_config["chat_params"],
            "client_params": model_config["client_params"]
        }

        # 应用前置处理器
        logger.info(f"模型 {model_name} 开始应用前置处理器")
        for preprocessor in model_config["preprocessors"]:
            logger.info(f"正在应用前置处理器 {preprocessor.__name__}")
            params = preprocessor(params)
            logger.info(f"前置处理器 {preprocessor.__name__} 已应用")
        logger.info(f"模型 {model_name} 前置处理器应用完成")

        # 调用AI生成故事
        logger.info(f"模型 {model_name} 开始调用AI生成故事")
        r = chat_ai(
            api_key=model_config["api_key"],
            **params,
            initial_backoff=60,
            max_backoff=600,
            max_retries=5
        )
        logger.info(f"模型 {model_name} AI生成故事完成")
        # 检查是否生成失败
        if r is None:
            logger.error(f"模型 {model_name} 生成故事失败，跳过后置处理器")
        else:
            # 应用后置处理器
            logger.info(f"模型 {model_name} 开始应用后置处理器")
            for processor in model_config["postprocessors"]:
                logger.info(f"正在应用后置处理器 {processor.__name__}")
                r = processor(r)
                logger.info(f"后置处理器 {processor.__name__} 已应用")
            logger.info(f"模型 {model_name} 后置处理器应用完成")

            # 保存到文件
            logger.info(f"模型 {model_name} 开始应用文件后置处理器")
            for file_processor in model_config["postprocessor_files"]:
                logger.info(f"正在应用文件后置处理器 {file_processor.__name__}")
                file_processor(r, model_name)
                logger.info(f"文件后置处理器 {file_processor.__name__} 已应用")
            logger.info(f"模型 {model_name} 文件后置处理器应用完成")

        # 如果提供了结果队列，将结果放入队列
        if result_queue is not None:
            result_queue.put((model_name, r))
        logger.info(f"模型 {model_name} 生成完成")
        return r
    except Exception as e:
        logger.error(f"模型 {model_name} 生成过程中出错: {str(e)}")
        return None


def run_multi_thread(selected_models, max_workers=4):
    result_queue = Queue()
    logger.info(f"开始多线程故事生成，将使用模型: {', '.join(selected_models)}，最大并发线程数: {max_workers}")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for model_name in selected_models:
            future = executor.submit(story_generator, model_name, result_queue)
            futures.append(future)
        for future in futures:
            future.result()  # 等待所有任务完成
    logger.info("所有模型的生成线程已完成")
    model_results = {}
    while not result_queue.empty():
        model_name, result = result_queue.get()
        model_results[model_name] = result
    return model_results


config_map = {
    "deepseek": load_model_config("deepseek_v3"),
    "zhipu": load_model_config("zhipu"),
    "豆包-思考": load_model_config("doubao_think"),
    "豆包": load_model_config("doubao"),
    "qwen": load_model_config("qwen"),
    # "kimi": load_model_config("kimi")
}

if __name__ == '__main__':
    logger.info("应用程序启动")

    # 指定要使用的模型
    models_to_use = [
        "deepseek",
        "zhipu",
        # "豆包-思考",
        "豆包",
        # "kimi"
        "qwen"
    ]

    # 运行多线程生成
    results = run_multi_thread(models_to_use, max_workers=4)

    logger.info("应用程序结束")
