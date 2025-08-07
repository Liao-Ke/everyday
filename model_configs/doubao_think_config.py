import os

from model_configs import JINSHAN
from processors.file_processors import save_to_md_file
from processors.format_processors import ensure_first_line_is_h1

# 从环境变量获取 API 密钥
API_KEY = os.getenv("API_KEY_DOUBAO")
CLIENT_PARAMS = {
    "base_url": "https://ark.cn-beijing.volces.com/api/v3"
}
CHAT_PARAMS = {
    "model": "doubao-seed-1-6-thinking-250715",
    "messages": [
        # {"role": "system", "content": "你是作者"},
        {"role": "user", "content": f"“{JINSHAN['note']}”之我见"},
        # {"role": "assistant", "content": "# "}
    ]

}
PREPROCESSORS = []

POSTPROCESSORS = [
    ensure_first_line_is_h1
]

POSTPROCESSOR_FILES = [
    # save_to_md_file
    lambda r, n:
    print(n, "<think>", r["reasoning_content"], "</think>\n\n", r["content"]) if "reasoning_content" in r else
    print(n, r["content"])
]
