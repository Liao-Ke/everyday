import os
import re
import glob
from datetime import datetime
from collections import Counter

import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud

from utils.mish_mash import modify_frontmatter, convert_path

# 设置中文字体
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]


def read_stopwords(file_path):
    """读取停词文件，包含中英文和符号"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # 读取所有停用词并转换为小写（英文）和原样（中文）
            return set([line.strip().lower() if re.match(r'^[a-zA-Z]+$', line.strip())
                        else line.strip()
                        for line in f if line.strip()])
    except FileNotFoundError:
        print(f"警告: 停词文件 '{file_path}' 未找到，将使用空停词列表。")
        return set()


def clean_markdown(content):
    """清理Markdown格式，保留文本内容"""
    # 移除ReasoningChainRenderer标签内容
    content = re.sub(r'<ReasoningChainRenderer>[\s\S]*?</ReasoningChainRenderer>', '', content)
    # 移除代码块
    content = re.sub(r'```[\s\S]*?```', '', content)
    # 移除标题标记
    content = re.sub(r'^#+\s', '', content, flags=re.M)
    # 移除链接和图片标记
    content = re.sub(r'\[.*?]\(.*?\)', '', content)
    # 移除列表标记
    content = re.sub(r'^[*\-+]\s', '', content, flags=re.M)
    # 移除其他Markdown符号
    content = re.sub(r'[`*_~>]', '', content)
    # 移除HTML标签
    content = re.sub(r'<[^>]*>', '', content)
    # 移除特殊符号但保留中英文
    content = re.sub(r'[^\w\u4e00-\u9fff\s]', '', content)
    return content


def tokenize_text(text, stopwords):
    """
    使用jieba进行中文分词并过滤停词
    处理中英文混合内容，过滤符号和停用词
    """
    # 使用jieba进行精确模式分词
    words = jieba.lcut(text)
    filtered_words = []

    for word in words:
        # 跳过空词
        if not word.strip():
            continue

        # 统一处理英文单词：转换为小写
        if re.fullmatch(r'[a-zA-Z]+', word):
            word = word.lower()

        # 检查是否为停用词（包括符号）
        if word in stopwords:
            continue

        # 过滤纯数字和单个字符
        if re.fullmatch(r'\d+', word) or len(word) == 1:
            continue

        # 处理中英文混合词（如"Python编程"）
        if any(char.isalpha() or '\u4e00' <= char <= '\u9fff' for char in word):
            filtered_words.append(word)

    return filtered_words


def generate_wordcloud(word_freq, output_path):
    """生成词云并保存"""
    # 创建词云对象
    wordcloud = WordCloud(
        width=800,
        height=600,
        background_color='white',
        font_path='./story/.vitepress/theme/fonts/jinkai.ttf'  # 如果系统中没有SimHei字体，可能需要指定其他字体路径
    ).generate_from_frequencies(word_freq)

    # 保存词云图片
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wordcloud.to_file(output_path)
    return wordcloud


def generate_report(word_freq, file_count, total_words, wordcloud_path, report_path):
    """生成Markdown格式的分析报告"""
    # 获取当前日期
    current_date = datetime.now().strftime('%Y-%m-%d')

    # 生成高频词统计
    top_words = word_freq.most_common(20)
    word_table = "| 词 | 频率 |\n|----|----|\n"
    for word, freq in top_words:
        word_table += f"| {word} | {freq} |\n"

    # 构建报告内容
    report = f"""# 词云分析报告 - {current_date}

## 一、处理概览
- 处理文件数量：{file_count} 个
- 总字数：{total_words} 个
- 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 二、高频词统计（Top 20）
{word_table}

## 三、词云图
![词云图](../images/{os.path.basename(wordcloud_path)})
"""

    # 保存报告
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)


def main():
    """主函数：执行词云分析和报告生成流程"""
    # 获取当前日期
    current_date = datetime.now().strftime('%Y%m%d')
    date_dashed = datetime.now().strftime('%Y-%m-%d')

    # 文件和目录路径
    stopwords_path = "stopwords_full.txt"
    input_dir = "./story/故事/"
    wordcloud_path = f"./story/images/wordcloud_{current_date}.png"
    report_path = f"./story/词云/{date_dashed}.md"

    # 读取停词
    stopwords = read_stopwords(stopwords_path)

    # 递归查找所有.md文件（排除index.md）
    md_files = [f for f in glob.glob(os.path.join(input_dir, '**', '*.md'), recursive=True)
                if os.path.basename(f).lower() != 'index.md']

    # 处理所有文件内容
    all_words = []
    total_words = 0

    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                cleaned_content = clean_markdown(content)
                words = tokenize_text(cleaned_content, stopwords)
                all_words.extend(words)
                total_words += len(words)
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")

    # 统计词频
    word_freq = Counter(all_words)

    # 生成词云
    generate_wordcloud(word_freq, wordcloud_path)

    # 生成报告
    generate_report(word_freq, len(md_files), total_words, wordcloud_path, report_path)

    modify_frontmatter("./story/index.md", "hero.actions.1.link", convert_path(report_path))

    print(f"词云分析完成！")
    print(f"- 词云图片已保存至: {wordcloud_path}")
    print(f"- 分析报告已保存至: {report_path}")


if __name__ == "__main__":
    main()
