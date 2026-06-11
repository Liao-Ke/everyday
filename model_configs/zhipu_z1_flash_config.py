import json
import os

from model_configs._shared import get_jinshan_cached, get_search_cached
from processors.file_processors import save_to_md_file
from processors.format_processors import ensure_first_line_is_h1
from utils.misc import process_reasoning_content, remove_leading_empty_line

# 从环境变量获取 API 密钥
API_KEY = os.getenv("API_KEY")

CLIENT_PARAMS = {"base_url": "https://open.bigmodel.cn/api/paas/v4/"}
CHAT_PARAMS = {
    "model": "glm-z1-flash",
    "messages": [
        {
            "role": "user",
            "content": f'以下是关于"{get_jinshan_cached().get("note")}"的参考资料：'
            + json.dumps(get_search_cached(), ensure_ascii=False, indent=2),
        },
        {
            "role": "user",
            "content": "根据以上参考资料，创作一篇基于内容的故事。为故事创建一个原创标题，最终只输出原创标题和故事内容的文本本身，不包括解释或其他任何额外信息。",
        },
        {
            "role": "assistant",
            "content": "# 《",
        },
    ],
}
PREPROCESSORS = []

POSTPROCESSORS = [process_reasoning_content, remove_leading_empty_line, ensure_first_line_is_h1]

POSTPROCESSOR_FILES = [save_to_md_file]
