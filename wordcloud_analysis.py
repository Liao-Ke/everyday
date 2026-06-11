import glob
import os
from datetime import datetime

from utils.wordcloud_core import build_word_freq, generate_report, generate_wordcloud, read_stopwords
from utils.yaml_utils import convert_path, modify_frontmatter

STOPWORDS_PATH = "stopwords_full.txt"
INPUT_DIR = "./story/故事/"
IMAGES_DIR = "./story/images/"
REPORTS_DIR = "./story/词云/"


def main():
    current_date = datetime.now().strftime("%Y%m%d")
    date_dashed = datetime.now().strftime("%Y-%m-%d")

    wordcloud_path = os.path.join(IMAGES_DIR, f"wordcloud_{current_date}.png")
    report_path = os.path.join(REPORTS_DIR, f"{date_dashed}.md")

    stopwords = read_stopwords(STOPWORDS_PATH)

    md_files = [
        f
        for f in glob.glob(os.path.join(INPUT_DIR, "**", "*.md"), recursive=True)
        if os.path.basename(f).lower() != "index.md"
    ]

    word_freq, total_words = build_word_freq(md_files, stopwords)

    generate_wordcloud(word_freq, wordcloud_path)
    generate_report(word_freq, len(md_files), total_words, wordcloud_path, report_path)

    modify_frontmatter("./story/index.md", "hero.actions.1.link", convert_path(report_path))

    print("词云分析完成！")
    print(f"- 词云图片已保存至: {wordcloud_path}")
    print(f"- 分析报告已保存至: {report_path}")


if __name__ == "__main__":
    main()
