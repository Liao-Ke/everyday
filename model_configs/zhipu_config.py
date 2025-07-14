import os

from dotenv import load_dotenv

from model_configs import JINSHAN
from processors.file_processors import save_to_md_file
from processors.format_processors import ensure_first_line_is_h1, insert_content_in_fourth_line, \
    process_string

# 仅在非生产环境加载 .env 文件
if os.environ.get('ENV') != 'production':
    load_dotenv()

# 从环境变量获取 API 密钥
API_KEY = os.getenv("API_KEY")
CLIENT_PARAMS = {
    "base_url": "https://open.bigmodel.cn/api/paas/v4/"
}
CHAT_PARAMS = {
    "model": "glm-4-flash-250414",
    "messages": [
        {"role": "system", "content": '''你现在是一个故事专家，请你根据我提供的主题写一个字数尽可能多（远超 800 字）的故事。按照下面的格式输出
""" 输出格式 """
# 故事的题目
> 故事的主题
故事内容'''},
        {"role": "user", "content": f"我提供的主题是：“{JINSHAN['note']}”"}
    ]
}
PREPROCESSORS = []

POSTPROCESSORS = [
    process_string,
    ensure_first_line_is_h1,
    insert_content_in_fourth_line,
    # format_story
]

POSTPROCESSOR_FILES = [
    save_to_md_file
]
