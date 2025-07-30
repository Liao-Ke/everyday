import os
import uuid
from io import StringIO
import logging
import requests
from ruamel.yaml import YAML
import secrets


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


def modify_frontmatter(file_path, key_path, new_value):
    """
    修改Markdown文件中的YAML front matter配置项

    参数:
    file_path (str): Markdown文件路径
    key_path (str): 配置项路径（点分隔格式，如"hero.name"）
    new_value: 新的配置值
    """
    yaml = YAML()
    yaml.preserve_quotes = True  # 保留引号格式
    yaml.width = 120  # 避免长文本自动换行
    yaml.indent(mapping=2, sequence=4, offset=2)  # 保持缩进风格

    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read().splitlines()

    # 定位front matter起始和结束位置
    start_idx = None
    end_idx = None
    for i, line in enumerate(content):
        if line.strip() == '---':
            if start_idx is None:
                start_idx = i
            else:
                end_idx = i
                break

    if start_idx is None or end_idx is None:
        raise ValueError("未找到有效的YAML front matter")

    # 解析YAML内容
    yaml_content = '\n'.join(content[start_idx + 1:end_idx])
    data = yaml.load(yaml_content)

    # 递归查找并修改配置项
    keys = key_path.split('.')
    current = data
    for key in keys[:-1]:
        if key.isdigit() and isinstance(current, list):
            key = int(key)
        current = current[key]

    # 设置新值
    last_key = keys[-1]
    if last_key.isdigit() and isinstance(current, list):
        last_key = int(last_key)
    current[last_key] = new_value

    # 将更新后的YAML写入字符串流
    stream = StringIO()
    yaml.dump(data, stream)
    stream.seek(0)
    updated_yaml = stream.getvalue().splitlines()

    # 重建文件内容
    new_content = content[:start_idx] + ['---'] + updated_yaml + ['---'] + content[end_idx + 1:]

    # 写入文件（使用临时文件避免数据丢失）
    temp_path = file_path + '.tmp'
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_content))

    # 替换原文件
    os.replace(temp_path, file_path)


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


def fixed_length_uuid(length):
    """
    生成加密安全的指定长度随机标识符（十六进制格式）

    参数:
        length (int): 要生成的字符串长度（必须大于0）

    返回:
        str: 指定长度的随机十六进制字符串（小写）

    异常:
        ValueError: 如果长度参数小于1

    特点:
        - 仅依赖secrets模块
        - 完全加密安全
        - 高效利用随机源
        - 支持任意长度（包括奇数）
    """
    if length < 1:
        raise ValueError("长度必须大于0")

    # 计算所需字节数（向上取整）
    num_bytes = (length + 1) // 2

    # 生成安全随机字节
    random_bytes = secrets.token_bytes(num_bytes)

    # 转换为十六进制字符串
    hex_str = random_bytes.hex()

    # 处理奇数长度情况
    if length % 2 == 1:
        # 使用最后一个字节的高4位生成单个字符
        last_char = format(random_bytes[-1] >> 4, 'x')  # 'x' 确保小写十六进制
        return hex_str[:length - 1] + last_char

    return hex_str[:length]
