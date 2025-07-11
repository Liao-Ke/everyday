import os

from dotenv import load_dotenv

from processors.file_processors import save_to_md_file
from processors.format_processors import ensure_first_line_is_h1

# 仅在非生产环境加载 .env 文件
if os.environ.get('ENV') != 'production':
    load_dotenv()

# 从环境变量获取 API 密钥
API_KEY = os.getenv("API_KEY_DOUBAO")
CLIENT_PARAMS = {
    "base_url": "https://ark.cn-beijing.volces.com/api/v3"
}
CHAT_PARAMS = {
    "model": "doubao-1-5-thinking-pro-250415",
    "messages": [
        {"role": "system", "content": "你是作者"},
        {"role": "user", "content": "写一篇最好的文章"}
    ]
}
PREPROCESSORS = []

POSTPROCESSORS = [
    ensure_first_line_is_h1
]

POSTPROCESSOR_FILES = [
    save_to_md_file
]
