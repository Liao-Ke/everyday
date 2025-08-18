import json
import os
import re
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


def out_test(r, n):
    print(n, "<think>", r["reasoning_content"], "</think>\n\n", r["content"]) if "reasoning_content" in r else \
        print(n, r["content"])


def web_search(api_key, search_query, search_engine="search_std",
               search_intent=False, count=10, search_domain_filter=None,
               search_recency_filter="noLimit", content_size="medium",
               request_id=None, user_id=None):
    """
    调用智谱Web Search API进行网络搜索

    参数说明：
    - api_key: 字符串，API访问密钥（必填）
    - search_query: 字符串，搜索内容，不超过70个字符（必填）
    - search_engine: 字符串，搜索引擎类型，可选值：search_std、search_pro、search_pro_sogou、search_pro_quark（必填）
    - search_intent: 布尔值，是否进行搜索意图识别，默认False
    - count: 整数，返回结果条数，1-50之间（默认10）
    - search_domain_filter: 字符串，限定域名（可选）
    - search_recency_filter: 字符串，时间范围，可选值：oneDay、oneWeek、oneMonth、oneYear、noLimit（默认noLimit）
    - content_size: 字符串，内容长度，可选值：medium、high（默认medium）
    - request_id: 字符串，用户端唯一请求标识（可选）
    - user_id: 字符串，终端用户唯一ID，6-128个字符（可选）

    返回：
    - 字典，API返回的搜索结果
    """
    # 检查必填参数
    if not api_key or not search_query:
        raise ValueError("api_key和search_query为必填参数")

    # 验证count参数范围
    if not isinstance(count, int) or count < 1 or count > 50:
        raise ValueError("count参数必须是1-50之间的整数")

    # 验证搜索引擎类型
    valid_engines = ["search_std", "search_pro", "search_pro_sogou", "search_pro_quark"]
    if search_engine not in valid_engines:
        raise ValueError(f"search_engine必须是以下值之一: {', '.join(valid_engines)}")

    # 验证时间范围
    valid_recency = ["oneDay", "oneWeek", "oneMonth", "oneYear", "noLimit"]
    if search_recency_filter not in valid_recency:
        raise ValueError(f"search_recency_filter必须是以下值之一: {', '.join(valid_recency)}")

    # 验证内容长度
    valid_content_sizes = ["medium", "high"]
    if content_size not in valid_content_sizes:
        raise ValueError(f"content_size必须是以下值之一: {', '.join(valid_content_sizes)}")

    # 构建请求URL和头部
    url = "https://open.bigmodel.cn/api/paas/v4/web_search"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # 构建请求数据
    data = {
        "search_query": search_query,
        "search_engine": search_engine,
        "search_intent": search_intent,
        "count": count,
        "search_recency_filter": search_recency_filter,
        "content_size": content_size
    }

    # 添加可选参数
    if search_domain_filter:
        data["search_domain_filter"] = search_domain_filter
    if request_id:
        data["request_id"] = request_id
    if user_id:
        data["user_id"] = user_id

    try:
        # 发送POST请求
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # 检查请求是否成功

        # 解析响应内容
        resp_data = response.json()
        if search_intent and response.json()['search_intent'][0]['intent'] == "SEARCH_NONE":
            logger.info(f"无搜索意图：{response.json()['search_intent']},将关闭意图识别后重试")
            return web_search(api_key, search_query, search_engine, False, count, search_domain_filter,
                              search_recency_filter,
                              content_size, request_id, user_id)

        logger.info(f"网络搜索成功：{response.json()['search_intent']}")
        return resp_data
    except requests.exceptions.RequestException as e:
        logger.error(f"请求发生错误：{e}")
        return None
    except json.JSONDecodeError:
        logger.error("响应内容不是有效的JSON格式")
        return None


def remove_leading_empty_line(d: dict) -> dict:
    """
    去除字符串开头的所有空行（仅包含空白字符的行）

    参数:
        s (str): 输入的字符串

    返回:
        str: 处理后的字符串，已移除所有开头的空行
    """
    lines = d['content'].splitlines(keepends=True)
    # 跳过所有开头空行
    start_index = 0
    for line in lines:
        if line.strip():  # 遇到非空行时停止
            break
        start_index += 1
    d['content'] = ''.join(lines[start_index:])
    return d


def process_reasoning_content(data_dict):
    # 检查字典是否有content键且其值为字符串类型
    if 'content' in data_dict and isinstance(data_dict['content'], str):
        content = data_dict['content']

        # 正则表达式匹配第一对<think>标签及其内容
        think_pattern = r'<think>(.*?)</think>'
        match = re.search(think_pattern, content, re.DOTALL)

        # 提取并存储推理内容
        reasoning_content = match.group(1) if match else ""
        data_dict['reasoning_content'] = reasoning_content

        # 从原始内容中移除匹配到的标签及内容
        if match:
            # 使用re.sub替换第一个匹配项
            data_dict['content'] = re.sub(
                think_pattern,
                '',
                content,
                count=1,
                flags=re.DOTALL
            )

    return data_dict
