import os
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud

plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]


def read_stopwords(file_path):
    try:
        with open(file_path, encoding="utf-8") as f:
            result = set()
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if re.fullmatch(r"[a-zA-Z]+", line):
                    result.add(line.lower())
                else:
                    result.add(line)
            return result
    except FileNotFoundError:
        print(f"警告: 停词文件 '{file_path}' 未找到，将使用空停词列表。")
        return set()


def clean_markdown(content):
    content = re.sub(r"<(ReasoningChainRenderer|code|pre)>[\s\S]*?</\1>", "", content)
    content = re.sub(r"[#*_~>`\[\]()\-+!|]", "", content)
    content = re.sub(r"[^\w\u4e00-\u9fff\s。，！？、；：" "''（）]", "", content)
    return content


def tokenize_text(text, stopwords):
    words = jieba.lcut(text)
    filtered = []

    for word in words:
        word = word.strip()
        if not word:
            continue

        if re.fullmatch(r"[a-zA-Z]+", word):
            word = word.lower()

        if word in stopwords:
            continue

        if re.fullmatch(r"\d+", word):
            continue

        if len(word) == 1 and re.fullmatch(r"[a-zA-Z]", word):
            continue

        if any(c.isalpha() or "\u4e00" <= c <= "\u9fff" for c in word):
            filtered.append(word)

    return filtered


def process_file(file_path, stopwords):
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        cleaned = clean_markdown(content)
        return tokenize_text(cleaned, stopwords)
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")
        return []


def build_word_freq(files, stopwords, workers=8):
    all_words = []
    total_words = 0

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(process_file, fp, stopwords): fp for fp in files}
        try:
            from tqdm import tqdm

            iterator = tqdm(as_completed(futures), total=len(futures), desc="分词中")
        except ImportError:
            iterator = as_completed(futures)

        for future in iterator:
            words = future.result()
            all_words.extend(words)
            total_words += len(words)

    word_freq = Counter(all_words)
    return word_freq, total_words


def generate_wordcloud(word_freq, output_path, min_freq=2, max_words=200, width=1200, height=800, font_path=""):
    filtered = {w: f for w, f in word_freq.items() if f >= min_freq}
    if not font_path:
        font_path = "./story/.vitepress/theme/fonts/jinkai.ttf"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wc = WordCloud(
        width=width,
        height=height,
        background_color="white",
        max_words=max_words,
        font_path=font_path,
    ).generate_from_frequencies(filtered)
    wc.to_file(output_path)
    return wc


def generate_report(word_freq, file_count, total_words, wordcloud_path, report_path, top_n=20):
    top_words = word_freq.most_common(top_n)
    word_table = "| 词 | 频率 |\n|----|----|\n"
    for word, freq in top_words:
        word_table += f"| {word} | {freq} |\n"

    report = f"""# 词云分析报告

## 一、处理概览
- 处理文件数量：{file_count} 个
- 总字数：{total_words} 个
- 生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 二、高频词统计（Top {top_n}）
{word_table}

## 三、词云图
![词云图](../images/{os.path.basename(wordcloud_path)})
"""

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
