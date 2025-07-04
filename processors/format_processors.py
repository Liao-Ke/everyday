

from model_configs import JINSHAN
import logging

from utils.mish_mash import download_image, convert_path

logger = logging.getLogger('每日故事')


def ensure_first_line_is_h1(markdown_text):
    """
    确保输入字符串的第一行是 Markdown 格式的一级标题。

    参数:
    markdown_text (str): 输入的 Markdown 文本。

    返回:
    str: 调整后的 Markdown 文本，确保第一行是一级标题。
    """
    lines = markdown_text['content'].splitlines()
    if not lines:
        return markdown_text  # 空输入直接返回

    first_line = lines[0]
    count = 0

    # 统计行首连续的 '#' 数量
    for char in first_line:
        if char == '#':
            count += 1
        else:
            break

    # 处理标题行（1-6级标题）
    if 1 <= count <= 6:
        # 移除开头的 '#' 和后续空白，构造新的一级标题
        rest = first_line[count:].lstrip()
        lines[0] = '# ' + rest
    else:
        # 非标题行或空行：直接添加一级标题标记
        lines[0] = '# ' + first_line

    markdown_text['content'] = '\n'.join(lines)

    return markdown_text


def format_story(story):
    """格式化故事内容"""
    story['content'] = f"\n{'=' * 40}\n{story['content'].strip()}\n{'=' * 40}\n"
    return story


def insert_content_in_fourth_line(s):
    image_path = download_image(JINSHAN.get('fenxiang_img'), "./story/images")
    logger.info(f"下载图片成功: {image_path}")
    lines = s['content'].splitlines()
    content = f"\n![{JINSHAN.get('note')}]({convert_path(image_path)})\n"
    if len(lines) < 4:
        lines.append(content)
    else:
        lines.insert(3, content)
    s['content'] = '\n'.join(lines)
    return s


def process_string(original_str, first_content="```", last_content="```"):
    original_lines = original_str['content'].splitlines()
    original_line_count = len(original_lines)

    delete_first = False
    delete_last = False

    # 检查是否需要删除第一行和最后一行
    if original_line_count >= 1:
        if first_content in original_lines[0]:
            delete_first = True
        if last_content in original_lines[-1]:
            delete_last = True

    # 处理删除操作
    new_lines = original_lines.copy()
    if delete_first and len(new_lines) >= 1:
        new_lines = new_lines[1:]
    if delete_last and len(new_lines) >= 1:
        new_lines = new_lines[:-1]

    # 生成处理后的字符串
    processed_str = '\n'.join(new_lines)

    if delete_first:
        logger.info(f" 删除了第一行: '{first_content}'")
    if delete_last:
        logger.info(f"删除了最后一行: '{last_content}'")

    original_str['content'] = processed_str
    return original_str
