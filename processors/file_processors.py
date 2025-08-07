import os
import logging
import datetime

from utils.mish_mash import modify_frontmatter, fixed_length_uuid

logger = logging.getLogger('每日故事')


def get_today_info():
    today = datetime.datetime.now()
    # 获取星期几，0表示星期一，6表示星期日
    weekday = today.weekday()
    weekday_names = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    date_time_str = today.strftime("%Y年/%m月/%d日")
    time_str = today.strftime("%H-%M-%S")
    return f"{date_time_str}/{weekday_names[weekday]}_{time_str}"


def save_to_md_file(content, model_name):
    try:
        file_name = f"{get_today_info()}.{fixed_length_uuid(3)}.md"
        file_path = f"./story/故事/{file_name}"
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(file_path, 'w', encoding='utf-8') as file:
            if 'reasoning_content' in content and content['reasoning_content']:
                file.write(f"<ReasoningChainRenderer>\n"
                           f"{content['reasoning_content']}"
                           f"\n</ReasoningChainRenderer>\n"
                           f"\n{content['content']}")
            else:
                file.write(content['content'])
        logger.info(f"内容已成功保存到 {file_path}")
        if model_name == "zhipu":
            modify_frontmatter("./story/index.md", "hero.actions.0.link", f"/故事/{file_name}")
            logger.info(f"修改index.md文件成功")
    except Exception as e:
        logger.error(f"保存文件时出错: {e}")
