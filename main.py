import os
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue

from config.logger_setup import setup_logger
from core.pipeline import run_model
from core.registry import ModelRegistry

logger = setup_logger()

EXCLUDED_MODELS: set[str] = {"doubao_think", "kimi", "zhipu_z1_flash"}


def run_multi_thread(selected_configs: list[tuple[str, dict]], max_workers=4):
    model_names = [name for name, _ in selected_configs]
    result_queue = Queue()
    logger.info(f"开始多线程故事生成，将使用模型: {', '.join(model_names)}，最大并发线程数: {max_workers}")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_model = {
            executor.submit(_run_single, name, config, result_queue): name for name, config in selected_configs
        }

        for future in as_completed(future_to_model):
            model_name = future_to_model[future]
            try:
                future.result()
            except Exception as e:
                error_msg = f"模型 {model_name} 生成故事时出错: {str(e)}\n{traceback.format_exc()}"
                logger.error(error_msg)
                result_queue.put((model_name, {"error": error_msg}))
    logger.info("所有模型的生成线程已完成")

    model_results = {}
    while not result_queue.empty():
        model_name, result = result_queue.get()
        model_results[model_name] = result
    return model_results


def _run_single(model_name: str, config: dict, result_queue: Queue):
    logger.info(f"已启动模型 {model_name} 的生成线程")
    r = run_model(config)
    if result_queue is not None:
        result_queue.put((model_name, r))
    logger.info(f"模型 {model_name} 生成完成")
    return r


if __name__ == "__main__":
    logger.info("应用程序启动")

    configs = ModelRegistry.discover()
    available_models = [name for name in configs if name not in EXCLUDED_MODELS]
    logger.info(f"可用模型: {', '.join(configs.keys())}, 排除后: {', '.join(available_models)}")

    selected_configs = [(name, configs[name]) for name in available_models]

    results = run_multi_thread(selected_configs, max_workers=min(32, (os.cpu_count() or 1) * 4))

    logger.info("应用程序结束")
