# everyday 重构实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 全面重构 everyday 项目，消除技术债务，提升可维护性、可测试性和代码质量。

**Architecture:** 保持现有流水线架构（preprocessors → API → postprocessors → file save），拆分 main.py 到 core/，拆分 mish_mash.py 到独立模块，消除导入时副作用，引入测试 + ruff。

**Tech Stack:** Python 3.11, pytest, ruff, VitePress

**设计文档:** `docs/refactoring-design.md`

---

## 文件映射

### 新建文件
| 路径 | 职责 |
|------|------|
| `core/__init__.py` | 包初始化 |
| `core/registry.py` | ModelRegistry: 自动发现模型配置 |
| `core/pipeline.py` | `run_model()` 流水线编排 |
| `core/chat.py` | `chat_ai()` API 调用逻辑（从 main.py 迁出） |
| `utils/web_search.py` | `get_jinshan()`, `web_search()` |
| `utils/image_utils.py` | `download_image()`, `cached_download()` |
| `utils/yaml_utils.py` | `modify_frontmatter()`, `convert_path()` |
| `utils/uuid_utils.py` | `fixed_length_uuid()` |
| `utils/misc.py` | `remove_leading_empty_line()`, `process_reasoning_content()`, `out_test()` |
| `utils/wordcloud_core.py` | 词云核心算法 |
| `model_configs/_shared.py` | 惰性加载 JINSHAN + SEARCH_RESULT |
| `.env.example` | API Key 模板 |
| `pyproject.toml` | ruff + pytest 配置 |
| `tests/conftest.py` | pytest fixture |
| `tests/test_chat.py` | chat_ai() 测试 |
| `tests/test_pipeline.py` | 流水线测试 |
| `tests/test_processors.py` | 格式处理测试 |
| `tests/test_utils.py` | 工具函数测试 |
| `tests/test_registry.py` | ModelRegistry 测试 |

### 修改文件
| 路径 | 修改内容 |
|------|----------|
| `main.py` | 精简：调用 core/ 模块，去掉 config_map 硬编码 |
| `model_configs/__init__.py` | 去掉 HTTP 副作用 |
| `processors/file_processors.py` | frontmatter 改为配置驱动 |
| `processors/format_processors.py` | lambda 改具名函数，复用图片缓存 |
| `utils/metadata_utils.py` | JSON 全量重写 → JSON Lines 追加 |
| `config/logger_setup.py` | 防重复调用保护 |
| `wordcloud_analysis.py` | 精简为 CLI 入口 |
| `story/.vitepress/components/WordCount.vue` | emoji → SVG，移动端样式 |
| `story/.vitepress/theme/styles/my.css` | 清理注释，响应式字号 |
| `story/.vitepress/config.mts` | OG 图片启用，排除硬编码清理 |
| `story/index.md` | 特色卡片真实描述 |
| `story/.vitepress/theme/MyLayout.vue` | 404 文案，清理 import |
| `story/.vitepress/components/ReasoningChainRenderer.vue` | 清理注释 CSS |
| `story/.vitepress/theme/index.ts` | 清理注释代码 |
| `story/.vitepress/theme/Layout.vue` | 清理未使用变量 |
| `.github/workflows/main.yml` | 统一 push，去掉 npm build |
| `.github/workflows/wordcloud-analysis.yml` | 统一 push |
| `check.py` | 适配 JSON Lines 格式 |
| `requirements.txt` | 加 pytest, pytest-mock, ruff |

### 删除文件
| 路径 | 原因 |
|------|------|
| `main.old.py` | 死代码 |
| `utils/mish_mash.py` | 拆分后废弃 |
| `.github/workflows/deploy.yml` | Cloudflare Pages 已接管 |
| `utils/__pycache__/untitled-*.pyc` | 残留缓存 |

---

## 任务分解

### 步骤 0：工具链 + 格式化

**Files:**
- Create: `pyproject.toml`
- Modify: `requirements.txt`
- Run: ruff check + format 全库

- [ ] **创建 pyproject.toml**

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "W", "UP", "N", "SIM", "ARG"]
ignore = ["N802", "N803", "N815", "N816"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **更新 requirements.txt**

```
openai==1.68.2
python-dotenv==1.0.1
jieba==0.42.1
wordcloud==1.9.3
matplotlib==3.9.2
ruamel.yaml==0.18.6
tqdm>=4.66.0
pytest>=8.0.0
pytest-mock>=3.14.0
ruff>=0.9.0
```

- [ ] **运行 ruff 格式化全库**

```bash
ruff check --fix . && ruff format .
```

- [ ] **提交**

```bash
git add -A && git commit -m "04重构：添加 ruff + pytest 配置，全库格式化"
```

### 步骤 1：死代码清理

**Files:**
- Delete: `main.old.py`, `.github/workflows/deploy.yml`
- Clean: 各 `*_config.py` 中注释掉的模型配置

- [ ] **删除 main.old.py**

```bash
rm main.old.py
```

- [ ] **删除 deploy.yml**

```bash
rm .github/workflows/deploy.yml
```

- [ ] **清理各 config 中注释掉的模型配置**（如 kimi、豆包思考、zhipu-z1 中被 `#` 注释的部分，实际保留代码未被注释的保留不动即可——确认后仅删除被完整注释的备选模型块）

- [ ] **提交**

```bash
git add -A && git commit -m "04重构：清理死代码"
```

### 步骤 2：拆分 mish_mash.py

**Files:** 新建 5 个文件，修改所有 import 引用，删除原文件

- [ ] **创建 utils/web_search.py**

```python
import json
import requests
from typing import Any

JINSHAN_URL = "https://open.iciba.com/dsapi/"

def get_jinshan() -> dict[str, str]:
    """获取金山词霸每日一句"""
    try:
        resp = requests.get(JINSHAN_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {"note": data.get("note", ""), "fenxiang_img": data.get("fenxiang_img", "")}
    except Exception as e:
        import logging
        logging.getLogger("每日故事").warning(f"获取金山词霸失败: {e}")
        return {"note": "", "fenxiang_img": ""}

def web_search(query: str = "") -> dict[str, Any]:
    """Zhipu 搜索 API 客户端"""
    from zhipuai import ZhipuAI
    api_key = os.getenv("API_KEY")
    if not api_key:
        return {"content": "", "status": "no_api_key"}
    client = ZhipuAI(api_key=api_key)
    try:
        resp = client.chat.completions.create(
            model="web-search-pro",
            messages=[{"role": "user", "content": query or f"查询今天的新闻热点和文化事件，日期是{datetime.now().strftime('%Y年%m月%d日')}"}],
        )
        return {"content": resp.choices[0].message.content, "status": "success"}
    except Exception as e:
        import logging
        logging.getLogger("每日故事").warning(f"网络搜索失败: {e}")
        if not query:
            return web_search("今天的重大新闻")
        return {"content": "", "status": "error"}
```

- [ ] **创建 utils/image_utils.py**

```python
import os
import uuid
import requests

_IMAGE_CACHE: dict[str, str] = {}

def download_image(url: str, save_dir: str = "./story/images/") -> str | None:
    """下载图片到本地，返回相对路径"""
    try:
        ext = os.path.splitext(url.split("?")[0])[1] or ".jpg"
        filename = f"{uuid.uuid4().hex[:8]}{ext}"
        os.makedirs(save_dir, exist_ok=True)
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        filepath = os.path.join(save_dir, filename)
        with open(filepath, "wb") as f:
            f.write(resp.content)
        return f"./story/images/{filename}"
    except Exception as e:
        import logging
        logging.getLogger("每日故事").warning(f"下载图片失败 {url}: {e}")
        return None

def cached_download(url: str, save_dir: str = "./story/images/") -> str | None:
    """带缓存的图片下载，同一 URL 不重复请求"""
    if url in _IMAGE_CACHE:
        return _IMAGE_CACHE[url]
    path = download_image(url, save_dir)
    if path:
        _IMAGE_CACHE[url] = path
    return path
```

- [ ] **创建 utils/yaml_utils.py**

```python
import os
from ruamel.yaml import YAML

yaml = YAML()
yaml.preserve_quotes = True

def convert_path(path: str) -> str:
    return path.replace("./story", "")

def modify_frontmatter(filepath: str, key_path: str, value: str) -> None:
    """递归点分隔键路径更新 YAML frontmatter，原子写入"""
    temp = filepath + ".tmp"
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if not lines or lines[0].strip() != "---":
            return
        end = next(i for i, l in enumerate(lines[1:], 1) if l.strip() == "---")
        body = "".join(lines[1:end])
        data = yaml.load(body) or {}
        keys = key_path.split(".")
        target = data
        for k in keys[:-1]:
            if isinstance(target.get(k), list):
                target = target[k][0] if target[k] else {}
            else:
                target = target.setdefault(k, {})
        target[keys[-1]] = value
        with open(temp, "w", encoding="utf-8") as f:
            f.write("---\n")
            yaml.dump(data, f)
            f.write("---\n")
            f.writelines(lines[end + 1:])
        os.replace(temp, filepath)
    except Exception as e:
        import logging
        logging.getLogger("每日故事").error(f"修改 frontmatter 失败: {e}")
        if os.path.exists(temp):
            os.remove(temp)
```

- [ ] **创建 utils/uuid_utils.py**

```python
import secrets

def fixed_length_uuid(length: int = 3) -> str:
    """生成加密安全十六进制短标识符"""
    return secrets.token_hex(length)
```

- [ ] **创建 utils/misc.py**

```python
import re

def remove_leading_empty_line(content: str) -> str:
    return re.sub(r"^\s*\n", "", content, count=1)

def process_reasoning_content(response: dict) -> dict:
    """从 <think> 标签提取 reasoning_content"""
    content = response.get("content", "")
    if not content.startswith("<think>"):
        return response
    match = re.match(r"<think>(.*?)</think>\s*(.*)", content, re.DOTALL)
    if match:
        response["reasoning_content"] = match.group(1).strip()
        response["content"] = match.group(2).strip()
    return response

def out_test(*args, **kwargs):
    print(*args, **kwargs)
```

- [ ] **更新所有 import 引用**
  查找 `from utils.mish_mash import` 和 `import utils.mish_mash` 引用，改为对应新模块

  受影响的文件：`main.py`, `processors/format_processors.py`, `processors/file_processors.py`, `wordcloud_analysis.py`, `model_configs/__init__.py`, `model_configs/zhipu_config.py`

- [ ] **删除 utils/mish_mash.py**

```bash
rm utils/mish_mash.py
```

- [ ] **提交**

```bash
git add -A && git commit -m "04重构：拆分 mish_mash.py 为 5 个独立模块"
```

### 步骤 3：消除导入时副作用 + ModelRegistry

**Files:**
- Create: `model_configs/_shared.py`, `core/__init__.py`, `core/registry.py`
- Modify: `model_configs/__init__.py`, 各 `*_config.py`, `main.py`, `kimi_config.py`

- [ ] **创建 model_configs/_shared.py**

```python
_JINSHAN_CACHE = None
_SEARCH_CACHE = None

def get_jinshan_cached():
    global _JINSHAN_CACHE
    if _JINSHAN_CACHE is None:
        from utils.web_search import get_jinshan
        _JINSHAN_CACHE = get_jinshan()
    return _JINSHAN_CACHE

def get_search_cached():
    global _SEARCH_CACHE
    if _SEARCH_CACHE is None:
        from utils.web_search import web_search
        _SEARCH_CACHE = web_search()
    return _SEARCH_CACHE
```

- [ ] **更新 model_configs/__init__.py** — 去掉 HTTP 调用

```python
from dotenv import load_dotenv

load_dotenv()
```

- [ ] **更新各 `*_config.py`** — `from model_configs import JINSHAN` → `from model_configs._shared import get_jinshan_cached`，在 CHAT_PARAMS 内部调用

- [ ] **更新 kimi_config.py** — 导入时 token 估算移到 PREPROCESSORS

- [ ] **创建 core/__init__.py**

```python
```

- [ ] **创建 core/registry.py**

```python
import importlib
import pkgutil
from typing import Any

import model_configs

REQUIRED_SYMBOLS = ["API_KEY", "CLIENT_PARAMS", "CHAT_PARAMS", "PREPROCESSORS", "POSTPROCESSORS", "POSTPROCESSOR_FILES"]

class ModelRegistry:
    _configs: dict[str, dict] = {}

    @classmethod
    def discover(cls) -> dict[str, dict]:
        if cls._configs:
            return cls._configs
        for importer, modname, ispkg in pkgutil.iter_modules(model_configs.__path__):
            if modname.startswith("_") or not modname.endswith("_config"):
                continue
            try:
                mod = importlib.import_module(f"model_configs.{modname}")
                config = {}
                for sym in REQUIRED_SYMBOLS:
                    config[sym] = getattr(mod, sym, None)
                config["name"] = modname.removesuffix("_config")
                if config["API_KEY"]:
                    cls._configs[config["name"]] = config
            except Exception as e:
                import logging
                logging.getLogger("每日故事").warning(f"加载模型配置 {modname} 失败: {e}")
        return cls._configs

    @classmethod
    def get(cls, name: str) -> dict | None:
        return cls._configs.get(name)

    @classmethod
    def names(cls) -> list[str]:
        return list(cls._configs.keys())
```

- [ ] **更新 main.py** — 替换 config_map 硬编码

```python
# 删除 config_map = {...} 硬编码
# 改为：
from core.registry import ModelRegistry
configs = ModelRegistry.discover()
models_to_use = [name for name, cfg in configs.items() if cfg.get("API_KEY")]
```

- [ ] **提交**

```bash
git add -A && git commit -m "04重构：消除导入时副作用 + ModelRegistry"
```

### 步骤 4：流水线优化

**Files:**
- Create: `core/chat.py`, `core/pipeline.py`
- Modify: `main.py`, `processors/file_processors.py`, `config/logger_setup.py`

- [ ] **创建 core/chat.py**

从 main.py 迁入 `chat_ai()`，保持签名不变。
使用 `copy.deepcopy(params)` 防止篡改调用方字典。

- [ ] **创建 core/pipeline.py**

```python
from core.chat import chat_ai

def run_model(config: dict, *, chat_fn=None) -> dict | None:
    params = {}
    params.update(config.get("CHAT_PARAMS", {}))
    for pre in config.get("PREPROCESSORS", []):
        pre(params)
    response = (chat_fn or chat_ai)(config, params)
    if response is None:
        return None
    for post in config.get("POSTPROCESSORS", []):
        post(response)
    for file_fn in config.get("POSTPROCESSOR_FILES", []):
        file_fn(response, config)
    return response
```

- [ ] **更新 main.py** — story_generator() → pipeline.run_model()

- [ ] **更新 processors/file_processors.py** — frontmatter 改为配置驱动

```python
def save_to_md_file(response: dict, config: dict) -> None:
    ...
    if config.get("UPDATE_FRONTMATTER", False):
        modify_frontmatter("./story/index.md", "hero.actions.0.link", ...)
```

- [ ] **更新 config/logger_setup.py**

```python
_LOGGER_INITIALIZED = False

def setup_logger():
    global _LOGGER_INITIALIZED
    if _LOGGER_INITIALIZED:
        return logging.getLogger("每日故事")
    _LOGGER_INITIALIZED = True
    ...
```

- [ ] **提交**

```bash
git add -A && git commit -m "04重构：流水线优化 + 配置驱动 frontmatter"
```

### 步骤 5：日志 + 缓存

**Files:**
- Modify: `utils/metadata_utils.py`, `check.py`

- [ ] **更新 utils/metadata_utils.py** — JSON 全量重写 → 按行追加

- [ ] **更新 check.py** — 适配 JSON Lines 格式

- [ ] **提交**

```bash
git add -A && git commit -m "04重构：日志改为 JSON Lines 追加写入"
```

### 步骤 6：wordcloud 重构

**Files:**
- Create: `utils/wordcloud_core.py`
- Modify: `wordcloud_analysis.py`

- [ ] **创建 utils/wordcloud_core.py** — 迁入核心算法，正则合并、并行处理、min_freq 过滤

- [ ] **更新 wordcloud_analysis.py** — 精简为 CLI 入口

- [ ] **提交**

```bash
git add -A && git commit -m "04重构：wordcloud 算法重构 + 模块化"
```

### 步骤 7：VitePress 清理

**Files:**
- Modify: `WordCount.vue`, `my.css`, `config.mts`, `index.md`, `MyLayout.vue`, `ReasoningChainRenderer.vue`, `index.ts`, `Layout.vue`

- [ ] **WordCount.vue** — emoji 替换为 SVG（可内联或使用简单 Unicode 符号替代方案）

- [ ] **my.css** — 清理注释，字号添加响应式 `font-size: clamp(16px, 1.2vw + 14px, 18px)`

- [ ] **config.mts** — 启用 og:image，srcExclude 改用 pattern

- [ ] **index.md** — 特色卡片改为真实描述

- [ ] **MyLayout.vue** — 404 文案优化，清理 unused import

- [ ] **ReasoningChainRenderer.vue** — 清理注释 CSS

- [ ] **index.ts** — 清理注释代码

- [ ] **Layout.vue** — 清理未使用变量

- [ ] **提交**

```bash
git add -A && git commit -m "04重构：VitePress 前端清理级优化"
```

### 步骤 8：GitHub Actions + .env

**Files:**
- Modify: `.github/workflows/main.yml`, `.github/workflows/wordcloud-analysis.yml`
- Create: `.env.example`

- [ ] **更新 main.yml**

删除 `ad-m/github-push-action`，删除 `npm run docs:build`，改为：

```yaml
      - run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add .
          git diff --cached --quiet || git commit -m "Add story"
          git push
```

- [ ] **更新 wordcloud-analysis.yml** — 同上统一 push

- [ ] **创建 .env.example**

```
# 智谱 AI (GLM-4.7/4.5/Z1 Flash)
API_KEY=your_zhipu_api_key

# DeepSeek (V4 Pro + Reasoner)
API_KEY_DS=your_deepseek_api_key

# Kimi (Kimi Thinking + K2)
API_KEY_KIMI=your_kimi_api_key

# 豆包 (Doubao 1.5 Pro + Thinking)
API_KEY_DOUBAO=your_doubao_api_key

# 通义千问 (Qwen 3-235B)
API_KEY_QWEN=your_qwen_api_key

# ModelScope (体验模型)
API_KEY_MODELSCOPE=your_modelscope_api_key

# Gemini (Gemini 2.5 Pro)
API_KEY_GEMINI=your_gemini_api_key
```

- [ ] **main.py 启动时校验环境变量**

- [ ] **提交**

```bash
git add -A && git commit -m "04重构：GitHub Actions 统一 + .env.example"
```

### 步骤 9：测试编写

**Files:**
- Create: `tests/conftest.py`, `tests/test_chat.py`, `tests/test_pipeline.py`, `tests/test_processors.py`, `tests/test_utils.py`, `tests/test_registry.py`

- [ ] **创建 tests/conftest.py** — 公共 fixture

- [ ] **创建 tests/test_chat.py**

- [ ] **创建 tests/test_pipeline.py**

- [ ] **创建 tests/test_processors.py**

- [ ] **创建 tests/test_utils.py**

- [ ] **创建 tests/test_registry.py**

- [ ] **运行全部测试**

```bash
python -m pytest tests/ -v
```

- [ ] **提交**

```bash
git add -A && git commit -m "04重构：添加单元测试"
```
