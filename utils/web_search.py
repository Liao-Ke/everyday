import json
import logging
from datetime import datetime, timedelta, timezone

import requests

logger = logging.getLogger("每日故事")

# 每日一句：主接口长期返回 504/无数据，备用接口字段基本兼容（只是没有 fenxiang_img）
DSAPI_URL = "https://open.iciba.com/dsapi/"
SENTENCE_URL = "http://sentence.iciba.com/index.php"
# (连接, 读取) 超时秒数：主接口挂死时会一直等，不设超时就无法及时回退
REQUEST_TIMEOUT = (5, 15)
# 官方服务的“今天”按北京时间；固定 +8 无夏令时，也不依赖 tzdata
BEIJING_TZ = timezone(timedelta(hours=8))


def _beijing_today():
    """北京时间当天日期：CI 机器是 UTC，直接用 date.today() 会在北京早上取到昨天。"""
    return datetime.now(BEIJING_TZ).date()


def _fetch_dsapi():
    """主接口 open.iciba.com/dsapi/，返回 {note, fenxiang_img}。"""
    res = requests.get(DSAPI_URL, timeout=REQUEST_TIMEOUT)
    res.raise_for_status()
    data = res.json()
    return {"note": data.get("note"), "fenxiang_img": data.get("fenxiang_img")}


def _fetch_sentence():
    """备用接口 sentence.iciba.com/index.php（响应头是 text/html，内容其实是 JSON）。"""
    # title 必须由调用方指定，且要与官方服务一致按北京时间取，否则 CI 上会取成昨天的句子
    params = {"c": "dailysentence", "m": "getdetail", "title": _beijing_today().isoformat()}
    res = requests.get(SENTENCE_URL, params=params, timeout=REQUEST_TIMEOUT)
    res.raise_for_status()
    data = json.loads(res.content.decode("utf-8"))
    if data.get("errno") != 0:
        raise ValueError(f"接口返回 errno={data.get('errno')} errmsg={data.get('errmsg')}")
    # 备用接口没有 fenxiang_img 字段，用同尺寸大图兜底
    return {
        "note": data.get("note"),
        "fenxiang_img": data.get("fenxiang_img") or data.get("picture2") or data.get("picture"),
    }


def get_jinshan():
    """获取今日金山词霸每日一句，主接口失败时依次回退备用接口。

    返回 {"note": 中文翻译, "fenxiang_img": 配图地址}；全部接口失败返回 None。
    """
    sources = (
        ("open.iciba.com/dsapi", _fetch_dsapi),
        ("sentence.iciba.com/index.php", _fetch_sentence),
    )
    for name, fetch in sources:
        try:
            data = fetch()
            if not data.get("note"):
                raise ValueError("返回内容缺少 note 字段")
            logger.info(f"今日金山词霸（{name}）：{data['note']}")
            return data
        except (requests.RequestException, ValueError) as e:
            # RequestException 覆盖网络/HTTP/超时；JSON 解析失败也是 ValueError
            logger.warning(f"金山词霸接口 {name} 不可用：{e}，尝试下一个接口")
    logger.error("金山词霸主接口与备用接口均不可用")
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
