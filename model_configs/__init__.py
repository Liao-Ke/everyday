import requests

import logging

logger = logging.getLogger('每日故事')


def get_jinshan():
    try:
        res = requests.get("https://open.iciba.com/dsapi/")
        res.raise_for_status()  # 检查请求是否成功
        data = res.json()
        logger.info(f"今日金山词霸：{data.get('note')}")
        return {
            "note": data.get('note'),
            "fenxiang_img": data.get('fenxiang_img')
        }
    except requests.RequestException as e:
        logger.error(f"网络请求错误: {e}")
        return None
    except ValueError as e:
        logger.error(f"JSON解析错误: {e}")
        return None


JINSHAN = get_jinshan()
