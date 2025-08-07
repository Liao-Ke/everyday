
import os

from dotenv import load_dotenv

from utils.mish_mash import get_jinshan, web_search

# 仅在非生产环境加载 .env 文件
if os.environ.get('ENV') != 'production':
    load_dotenv()

JINSHAN = get_jinshan()
SEARCH_RESULT = web_search(
    api_key=os.getenv("API_KEY"),
    search_query=JINSHAN['note'],
    search_engine="search_pro",  # 使用高级搜索引擎
    content_size="high",
    search_intent=True
)
