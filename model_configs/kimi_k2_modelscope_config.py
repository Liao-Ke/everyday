import json
import os

from model_configs import JINSHAN, SEARCH_RESULT
from processors.file_processors import save_to_md_file
from processors.format_processors import ensure_first_line_is_h1

# 从环境变量获取 API 密钥
API_KEY = os.getenv("API_KEY_MODELSCOPE")
CLIENT_PARAMS = {
    "base_url": "https://api-inference.modelscope.cn/v1"
}
some_params = {
    "model": "moonshotai/Kimi-K2-Instruct",
    "messages": [
        {
            'role': 'system',
            'content': 'You are Kimi, an AI assistant created by Moonshot '
                       'AI.请根据以下提供的参考资料（JSON'
                       '格式）来回答用户的问题。如果资料中包含相关信息，请优先基于资料内容进行回答，并可以适当补充你的知识。如果资料中没有相关信息，也可以根据你的知识进行回答。'
        },

        {"role": "user", "content": f'以下是关于"{JINSHAN.get("note")}"的参考资料：' +
                                    json.dumps(SEARCH_RESULT, ensure_ascii=False, indent=2)},
        # {"role": "assistant", "content": "已收到参考资料"},
        {"role": "user",
         "content": f'请根据上述资料，创作一篇以"{JINSHAN.get("note")}"为核心立意的故事，要求通过完整的故事情节体现其寓意，需自拟主标题，'
                    f'字数控制在2000-3000字范围内,并以markdown格式呈现。'},
        {
            "role": "assistant",
            "content": "# ",
            "partial": True
        }
    ]
}
# kimi_token_count = estimate_tokens(API_KEY, some_params["model"], some_params["messages"],
#                                    url="https://api.moonshot.cn/v1/tokenizers/estimate-token-count")
CHAT_PARAMS = {
    **some_params,
    # 修复 max_tokens 格式错误
    # "max_tokens": 32000 - kimi_token_count,
    "temperature": 0.6,
    "stream": False,
    "RETRY": False
}

PREPROCESSORS = []

POSTPROCESSORS = [

    # format_story
    ensure_first_line_is_h1,

]

POSTPROCESSOR_FILES = [
    # lambda r, n: print(n, r["content"])
    # out_test
    save_to_md_file
]
