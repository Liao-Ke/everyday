import os
import shutil
import datetime
import re


def move_file_if_exceeds_threshold(file_path, threshold_mb, target_dir, rename_rule):
    """
    检查文件大小是否超过阈值，如果是则移动到目标目录并重命名

    Args:
        file_path (str): 源文件路径
        threshold_mb (float): 大小阈值(MB)
        target_dir (str): 目标目录路径
        rename_rule (str): 重命名规则，支持以下占位符:
            {timestamp} - 当前时间戳
            {seq} - 自动生成的序列号
            {filename} - 原文件名
            {ext} - 原文件扩展名
    """
    try:
        # 检查源文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 检查目标目录是否存在，不存在则创建
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        # 获取文件大小(MB)
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

        # 检查文件是否达到阈值
        if file_size_mb < threshold_mb:
            print(f"文件大小 {file_size_mb:.2f}MB 未达到阈值 {threshold_mb}MB，不执行移动操作")
            return False

        # 准备重命名所需的变量
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        # 生成序列号(查找目标目录中已存在的最大序列号)
        existing_files = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))]
        seq = 1
        for f in existing_files:
            match = re.search(r'^(\d+)_', f)
            if match:
                seq = max(seq, int(match.group(1)) + 1)

        # 应用重命名规则
        new_filename = rename_rule
        new_filename = new_filename.replace("{timestamp}", timestamp)
        new_filename = new_filename.replace("{seq}", f"{seq:04d}")
        new_filename = new_filename.replace("{filename}", name)
        new_filename = new_filename.replace("{ext}", ext)

        # 构建目标路径
        target_path = os.path.join(target_dir, new_filename)

        # 移动文件
        shutil.move(file_path, target_path)
        print(f"文件已移动并重命名: {filename} -> {new_filename}")
        return True

    except FileNotFoundError as e:
        print(f"错误: {e}")
        return False
    except PermissionError:
        print(f"错误: 没有足够的权限移动文件 {file_path}")
        return False
    except Exception as e:
        print(f"移动文件时发生未知错误: {e}")
        return False


# 使用示例
if __name__ == "__main__":
    # 示例调用
    result = move_file_if_exceeds_threshold(
        file_path="chat_logs/story_records.json",
        threshold_mb=4.78,
        target_dir="chat_logs/archive",
        rename_rule="{filename}{ext}@{timestamp}"
    )
