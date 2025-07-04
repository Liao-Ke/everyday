import datetime

import json
import os

import sys


def save_chat_metadata(response_time: float, session_id: str, response_data: dict, client_params: dict,
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
                print(f"检测到损坏日志文件，尝试修复: {str(e)}")
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
        print(f"严重错误: 数据保存失败 - {str(e)}")
        # 这里可以添加将错误数据暂存到内存的逻辑
