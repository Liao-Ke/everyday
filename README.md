# everyday - AI 每日故事生成器

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/Liao-Ke/everyday?tab=MIT-1-ov-file)
[![在线预览](https://img.shields.io/badge/%20%E5%9C%A8%E7%BA%BF%E9%A2%84%E8%A7%88-story--aii.pages.dev-ff69b4)](https://story-aii.pages.dev/)

根据金山词霸每日一句，通过多个 AI 模型并行生成故事，保存为 Markdown 文件，由 VitePress 静态站点展示。

## 特性

- **多模型并行**：同时调用 7+ AI 模型（DeepSeek、智谱、Kimi、豆包、通义千问、ModelScope、Gemini），ThreadPoolExecutor 并发运行
- **插件式模型配置**：每个模型一个 `*_config.py` 文件，导出 6 个标准化符号即可注册，无需修改核心代码
- **惰性数据加载**：import 时不发起 HTTP 请求，金山词霸每日句和网络搜索结果通过 `model_configs/_shared.py` 惰性获取
- **流水线架构**：PREPROCESSORS → chat → POSTPROCESSORS → 文件持久化，各环节可插拔
- **JSON Lines 日志**：`chat_logs/story_records.json` 追加写入，O(1) 持久化，兼容旧 JSON 数组格式
- **自动归档**：`check.py` 监控日志文件大小，超过阈值自动归档
- **每周词云**：`wordcloud_analysis.py` 对全量故事做分词、词频统计，生成词云图 + 分析报告
- **自动化部署**：GitHub Actions 每日自动生成并提交故事，Cloudflare Pages 自动构建部署

## 快速开始

```bash
git clone https://github.com/Liao-Ke/everyday.git && cd everyday
conda create -n storygen python=3.11 && conda activate storygen
pip install -r requirements.txt
```

## 配置

复制 `.env.example` 为 `.env`，填入 API 密钥：

| 环境变量 | 说明 | 获取地址 |
|----------|------|----------|
| `API_KEY` | 智谱 AI（GLM-4.7/4.5/Z1 Flash） | https://bigmodel.cn |
| `API_KEY_DS` | DeepSeek（V4 Pro + Reasoner） | https://platform.deepseek.com |
| `API_KEY_KIMI` | Kimi（Thinking + K2） | https://platform.moonshot.cn |
| `API_KEY_DOUBAO` | 豆包（1.5 Pro + Thinking） | https://console.volcengine.com/ark |
| `API_KEY_QWEN` | 通义千问（Qwen 3-235B） | https://bailian.console.aliyun.com |
| `API_KEY_MODELSCOPE` | ModelScope（体验模型） | https://modelscope.cn |
| `API_KEY_GEMINI` | Gemini 2.5 Pro | https://aistudio.google.com |

## 使用

```bash
# 生成今日故事
python main.py

# 本地预览 VitePress 站点
npm install && npm run docs:dev

# 生成词云分析报告
python wordcloud_analysis.py

# 归档超大的日志文件
python check.py
```

## 开发

```bash
# 代码检查
ruff check .

# 运行测试
pytest -v

# 运行单个测试文件
pytest tests/test_pipeline.py -v
```

## 项目结构

```
everyday/
├── main.py                       # 入口：发现模型 → 排除 → 并行生成
├── wordcloud_analysis.py         # 词云分析入口
├── check.py                      # 日志归档工具
├── pyproject.toml                # ruff + pytest 配置
├── core/                         # 核心流水线
│   ├── chat.py                   #   OpenAI 兼容 API 调用 + 指数退避重试
│   ├── pipeline.py               #   处理器编排（PRE → chat → POST → FILE）
│   └── registry.py               #   ModelRegistry 自动发现模型配置
├── model_configs/                # 插件式模型配置
│   ├── _shared.py                #   惰性缓存：get_jinshan_cached / get_search_cached
│   ├── deepseek_v3_config.py     #   DeepSeek V4 Pro（余华风格）
│   ├── deepseek_r1_config.py     #   DeepSeek Reasoner
│   ├── zhipu_config.py           #   智谱 GLM-4.7 Flash（含配图）
│   ├── zhipu_4_5_flash_config.py
│   ├── zhipu_z1_flash_config.py  #   智谱推理模型
│   ├── doubao_config.py          #   豆包 1.5 Pro
│   ├── doubao_think_config.py    #   豆包思维链模型
│   ├── kimi_config.py            #   Kimi Thinking（刘慈欣风格）
│   ├── kimi_k2_config.py
│   ├── qwen_config.py            #   通义千问 Qwen 3-235B
│   ├── gemini_config.py
│   └── experience_modelscope_config.py
├── processors/                   # 通用处理器
│   ├── format_processors.py      #   H1 强制、配图注入、代码块清理
│   └── file_processors.py        #   文件保存 + index.md 首页更新
├── utils/                        # 工具模块
│   ├── misc.py                   #   推理内容提取、前导空行清理
│   ├── uuid_utils.py             #   定长 hex UUID 生成
│   ├── web_search.py             #   金山词霸 API + 智谱搜索 API
│   ├── yaml_utils.py             #   YAML frontmatter 编辑
│   ├── image_utils.py            #   图片下载 + 内存缓存
│   ├── wordcloud_core.py         #   分词、词频统计、WordCloud 生成
│   └── metadata_utils.py         #   JSON Lines 元数据持久化 + 流式输出合并
├── config/
│   └── logger_setup.py           # File + Console 双输出日志
├── tests/                        # pytest 测试
│   ├── conftest.py               #   自动 mock 环境变量
│   ├── test_chat.py              #   chat_ai 重试逻辑
│   ├── test_pipeline.py          #   流水线编排
│   ├── test_registry.py          #   模型发现
│   ├── test_processors.py        #   格式处理器
│   └── test_utils.py             #   工具函数
├── story/                        # VitePress 站点 + 内容
│   ├── 故事/                     #   日期嵌套的故事原稿
│   ├── 词云/                     #   词云分析报告
│   ├── images/                   #   配图 + 词云图片
│   └── .vitepress/               #   VitePress 配置 + 组件 + 主题
├── chat_logs/
│   └── story_records.json        #   JSON Lines 接口调用日志
└── .github/workflows/
    ├── main.yml                  #   每日 23:00 UTC 生成故事
    └── wordcloud-analysis.yml    #   每周三 00:00 UTC 词云分析
```

## 添加新模型

1. 在 `.env` 中添加 `API_KEY_XXX`
2. 创建 `model_configs/xxx_config.py`，导出 6 个符号：

| 符号 | 说明 |
|------|------|
| `API_KEY` | `os.getenv("API_KEY_XXX")` |
| `CLIENT_PARAMS` | OpenAI 客户端参数（`base_url`） |
| `CHAT_PARAMS` | Chat 参数（`model`、`messages`、`stream` 等） |
| `PREPROCESSORS` | API 调用前预处理函数列表 |
| `POSTPROCESSORS` | API 响应后处理函数列表 |
| `POSTPROCESSOR_FILES` | 持久化输出函数列表 |

3. 若需排除（如思维链模型），在 `main.py:13` 的 `EXCLUDED_MODELS` 中添加模型名
4. 将 `API_KEY_XXX` 添加到 GitHub Secrets 和 `.github/workflows/main.yml`

## 部署

- **GitHub Actions**：`main.yml` 每日 23:00 UTC 自动运行 `python main.py` 并提交生成的故事
- **Cloudflare Pages**：自动从 `story/` 目录构建部署，无需在 CI 中运行 `npm run docs:build`

## 许可

[MIT License](LICENSE)

## 致谢

- [金山词霸每日一句](https://open.iciba.com/index.php?c=wiki) - 故事灵感来源
- [DeepSeek](https://platform.deepseek.com) · [智谱 AI](https://bigmodel.cn) · [Kimi](https://platform.moonshot.cn) · [豆包](https://console.volcengine.com/ark) · [通义千问](https://bailian.console.aliyun.com) · [ModelScope](https://modelscope.cn) · [Gemini](https://aistudio.google.com) - AI 生成引擎
- [VitePress](https://vitepress.dev) - 文档站点框架
- [Cloudflare Pages](https://pages.cloudflare.com) - 站点部署
