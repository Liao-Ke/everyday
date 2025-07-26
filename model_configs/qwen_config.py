import os

from dotenv import load_dotenv

from model_configs import JINSHAN
from processors.file_processors import save_to_md_file
from processors.format_processors import ensure_first_line_is_h1

# 仅在非生产环境加载 .env 文件
if os.environ.get('ENV') != 'production':
    load_dotenv()

# 从环境变量获取 API 密钥
API_KEY = os.getenv("API_KEY_QWEN")
CLIENT_PARAMS = {
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
}
CHAT_PARAMS = {
    "model": "qwen3-235b-a22b-thinking-2507",
    "messages": [
        {"role": "system", "content": """**你是一位思想深邃、富有创造力和洞察力的作者。你的写作以引发思考、提供新颖视角和揭示深层意义见长。在创作或表达观点时：**

1.  **超越常规：** 努力跳出思维定式，尝试建立独特的联系、提出新颖的类比或构想出人意料的观点。
2.  **挖掘深层含义：** 关注主题背后的象征意义、情感内核、社会文化背景或哲学意涵。
3.  **展现思想深度：** 避免浅尝辄止，将思考推向更深的层次，探讨更根本性的问题。
4.  **富有感染力：** 用富有哲理、引人深思或充满洞见的语言来表达，力求触动读者的思想。
5.  **结构服务于思想：** 文章的架构应服务于展现思考的深度和观点的递进，而非流于形式。

**请以思想深刻、富有洞见的作者身份进行回应/创作。**
        """},
        {"role": "user", "content": f"写一篇小说用来解读“{JINSHAN['note']}”这句话。要求：1. 字数在 2333 字左右。2. 自拟标题。"},
        {
            "role": "assistant",
            "content": "# ",
            # "partial": True
        }
    ],
    # "extra_body": {"enable_search": True}
    # "stream": True
}
PREPROCESSORS = []

POSTPROCESSORS = [
    ensure_first_line_is_h1
]

POSTPROCESSOR_FILES = [
    save_to_md_file
    # lambda r, n:
    # print(n, "<think>", r["reasoning_content"], "</think>\n\n", r["content"]) if "reasoning_content" in r else
    # print(n, r["content"])
]
