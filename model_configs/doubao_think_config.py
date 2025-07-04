from dotenv import dotenv_values
from processors.file_processors import save_to_md_file
from processors.format_processors import ensure_first_line_is_h1

# 获取 .env 文件内容为字典
config = dotenv_values(".env")

API_KEY = config["API_KEY_DOUBAO"]
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
