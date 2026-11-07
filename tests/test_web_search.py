import json
from datetime import UTC, date, datetime
from unittest.mock import MagicMock

import requests

from utils.web_search import DSAPI_URL, SENTENCE_URL, _beijing_today, get_jinshan


def json_response(payload):
    """模拟主接口：标准 JSON 响应。"""
    res = MagicMock()
    res.raise_for_status.return_value = None
    res.json.return_value = payload
    return res


def html_response(payload):
    """模拟备用接口：响应头是 text/html，不能用 res.json()，代码按原始字节解码。"""
    res = MagicMock()
    res.raise_for_status.return_value = None
    res.json.side_effect = ValueError("Expecting value")
    res.content = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    return res


def sentence_payload(**overrides):
    payload = {
        "errno": 0,
        "errmsg": "success",
        "title": "2026-11-07",
        "content": "Winter arrives quietly.",
        "note": "立冬悄然而至。",
        "picture": "https://cdn/picture.png",
        "picture2": "https://cdn/picture2.png",
    }
    payload.update(overrides)
    return payload


class TestGetJinshanPrimary:
    def test_returns_primary_data(self, monkeypatch):
        calls = []

        def fake_get(url, **_kwargs):
            calls.append((url, _kwargs))
            return json_response({"note": "主接口句子", "fenxiang_img": "https://cdn/a.png"})

        monkeypatch.setattr("utils.web_search.requests.get", fake_get)

        assert get_jinshan() == {"note": "主接口句子", "fenxiang_img": "https://cdn/a.png"}
        assert [c[0] for c in calls] == [DSAPI_URL], "主接口成功时不应请求备用接口"

    def test_passes_timeout(self, monkeypatch):
        captured = {}

        def fake_get(_url, **kwargs):
            captured.update(kwargs)
            return json_response({"note": "句子", "fenxiang_img": "https://cdn/a.png"})

        monkeypatch.setattr("utils.web_search.requests.get", fake_get)
        get_jinshan()

        assert captured.get("timeout"), "必须设超时，否则主接口挂死会卡住整条流水线"


class TestGetJinshanFallback:
    def test_falls_back_when_primary_times_out(self, monkeypatch):
        urls = []

        def fake_get(url, **_kwargs):
            urls.append(url)
            if url == DSAPI_URL:
                raise requests.Timeout("主接口超时")
            return html_response(sentence_payload())

        monkeypatch.setattr("utils.web_search.requests.get", fake_get)

        assert get_jinshan() == {"note": "立冬悄然而至。", "fenxiang_img": "https://cdn/picture2.png"}
        assert urls == [DSAPI_URL, SENTENCE_URL]

    def test_falls_back_when_primary_returns_504(self, monkeypatch):
        def fake_get(url, **_kwargs):
            if url == DSAPI_URL:
                raise requests.HTTPError("504 Server Error")
            return html_response(sentence_payload())

        monkeypatch.setattr("utils.web_search.requests.get", fake_get)

        assert get_jinshan()["note"] == "立冬悄然而至。"

    def test_falls_back_when_primary_has_no_note(self, monkeypatch):
        def fake_get(url, **_kwargs):
            if url == DSAPI_URL:
                return json_response({"fenxiang_img": "https://cdn/a.png"})
            return html_response(sentence_payload())

        monkeypatch.setattr("utils.web_search.requests.get", fake_get)

        assert get_jinshan()["note"] == "立冬悄然而至。"

    def test_fallback_uses_beijing_date(self, monkeypatch):
        """备用接口的 title 必须按北京时间，否则 CI（UTC 机器）早上会取成昨天的句子。"""
        captured = {}

        def fake_get(url, **kwargs):
            if url == DSAPI_URL:
                raise requests.Timeout("超时")
            captured.update(kwargs)
            return html_response(sentence_payload())

        monkeypatch.setattr("utils.web_search.requests.get", fake_get)
        monkeypatch.setattr("utils.web_search._beijing_today", lambda: date(2026, 11, 8))
        get_jinshan()

        assert captured["params"]["title"] == "2026-11-08"

    def test_fallback_requests_today(self, monkeypatch):
        captured = {}

        def fake_get(url, **kwargs):
            if url == DSAPI_URL:
                raise requests.ConnectionError("连不上")
            captured.update(kwargs)
            return html_response(sentence_payload())

        monkeypatch.setattr("utils.web_search.requests.get", fake_get)
        get_jinshan()

        assert captured["params"] == {
            "c": "dailysentence",
            "m": "getdetail",
            "title": _beijing_today().isoformat(),
        }

    def test_fallback_image_falls_back_to_picture(self, monkeypatch):
        def fake_get(url, **_kwargs):
            if url == DSAPI_URL:
                raise requests.Timeout("超时")
            return html_response(sentence_payload(picture2="", fenxiang_img=""))

        monkeypatch.setattr("utils.web_search.requests.get", fake_get)

        assert get_jinshan()["fenxiang_img"] == "https://cdn/picture.png"

    def test_fallback_uses_fenxiang_img_when_present(self, monkeypatch):
        def fake_get(url, **_kwargs):
            if url == DSAPI_URL:
                raise requests.Timeout("超时")
            return html_response(sentence_payload(fenxiang_img="https://cdn/share.png"))

        monkeypatch.setattr("utils.web_search.requests.get", fake_get)

        assert get_jinshan()["fenxiang_img"] == "https://cdn/share.png"

    def test_fallback_rejects_error_errno(self, monkeypatch):
        def fake_get(url, **_kwargs):
            if url == DSAPI_URL:
                raise requests.Timeout("超时")
            return html_response(sentence_payload(errno=10001, errmsg="参数错误"))

        monkeypatch.setattr("utils.web_search.requests.get", fake_get)

        assert get_jinshan() is None


class TestBeijingToday:
    """CI 机器时区是 UTC，取日期必须按北京时间算。"""

    def test_utc_night_is_next_day_in_beijing(self, monkeypatch):
        class FakeDateTime:
            @staticmethod
            def now(tz=None):
                return datetime(2026, 11, 7, 23, 0, tzinfo=UTC).astimezone(tz or UTC)

        monkeypatch.setattr("utils.web_search.datetime", FakeDateTime)

        assert _beijing_today() == date(2026, 11, 8), "UTC 23:00 时北京已是次日 07:00"

    def test_before_beijing_midnight_keeps_same_day(self, monkeypatch):
        class FakeDateTime:
            @staticmethod
            def now(tz=None):
                return datetime(2026, 11, 7, 15, 59, tzinfo=UTC).astimezone(tz or UTC)

        monkeypatch.setattr("utils.web_search.datetime", FakeDateTime)

        assert _beijing_today() == date(2026, 11, 7), "UTC 15:59 时北京仍是 23:59"


class TestGetJinshanAllFailed:
    def test_returns_none_when_both_fail(self, monkeypatch):
        def fake_get(_url, **_kwargs):
            raise requests.ConnectionError("网络不可用")

        monkeypatch.setattr("utils.web_search.requests.get", fake_get)

        assert get_jinshan() is None

    def test_returns_none_when_fallback_is_not_json(self, monkeypatch):
        def fake_get(url, **_kwargs):
            if url == DSAPI_URL:
                raise requests.Timeout("超时")
            res = MagicMock()
            res.raise_for_status.return_value = None
            res.content = b"<html>error</html>"
            return res

        monkeypatch.setattr("utils.web_search.requests.get", fake_get)

        assert get_jinshan() is None
