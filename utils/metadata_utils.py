import datetime

import json
import logging
import os

import sys

logger = logging.getLogger('每日故事')


def save_chat_metadata(response_time: float, session_id: str, response_data: dict | list, client_params: dict,
                       chat_params: dict):
    """修复后的元数据保存
    :param response_data:
    :param session_id:
    :param response_time:
    :param client_params:
    :param chat_params:
    """
    metadata = {
        "session_id": session_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "response_time": round(response_time, 3),
        "client_params": client_params,
        "chat_params": chat_params,
        "response_data": response_data,
        "system_metrics": {
            "platform": os.name,
            "python_version": sys.version.split()[0]
        }
    }

    _save_to_json(metadata, "chat_logs/story_records.json")


def _save_to_json(data: dict, filename: str):
    """修复后的通用存储方法"""
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        existing = []

        # 更健壮的文件读取方式
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            except json.JSONDecodeError as e:
                logger.warning(f"检测到损坏日志文件，尝试修复: {str(e)}")
                # 备份损坏文件
                corrupted_name = f"{filename}.corrupted_{datetime.datetime.now().timestamp()}"
                os.rename(filename, corrupted_name)

        # 追加新数据
        existing.append(data)

        # 原子写入操作
        temp_file = f"{filename}.tmp"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)

        os.replace(temp_file, filename)

    except Exception as e:
        logger.critical(f"严重错误: 数据保存失败 - {str(e)}")
        # 这里可以添加将错误数据暂存到内存的逻辑


def process_stream_chunks(chunks):
    """
    处理OpenAI SDK流式输出消息块，转换为非流式输出结构
    保留所有原始字段，合并增量内容（包括function_call, tool_calls等）

    参数:
    chunks -- 包含所有流式输出块的列表，每个块是ChatCompletionChunk对象

    返回:
    dict -- 完整的非流式响应结构，包含所有原始字段和合并后的消息
    """
    if not chunks:
        return None

    # 初始化结果结构，使用第一个chunk的非增量字段
    result = {
        "id": chunks[0].id,
        "object": "chat.completion",  # 修改为完整响应的object类型
        "created": chunks[0].created,
        "model": chunks[0].model,
        "system_fingerprint": getattr(chunks[0], 'system_fingerprint', None),
        "choices": [{
            "index": 0,
            "message": {
                "role": "",
                "content": "",
                # 初始化可能存在的其他字段
            },
            "finish_reason": None,
            "logprobs": None,
        }],
        "usage": None
    }

    # 添加可能存在的额外字段（如service_tier）
    for key in chunks[0].__dict__.keys():
        if key not in ['choices', 'id', 'object', 'created', 'model', 'system_fingerprint']:
            result[key] = getattr(chunks[0], key, None)

    # 初始化合并容器
    message = result["choices"][0]["message"]
    function_calls = {}
    tool_calls = {}
    reasoning_content = ""

    # 处理所有chunks
    for chunk in chunks:
        # 更新usage（最后一个chunk可能有值）
        if getattr(chunk, 'usage', None):
            result["usage"] = chunk.usage.model_dump()

        # 获取当前chunk的delta
        if not chunk.choices:
            continue

        choice = chunk.choices[0]

        # 更新finish_reason（最后一个chunk有值）
        if choice.finish_reason:
            result["choices"][0]["finish_reason"] = choice.finish_reason

        # 更新logprobs
        if choice.logprobs:
            result["choices"][0]["logprobs"] = choice.logprobs

        delta = choice.delta

        # 处理角色
        if getattr(delta, 'role', None):
            message["role"] = delta.role

        # 合并内容
        if getattr(delta, 'content', None):
            message["content"] += delta.content

        # 合并function_call
        if getattr(delta, 'function_call', None):
            fc = delta.function_call
            if fc.name:
                function_calls['name'] = fc.name
            if fc.arguments:
                function_calls.setdefault('arguments', "")
                function_calls['arguments'] += fc.arguments

        # 合并tool_calls
        if getattr(delta, 'tool_calls', None):
            for tool in delta.tool_calls:
                index = tool.index
                if index not in tool_calls:
                    tool_calls[index] = {
                        'id': '',
                        'type': '',
                        'function': {'name': '', 'arguments': ''}
                    }

                if tool.id:
                    tool_calls[index]['id'] = tool.id
                if tool.type:
                    tool_calls[index]['type'] = tool.type

                if tool.function:
                    if tool.function.name:
                        tool_calls[index]['function']['name'] = tool.function.name
                    if tool.function.arguments:
                        tool_calls[index]['function']['arguments'] += tool.function.arguments

        # 处理自定义字段（如reasoning_content）
        if getattr(delta, 'reasoning_content', None):
            reasoning_content += delta.reasoning_content

    # 设置默认角色
    if not message["role"]:
        message["role"] = "assistant"

    # 添加合并后的function_call
    if function_calls:
        # 将 function_calls 字典转换为 JSON 字符串
        message["function_call"] = json.dumps(function_calls, ensure_ascii=False)

    # 添加合并后的tool_calls
    if tool_calls:
        # 将 tool_calls 列表转换为 JSON 字符串
        message["tool_calls"] = json.dumps([tool_calls[i] for i in sorted(tool_calls.keys())], ensure_ascii=False)

    # 添加自定义字段
    if reasoning_content:
        message["reasoning_content"] = reasoning_content

    return result
