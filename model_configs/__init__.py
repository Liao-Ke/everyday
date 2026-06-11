import os

from dotenv import load_dotenv

# 仅在非生产环境加载 .env 文件
if os.environ.get("ENV") != "production":
    load_dotenv()
