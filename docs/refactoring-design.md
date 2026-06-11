# 重构设计方案 — everyday

日期：2026-06-11
状态：已审阅

## 1. 目标

对 AI 每日故事生成器进行系统性重构，消除技术债务，提升可维护性、可测试性和代码质量。

## 2. 范围

| 模块 | 重构方式 | 文件 | 行数 |
|------|----------|------|------|
| 核心流水线 | 拆分 main.py → core/{pipeline,chat,registry}.py | ~4 新建 | ~307 |
| utils | 拆分 mish_mash.py → 5 个独立模块 | ~5 新建 | ~321 |
| model_configs | 消除导入时副作用，惰性加载 | __init__.py + _shared.py | ~19 |
| processors | frontmatter 配置驱动，图片缓存 | file_processors.py, format_processors.py | ~137 |
| 日志 | JSON 全量重写 → JSON Lines 追加 | metadata_utils.py | ~198 |
| 死代码 | 删除 main.old.py, deploy.yml, 注释配置 | 删除 | ~989 |
| wordcloud | 算法重构 + 模块化 | wordcloud_core.py + 精简入口 | ~183 |
| VitePress | 清理级 | 6 个文件 | ~350 |
| GitHub Actions | 统一 push, 删除 deploy, 去掉 npm build | 2 个 workflow | ~81 |
| .env | 新增 .env.example + 启动校验 | 新建 ~1 | ~15 |
| 测试 | pytest + mock | ~6 个文件 | 新建 |
| 工具链 | ruff | pyproject.toml | 新建 |

## 3. 设计决策

### 3.1 模块拆分：mish_mash.py → 5 独立模块

**动机**：321 行万能工具模块，职责混杂，改动时难以定位。

| 新文件 | 迁入函数 | 说明 |
|--------|----------|------|
| `utils/web_search.py` | `get_jinshan()`, `web_search()` | Zhipu 搜索 API 客户端 |
| `utils/image_utils.py` | `download_image()`, 新增 `cached_download()` | 图片下载 + 内存缓存 |
| `utils/yaml_utils.py` | `modify_frontmatter()`, `convert_path()` | YAML frontmatter 编辑 |
| `utils/uuid_utils.py` | `fixed_length_uuid()` | UUID 生成 |
| `utils/misc.py` | `remove_leading_empty_line()`, `process_reasoning_content()`, `out_test()` | 其余零散工具 |

迁移后更新所有 `from utils.mish_mash import X` 引用，删除 `utils/mish_mash.py`。

### 3.2 消除导入时副作用

**动机**：`model_configs/__init__.py` 在导入时发起 HTTP 请求（金山词霸 + Zhipu 搜索），网络不可用则全程序崩溃。`kimi_config.py` 同理在导入时调用 token 估算 API。

**方案**：

- `model_configs/__init__.py` 仅保留 `load_dotenv()`，移除 `get_jinshan()`/`web_search()` 调用
- 新增 `model_configs/_shared.py`，使用惰性加载：

```python
_JINSHAN_CACHE = None
_SEARCH_CACHE = None

def get_jinshan_cached():
    global _JINSHAN_CACHE
    if _JINSHAN_CACHE is None:
        from utils.web_search import get_jinshan
        _JINSHAN_CACHE = get_jinshan()
    return _JINSHAN_CACHE
```

- 各 `*_config.py` 的 `CHAT_PARAMS` 中使用 `get_jinshan_cached()` 替代 `from model_configs import JINSHAN`
- `kimi_config.py`：token 估算从导入时移到 `PREPROCESSORS` 中按需调用

### 3.3 ModelRegistry

**动机**：`config_map` 硬编码 9 个模型在 `main.py` 中，新增/删除模型需要修改主文件。

**方案**：

```python
# core/registry.py
class ModelRegistry:
    _configs: dict[str, dict] = {}

    @classmethod
    def discover(cls) -> dict[str, dict]:
        """扫描 model_configs/*_config.py，动态导入 6 符号"""
        ...

    @classmethod
    def get(cls, name: str) -> dict | None: ...
```

### 3.4 流水线优化

**动机**：`story_generator()` 在 main.py 中，不可独立测试；`chat_params.pop("RETRY")` 篡改调用方字典；`random.shuffle()` 引入非确定性；frontmatter 更新与模型名耦合。

**方案**：

- 新建 `core/chat.py`：迁入 `chat_ai()`，保留签名
- 新建 `core/pipeline.py`：`run_model(config, *, chat_fn=None)`，`chat_fn` 可注入 mock
- 各配置新增 `UPDATE_FRONTMATTER = True/False`，`save_to_md_file()` 据此决定是否更新首页链接
- `chat_params.pop("RETRY")` → `deepcopy(chat_params)` + `config.get("RETRY", True)`
- 移除 `random.shuffle()`，按注册顺序执行
- `setup_logger()` 加防重复处理器检查

### 3.5 日志追加写入

**动机**：`_save_to_json()` 每次追加读 → append → 重写全文件，O(n) 增长。

**方案**：

```python
def _save_to_json(data: dict, filepath: str) -> None:
    """按行追加一条 JSON 记录（JSON Lines），O(1)"""
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")
```

`read_all_metadata()` 兼容旧 JSON 数组格式和新 JSON Lines 格式。
`check.py` 的归档逻辑适配新格式。

### 3.6 图片缓存

**动机**：`insert_content_in_fourth_line()` 每次运行下载金山配图，多个模型重复下载。

**方案**：`utils/image_utils.py` 新增 `cached_download()`，内存缓存 + 文件系统幂等（同名 URL 存同名文件）。

### 3.7 wordcloud 算法重构

**动机**：183 行单体脚本，正则 7 次扫描、文件串行处理、WordCloud 参数硬编码、单字词一刀切、无进度提示。

**方案**：

算法改进点：

| 改进 | 现状 | 改为 |
|------|------|------|
| 正则合并 | 7 次独立 `re.sub` 扫描 | 合并为 2-3 次，去除重叠匹配 |
| 文件扫描 | 串行 2,485 个文件 | `ThreadPoolExecutor(8)` + `tqdm` 进度条 |
| min_freq 过滤 | WordCloud 默认全部词参与 | 过滤仅出现 1-2 次的噪声词 |
| 单字词过滤 | `len(word)==1` 一刀切 | 中文单字仅由停词表过滤 |
| WordCloud 参数 | `800x600` 硬编码 | 可配置（width,height,max_words,min_freq） |
| jieba 词典 | 默认词典 | 注入故事领域自定义词典 |
| 报告 | Top 20 硬编码 | `generate_report(..., top_n=20)` 参数化 |

模块化：

```python
# utils/wordcloud_core.py
def read_stopwords(path: str) -> set[str]: ...
def clean_markdown(content: str) -> str: ...
def tokenize_text(text: str, stopwords: set[str]) -> list[str]: ...
def process_file(path: str, stopwords: set[str]) -> list[str]: ...
def build_word_freq(files: list[str], stopwords: set[str], ...) -> Counter: ...
def generate_wordcloud(word_freq: Counter, output_path: str, min_freq=2, max_words=200, ...): ...
def generate_report(word_freq: Counter, file_count: int, total_words: int, report_path: str, top_n=30): ...
```

`wordcloud_analysis.py` 精简为 CLI 入口，移除 `utils.mish_mash` 依赖。

### 3.8 VitePress 清理级

**动机**：emoji 做图标、首页占位卡片、硬编码排除文件、注释 CSS、404 文案不贴切。

| 文件 | 改动 |
|------|------|
| `WordCount.vue` | emoji（📝🔠⏱️）→ Lucide SVG 图标；启用移动端样式 |
| `index.md` | 特色卡片"A/B/C" → 真实功能描述 |
| `my.css` | 清理注释代码；字号 18px → 响应式 |
| `config.mts` | 启用 `og:image`；`srcExclude` 硬编码文件 → pattern 排除 |
| `MyLayout.vue` | 404 文案优化；清理未使用 import |
| `ReasoningChainRenderer.vue` | 清理注释 CSS |

### 3.9 GitHub Actions

- 删除 `.github/workflows/deploy.yml`（Cloudflare Pages 已接管）
- `main.yml`：`ad-m/github-push-action@master` → 原生 `git push`
- `wordcloud-analysis.yml`：同上统一
- 两个 workflow 统一使用 `actions/setup-python@v5`
- `main.yml` 移除 `npm run docs:build`（Cloudflare Pages 自动构建）

### 3.10 .env 管理

- 新建 `.env.example`：列出 7 个 API Key，每个带注释说明使用模型
- `main.py` 启动时校验必需环境变量，缺失时打印警告

## 4. 执行顺序

| 步骤 | 内容 | 验证 |
|------|------|------|
| 0 | 工具链：pyproject.toml + ruff + pytest 依赖 | `ruff check .` 通过 |
| 1 | 死代码：删除 main.old.py, deploy.yml, 注释配置 | 文件不存在 |
| 2 | 拆分 mish_mash.py → 5 独立模块 | 各模块 import 正常 |
| 3 | 消除导入时副作用 + ModelRegistry | import 不发起 HTTP |
| 4 | 流水线优化：core/{pipeline,chat}.py + 配置驱动 frontmatter | `python main.py` 正常 |
| 5 | 日志 JSON Lines + 图片缓存 | 写入验证 |
| 6 | wordcloud 算法重构 + 模块化 | `python wordcloud_analysis.py` |
| 7 | VitePress 清理级 | `npm run docs:build` 通过 |
| 8 | GitHub Actions 统一 + .env.example | check workflows |
| 9 | 测试编写 | `pytest -v` 通过 |

## 5. 不变内容

- 模型 prompt/创作风格（`*_config.py` 的 system prompt）
- VitePress UI 功能改造（归档页、RSS 属于 B 级，本次不做）
- `.env` 密钥本身（保持 gitignored）
- GitHub Actions cron 调度时间
- VitePress 页面结构（不做 UI 重设计）
