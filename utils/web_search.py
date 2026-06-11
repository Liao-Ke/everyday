import json
import logging

import requests

logger = logging.getLogger("每日故事")


def get_jinshan():
    try:
        res = requests.get("https://open.iciba.com/dsapi/")
        res.raise_for_status()
        data = res.json()
        logger.info(f"今日金山词霸：{data.get('note')}")
        return {"note": data.get("note"), "fenxiang_img": data.get("fenxiang_img")}
    except requests.RequestException as e:
        logger.error(f"网络请求错误: {e}")
        return None
    except ValueError as e:
        logger.error(f"JSON解析错误: {e}")
        return None


def web_search(
    api_key,
    search_query,
    search_engine="search_std",
    search_intent=False,
    count=10,
    search_domain_filter=None,
    search_recency_filter="noLimit",
    content_size="medium",
    request_id=None,
    user_id=None,
):
    if not api_key or not search_query:
        raise ValueError("api_key和search_query为必填参数")

    if not isinstance(count, int) or count < 1 or count > 50:
        raise ValueError("count参数必须是1-50之间的整数")

    valid_engines = ["search_std", "search_pro", "search_pro_sogou", "search_pro_quark"]
    if search_engine not in valid_engines:
        raise ValueError(f"search_engine必须是以下值之一: {', '.join(valid_engines)}")

    valid_recency = ["oneDay", "oneWeek", "oneMonth", "oneYear", "noLimit"]
    if search_recency_filter not in valid_recency:
        raise ValueError(f"search_recency_filter必须是以下值之一: {', '.join(valid_recency)}")

    valid_content_sizes = ["medium", "high"]
    if content_size not in valid_content_sizes:
        raise ValueError(f"content_size必须是以下值之一: {', '.join(valid_content_sizes)}")

    url = "https://open.bigmodel.cn/api/paas/v4/web_search"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    data = {
        "search_query": search_query,
        "search_engine": search_engine,
        "search_intent": search_intent,
        "count": count,
        "search_recency_filter": search_recency_filter,
        "content_size": content_size,
    }

    if search_domain_filter:
        data["search_domain_filter"] = search_domain_filter
    if request_id:
        data["request_id"] = request_id
    if user_id:
        data["user_id"] = user_id

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()

        resp_data = response.json()
        if search_intent and response.json()["search_intent"][0]["intent"] == "SEARCH_NONE":
            logger.info(f"无搜索意图：{response.json()['search_intent']},将关闭意图识别后重试")
            return web_search(
                api_key,
                search_query,
                search_engine,
                False,
                count,
                search_domain_filter,
                search_recency_filter,
                content_size,
                request_id,
                user_id,
            )

        logger.info(f"网络搜索成功：{response.json()['search_intent']}")
        return resp_data
    except requests.exceptions.RequestException as e:
        logger.error(f"请求发生错误：{e}")
        return None
    except json.JSONDecodeError:
        logger.error("响应内容不是有效的JSON格式")
        return None
