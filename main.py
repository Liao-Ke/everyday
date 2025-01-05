# 这是一个示例 Python 脚本。
import os
import uuid

import requests

from zhipuai import ZhipuAI
import zhipuai
import datetime
from dotenv import load_dotenv


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
    date_time_str = today.strftime("%Y年/%m月/%d日/")
    time_str = today.strftime("%H:%M:%S")
    return f"{date_time_str}/{weekday_names[weekday]} {time_str}"


def insert_content_in_fourth_line(s, content):
    lines = s.splitlines()
    if len(lines) < 4:
        lines.append(content)
    else:
        lines.insert(3, content)
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


def chat_ai(msg, api_key):
    client = ZhipuAI(api_key=api_key)  # 请填写您自己的APIKey

    prompt = """
请根据我提供的一句话，以 Markdown 格式的一级标题为这个故事起标题，在标题下方以 Markdown 格式引用该句话。充分释放创意，不限风格、叙事视角、角色、场景、情感基调，创作一个深度贴合该句含义，情节跌宕起伏、扣人心弦且逻辑缜密，字数最少 800 字的故事。
"""
    try:

        response = client.chat.completions.create(
            model="glm-4-flash",  # 请填写您要调用的模型名称
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": msg}
            ],
        )
        return response.choices[0].message.content

    except zhipuai.APIRequestFailedError:
        print('敏感词:', msg)
    except Exception as e:
        print('未知的异常:', e)


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
    file_name = f"{uuid.uuid4().hex}.jpg"  # 默认使用 .jpg 扩展名，你可以根据需要修改
    file_path = os.path.join(save_dir, file_name)

    # 将图片数据写入文件
    with open(file_path, 'wb') as file:
        file.write(response.content)

    return file_path


def convert_path(path):
    new_path = path.replace('./story', '')
    return new_path


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    load_dotenv()
    # save_to_md_file(chat_ai("你的生活不会因偶然变好，而是因改变变好。", os.environ.get("API_KEY")), f"./test/{get_today_info()}.md")
    jinshan = get_jinshan()

    img_path = download_image(jinshan.get('fenxiang_img'), './story/imgages')

    story = chat_ai(jinshan.get('note'), os.environ.get("API_KEY"))
    story = ensure_first_line_is_h1(story)

    story = insert_content_in_fourth_line(story, f"\n![{jinshan.get('note')}]({convert_path(img_path)})")

    save_to_md_file(story, f"./story/{get_today_info()}.md")
