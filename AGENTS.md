# 项目知识库 — everyday

AI 每日故事生成器：获取金山词霸每日一句 → 网络搜索增强 → 7+ AI 模型并行生成 → 保存为日期嵌套 Markdown。前端为 VitePress 静态站点，部署于 Cloudflare Pages。

## 命令

```bash
conda activate storygen           # 激活 conda 环境（如命名不同则调整）
pip install -r requirements.txt   # 安装 Python 依赖
python main.py                    # 生成故事（需要 .env API 密钥）
python wordcloud_analysis.py      # 每周词云 + 词频报告
python check.py                   # 归档超大的 chat_logs
ruff check .                      # 代码检查
pytest -v                         # 运行所有测试
pytest tests/test_pipeline.py -v  # 运行单个测试文件
npm run docs:dev                  # VitePress 开发服务器
npm run docs:build                # VitePress 构建
```

## 架构

### 入口与流水线

| 文件 | 职责 |
|------|------|
| `main.py` | 入口：发现模型配置，排除 `EXCLUDED_MODELS`，ThreadPoolExecutor 并行运行 |
| `core/registry.py` | `ModelRegistry.discover()` 动态扫描 `model_configs/*_config.py` |
| `core/chat.py` | `chat_ai()` OpenAI 兼容 API 调用 + 指数退避重试（非流式/流式） |
| `core/pipeline.py` | `run_model(config)` 编排 PREPROCESSORS → chat → POSTPROCESSORS → 文件 |

### 关键常量

- `JINSHAN` / `SEARCH_RESULT`：通过 `model_configs/_shared.py` 的惰性缓存获取（`get_jinshan_cached()` / `get_search_cached()`）
- `EXCLUDED_MODELS` in `main.py:13`：排除思维链/思考模型（doubao_think, doubao, kimi, kimi_k2, zhipu_z1_flash）

### 模型配置（Plugin System）

每个文件在 `model_configs/{name}_config.py`，导出 6 个符号：

| 符号 | 说明 |
|------|------|
| `API_KEY` | `os.getenv("API_KEY_XXX")` |
| `CLIENT_PARAMS` | OpenAI client 参数：`base_url` |
| `CHAT_PARAMS` | Chat 参数：`model`, `messages`, `max_tokens`, `stream`, `extra_body` |
| `PREPROCESSORS` | `[(dict) -> dict]` — API 调用前转换 |
| `POSTPROCESSORS` | `[(dict) -> dict]` — API 响应后转换 |
| `POSTPROCESSOR_FILES` | `[(dict, config_dict) -> None]` — 持久化输出 |

可用处理器函数：
- `processors.format_processors.ensure_first_line_is_h1` — 强制 H1 标题（VitePress 必需）
- `processors.format_processors.insert_content_in_fourth_line` — 在第 4 行插入金山配图
- `processors.format_processors.process_string` — 去除代码块包裹
- `utils.misc.process_reasoning_content` — 提取 `<think>` 推理内容
- `utils.misc.remove_leading_empty_line` — 去除前导空行
- `processors.file_processors.save_to_md_file` — 保存故事到文件
- `utils.misc.out_test` — 用于调试的 stdout 输出

配置可设 `UPDATE_FRONTMATTER = True` 让 `save_to_md_file` 自动更新 `story/index.md` 首页链接（仅 zhipu 配置启用）。

## 工具模块 (`utils/`)

`mish_mash.py` 已拆分：

| 文件 | 职责 |
|------|------|
| `misc.py` | `process_reasoning_content()`, `remove_leading_empty_line()`, `out_test()` |
| `uuid_utils.py` | `fixed_length_uuid()` 生成定长十六进制 ID |
| `web_search.py` | `get_jinshan()`, `web_search()` — 金山词霸 + 智谱搜索 API |
| `yaml_utils.py` | `modify_frontmatter()` — YAML frontmatter 编辑（ruamel.yaml） |
| `image_utils.py` | `download_image()`, `cached_download()` — 图片下载 + 内存缓存 |
| `wordcloud_core.py` | 词云生成核心：分词、频率统计、WordCloud 生成、报告 |
| `metadata_utils.py` | `save_chat_metadata()`, `read_all_metadata()`, `process_stream_chunks()` |

## 约定

- **纯函数式风格**：不使用类（`ModelRegistry` 是目前唯一的例外，用作命名空间）
- **绝对导入**：禁止相对导入
- **f-string 优先**：字符串拼接用 f-string，不用 `%` 或 `+`
- **Logger 名称**：统一 `logging.getLogger("每日故事")`
- **文件写入**：JSON Lines 追加写入（`chat_logs/story_records.json`），兼容旧 JSON 数组格式
- **原子写入**：Markdown 文件通过 `.tmp` 临时文件后 `os.replace()`

## 关键注意点

- **不要在导入时发起 HTTP 请求**：`model_configs/__init__.py` 只做 `load_dotenv()`。各 config 文件使用 `get_jinshan_cached()` / `get_search_cached()` 惰性获取共享数据
- **不要删除 `.env.example`**：它列出了 7 个 API Key 格式
- **测试模拟 API 密钥**：`tests/conftest.py` 会自动注入 mock 环境变量
- **`chat_params.pop("RETRY")` 会修改调用方字典**：`chat_ai()` 内部已做 `params_copy`
- **GitHub Actions**：`main.yml` 每日 23:00 UTC 运行，`wordcloud-analysis.yml` 每周三 00:00 UTC 运行。API 密钥通过 Secrets 注入
- **Cloudflare Pages**：自动从 `story/` 目录构建部署，不依赖本地 `docs:build`
- **`check.py`** 可配置阈值、目标目录和重命名规则，用于归档大型日志文件
