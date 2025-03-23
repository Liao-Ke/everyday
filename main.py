import json
import os
# import uuid
# import platform
import requests
import zhipuai
from dotenv import load_dotenv
from openai import APIConnectionError, APIError
from openai import OpenAI
from zhipuai import ZhipuAI
import time
import uuid
import datetime
import sys


# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。
def save_to_md_file(content, file_path):
    try:
        # 获取文件路径的目录部分
        directory = os.path.dirname(file_path)
        # 如果目录不存在，则创建目录
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"内容已成功保存到 {file_path}")
    except Exception as e:
        print(f"保存文件时出错: {e}")


def get_today_info():
    today = datetime.datetime.now()
    # 获取星期几，0表示星期一，6表示星期日
    weekday = today.weekday()
    weekday_names = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    date_time_str = today.strftime("%Y年/%m月/%d日")
    time_str = today.strftime("%H:%M:%S")
    return f"{date_time_str}/{weekday_names[weekday]} {time_str}"


def insert_content_in_fourth_line(s, content):
    lines = s.splitlines()
    if len(lines) < 4:
        lines.append(content)
    else:
        lines.insert(3, content)
    return '\n'.join(lines)


def insert_content_in_first_line(s, content):
    lines = s.splitlines()

    lines.insert(0, content)
    return '\n'.join(lines)


def get_jinshan():
    try:
        res = requests.get("https://open.iciba.com/dsapi/")
        res.raise_for_status()  # 检查请求是否成功
        data = res.json()
        return {
            "note": data.get('note'),
            "fenxiang_img": data.get('fenxiang_img')
        }
    except requests.RequestException as e:
        print(f"网络请求错误: {e}")
        return None
    except ValueError as e:
        print(f"JSON解析错误: {e}")
        return None


def chat_ai(msg: str, api_key: str, session_id: str = None) -> str:
    client = ZhipuAI(api_key=api_key)  # 请填写您自己的APIKey

    # 生成会话ID（如果未提供）
    session_id = session_id or str(uuid.uuid4())

    # 初始化计时器
    start_time = time.time()

    # prompt = ("请根据我提供的一句话，以 Markdown 格式的一级标题为这个故事起标题，在标题下方以 Markdown "
    #           "格式引用该句话。充分释放创意，不限风格、叙事视角、角色、场景、情感基调，创作一个深度贴合该句含义，情节跌宕起伏、扣人心弦且逻辑缜密，字数尽可能多（远超 800 字）的故事。")
    prompt = '''你现在是一个故事专家，请你根据我提供的主题写一个字数尽可能多（远超 800 字）的故事。按照下面的格式输出
""" 输出格式 """
# 故事的题目
> 故事的主题
故事内容'''

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": msg}
    ]
    try:

        response = client.chat.completions.create(
            model="glm-4-flash",  # 请填写您要调用的模型名称
            messages=messages
            # top_p=0.70,
            # temperature=0.95
        )
        # 获取响应内容
        response_content = response.choices[0].message.content or ""
        # 记录响应耗时
        response_time = time.time() - start_time

        # 保存完整的对话记录（包含原始响应）
        save_chat_metadata(
            messages=messages,
            response_time=response_time,
            session_id=session_id,
            response_data=response.to_dict()
        )

        return response_content

    except zhipuai.APIRequestFailedError as e:
        error_msg = f"敏感词:{msg} \n{str(e)}"
        print(error_msg)
        log_error(error_msg)
        return "服务暂时不可用，请稍后重试(敏感词)"
    except Exception as e:
        error_msg = f"系统错误: {str(e)}"
        print(error_msg)
        log_error(error_msg)
        return "服务暂时不可用，请稍后重试"


# def get_prompt() -> str:
#     """返回动态生成的提示词"""
#     return f'''作为专业作家，请根据主题创作故事。要求：
#     - 当前时间：{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
#     - 严格按格式输出：
#     # 标题
#     > 主题
#     故事内容（远超800字）
#     - 保持逻辑严密、情节曲折'''


def save_chat_metadata(messages:  list[dict[str, str] | dict[str, str]], response_time: float, session_id: str,
                       response_data: dict):
    """修复后的元数据保存"""
    metadata = {
        "session_id": session_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "response_time": round(response_time, 3),
        "messages": messages,
        "system_metrics": {
            "platform": os.name,
            "python_version": sys.version.split()[0]
        },
        "response_data": response_data

    }

    # 使用固定路径测试
    _save_to_json(metadata, "chat_logs/story_records.json")


def log_error(error_msg: str):
    """独立的错误日志记录"""
    error_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "error": error_msg,
        "level": "ERROR"
    }
    _save_to_json(error_entry, "error_logs/ai_errors.json")


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


def chat_ai_ds(msg: str, api_key: str, session_id: str = None) -> tuple:
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")  # 请填写您自己的APIKey

    # 生成会话ID（如果未提供）
    session_id = session_id or str(uuid.uuid4())

    # 初始化计时器
    start_time = time.time()

    # prompt = ("请根据我提供的一句话，以 Markdown 格式的一级标题为这个故事起标题，在标题下方以 Markdown "
    #           "格式引用该句话。充分释放创意，不限风格、叙事视角、角色、场景、情感基调，创作一个深度贴合该句含义，情节跌宕起伏、扣人心弦且逻辑缜密，字数尽可能多（远超 800 字）的故事。")
    #     prompt = '''你现在是一个故事专家，请你根据我提供的主题写一个字数尽可能多（远超 800 字）的故事。按照下面的格式输出
    # """ 输出格式 """
    # # 故事的题目
    # > 故事的主题
    # 故事内容'''
    prompt = '''作为专业作家，请根据主题创作故事。要求：
    - 严格按格式输出：
    # 标题
    > 主题
    故事内容（远超800字）
    - 保持逻辑严密、情节曲折'''

    messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": msg}
            ]
    try:

        response = client.chat.completions.create(
            model="deepseek-reasoner",  # 请填写您要调用的模型名称
            messages=messages,
            # top_p=0.70,
            # temperature=1.5,
            stream=False
        )

        # 获取响应内容
        reasoning_content = response.choices[0].message.reasoning_content or ""
        response_content = response.choices[0].message.content or ""
        # 记录响应耗时
        response_time = time.time() - start_time

        # 保存完整的对话记录（包含原始响应）
        save_chat_metadata(
            messages=messages,
            response_time=response_time,
            session_id=session_id,
            response_data=response.to_dict()
        )

        return reasoning_content, response_content

    except (APIConnectionError, APIError) as e:
        error_msg = f"API错误: {str(e)}"
        print(error_msg)
        log_error(error_msg)  # 建议添加独立的错误日志
        return "思考失败", "服务暂时不可用，请稍后重试"

    except Exception as e:
        error_msg = f"系统错误: {str(e)}"
        print(error_msg)
        log_error(error_msg)
        return "思考失败", "生成失败，请联系管理员"


def ensure_first_line_is_h1(markdown_text):
    """
    确保输入字符串的第一行是 Markdown 格式的一级标题。

    参数:
    markdown_text (str): 输入的 Markdown 文本。

    返回:
    str: 调整后的 Markdown 文本，确保第一行是一级标题。
    """
    lines = markdown_text.splitlines()
    if lines:
        first_line = lines[0]

        # 检查第一行是否是标题，并确定其级别
        if first_line.startswith('# '):
            # 已经是一级标题，不做改动
            pass
        elif first_line.startswith('## '):
            # 二级标题，降为一级标题
            lines[0] = '#' + first_line[2:]
        elif first_line.startswith('### '):
            # 三级标题，降为一级标题
            lines[0] = '#' + first_line[3:]
        else:
            # 不是标题，则直接添加一级标题格式
            lines.insert(0, '# ' + first_line)

    # 重新组合成字符串返回
    return '\n'.join(lines)


def download_image(url, save_dir):
    """
    下载图片并保存到指定目录，返回图片保存路径。

    参数:
    url (str): 图片的 URL。
    save_dir (str): 保存图片的目录。

    返回:
    str: 保存的图片文件的路径。
    """

    # 检查保存目录是否存在，如果不存在则创建
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 发送 HTTP 请求获取图片数据
    response = requests.get(url)
    response.raise_for_status()  # 如果请求失败，则引发 HTTPError 异常

    # 生成一个唯一的文件名，避免文件名冲突
    unique_file_name = f"{uuid.uuid4().hex}.jpg"  # 默认使用 .jpg 扩展名，你可以根据需要修改
    file_path = os.path.join(save_dir, unique_file_name)

    # 将图片数据写入文件
    with open(file_path, 'wb') as file:
        file.write(response.content)

    return file_path


def convert_path(path):
    new_path = path.replace('./story', '')
    return new_path


def modify_link(file_path, text):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if 'link:' in line:
            parts = line.split('link: ')
            parts[1] = text
            lines[i] = '      link: ' + text + '\n'
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)


def process_string(original_str, first_content, last_content, log_file_path):
    original_lines = original_str.splitlines()
    original_line_count = len(original_lines)

    delete_first = False
    delete_last = False

    # 检查是否需要删除第一行和最后一行
    if original_line_count >= 1:
        if original_lines[0] == first_content:
            delete_first = True
        if original_lines[-1] == last_content:
            delete_last = True

    # 处理删除操作
    new_lines = original_lines.copy()
    if delete_first and len(new_lines) >= 1:
        new_lines = new_lines[1:]
    if delete_last and len(new_lines) >= 1:
        new_lines = new_lines[:-1]

    # 生成处理后的字符串
    processed_str = '\n'.join(new_lines)

    # 生成日志条目
    log_entries = []
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if delete_first:
        log_entries.append(f"[{timestamp}] 删除了第一行: '{first_content}'")
    if delete_last:
        log_entries.append(f"[{timestamp}] 删除了最后一行: '{last_content}'")

    # 将日志写入文件（自动创建目录）
    if log_entries:
        log_dir = os.path.dirname(log_file_path)
        if log_dir:  # 确保目录路径非空
            os.makedirs(log_dir, exist_ok=True)
        with open(log_file_path, 'a', encoding='utf-8') as log_file:
            for entry in log_entries:
                log_file.write(entry + '\n')

    return processed_str


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    load_dotenv()
    # save_to_md_file(chat_ai("你的生活不会因偶然变好，而是因改变变好。", os.environ.get("API_KEY")), f"./test/{get_today_info()}.md")
    jinshan = get_jinshan()

    img_path = download_image(jinshan.get('fenxiang_img'), './story/images')

    file_name = f"{get_today_info()}.md"

    story = chat_ai(f"我提供的主题是：{jinshan.get('note')}", os.environ.get("API_KEY"))
    story = process_string(story, "```markdown", "```", f"./story/{file_name}.log")
    story = ensure_first_line_is_h1(story)
    story = insert_content_in_fourth_line(story, f"\n![{jinshan.get('note')}]({convert_path(img_path)})\n")

    save_to_md_file(story, f"./story/{file_name}")
    modify_link("./story/index.md", f"/{file_name}")

    # DeepSeek
    ds_reasoning_content, ds_story = chat_ai_ds(f"我提供的主题是：{jinshan.get('note')}", os.environ.get("API_KEY_DS"))

    ds_story = insert_content_in_first_line(ds_story, f"<ReasoningChainRenderer>\n"
                                                      f"{ds_reasoning_content}"
                                                      f"\n</ReasoningChainRenderer>\n")

    file_name = f"{get_today_info()}.md"
    save_to_md_file(ds_story, f"./story/{file_name}")
