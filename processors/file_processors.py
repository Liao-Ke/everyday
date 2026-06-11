import datetime
import logging
import os

from utils.uuid_utils import fixed_length_uuid
from utils.yaml_utils import modify_frontmatter

logger = logging.getLogger("每日故事")


def get_today_info():
    today = datetime.datetime.now()
    # 获取星期几，0表示星期一，6表示星期日
    weekday = today.weekday()
    weekday_names = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    date_time_str = today.strftime("%Y年/%m月/%d日")
    time_str = today.strftime("%H-%M-%S")
    return f"{date_time_str}/{weekday_names[weekday]}_{time_str}"


def save_to_md_file(content, model_config):
    try:
        model_name = model_config if isinstance(model_config, str) else model_config.get("name", "unknown")
        update_frontmatter = isinstance(model_config, dict) and model_config.get("UPDATE_FRONTMATTER", False)

        file_name = f"{get_today_info()}.{fixed_length_uuid(3)}.md"
        file_path = f"./story/故事/{file_name}"
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(file_path, "w", encoding="utf-8") as file:
            if "reasoning_content" in content and content["reasoning_content"]:
                file.write(
                    f"<ReasoningChainRenderer>\n"
                    f"{content['reasoning_content']}"
                    f"\n</ReasoningChainRenderer>\n"
                    f"\n{content['content']}"
                )
            else:
                file.write(content["content"])
        logger.info(f"内容已成功保存到 {file_path}")
        if update_frontmatter:
            modify_frontmatter("./story/index.md", "hero.actions.0.link", f"/故事/{file_name}")
            logger.info(f"模型 {model_name} 更新 index.md 成功")
    except Exception as e:
        logger.error(f"保存文件时出错: {e}")
