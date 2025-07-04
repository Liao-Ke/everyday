import importlib
from config.logger_setup import setup_logger
import re
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from openai import APIConnectionError, APIError
from openai import OpenAI
from utils.metadata_utils import save_chat_metadata

# 获取配置好的日志器
logger = setup_logger()


def chat_ai(api_key: str, client_params: dict, chat_params: dict, session_id: str = str(uuid.uuid4()),
            max_retries=3, initial_backoff=1, max_backoff=10):
    # 初始化计时器
    start_time = time.time()
    retries = 0

    while retries < max_retries:
        try:
            client = OpenAI(api_key=api_key, **client_params)

            response = client.chat.completions.create(
                **chat_params
            )
            # 获取响应内容
            response_content = response.choices[0].message.to_dict() or ""
            # 记录响应耗时
            response_time = time.time() - start_time

            # 保存完整的对话记录（包含原始响应）
            save_chat_metadata(response_time=response_time, session_id=session_id, response_data=response.to_dict(),
                               client_params=client_params, chat_params=chat_params)

            return response_content

        except (APIConnectionError, APIError) as e:
            backoff_time = min(initial_backoff * (2 ** retries), max_backoff)
            logger.error(f"API错误，第 {retries + 1} 次重试，将等待 {backoff_time:.2f} 秒: {str(e)}")
        except TimeoutError as e:
            backoff_time = min(initial_backoff * (2 ** retries), max_backoff)
            logger.error(f"请求超时，第 {retries + 1} 次重试，将等待 {backoff_time:.2f} 秒: {str(e)}")
        except Exception as e:
            backoff_time = min(initial_backoff * (2 ** retries), max_backoff)
            logger.critical(f"严重错误: {str(e)}，第 {retries + 1} 次重试，将等待 {backoff_time:.2f} 秒", exc_info=True)

        retries += 1
        if retries < max_retries:
            time.sleep(backoff_time)  # 使用指数退避计算的时间等待

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
            **params
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
    "deepseek": load_model_config("deepseek_r1"),
    "zhipu": load_model_config("zhipu"),
    "豆包-思考": load_model_config("doubao_think"),
    "豆包": load_model_config("doubao")
}

if __name__ == '__main__':
    logger.info("应用程序启动")

    # 指定要使用的模型
    models_to_use = [
        # "deepseek",
        "zhipu",
        # "豆包-思考",
        "豆包"

    ]

    # 运行多线程生成
    results = run_multi_thread(models_to_use, max_workers=4)

    logger.info("应用程序结束")
