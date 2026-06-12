import os

from model_configs._shared import get_jinshan_cached
from processors.file_processors import save_to_md_file
from processors.format_processors import ensure_first_line_is_h1

# 从环境变量获取 API 密钥
API_KEY = os.getenv("API_KEY_DS")
CLIENT_PARAMS = {"base_url": "https://api.deepseek.com"}
CHAT_PARAMS = {
    "model": "deepseek-v4-flash",
     "messages": [
           {
               "role": "system",
               "content": "你是一名散文作者，文笔流畅自然、有洞察力。风格介于豆瓣专栏和《南方周末》副刊之间——不学术也不鸡汤，让读者有收获感。",
           },
           {
               "role": "user",
               "content": (
                   f"# 今日素材\n{get_jinshan_cached().get('note')}\n\n"
                   "请以上面这段素材为引子，写一篇 800-1200 字的知识性文章。\n\n"
                   "要求：\n"
                   "- 从一个具体的场景或问题切入，不要泛泛而谈\n"
                   "- 围绕素材的核心概念展开，联系实际生活或文化背景\n"
                   "- 给出一个让人记住的观点或观察\n"
                   "- 标题用 H1（# 开头）"
               ),
           },
       ],
}
PREPROCESSORS = []

POSTPROCESSORS = [ensure_first_line_is_h1]

POSTPROCESSOR_FILES = [save_to_md_file]
