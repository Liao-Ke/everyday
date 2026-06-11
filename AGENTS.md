# PROJECT KNOWLEDGE BASE

**Generated:** 2026-05-03
**Commit:** d673984
**Branch:** ai-refactor

## OVERVIEW
AI-powered daily story generator. Fetches 金山词霸 daily quote, enriches via web search, dispatches to 7+ AI models in parallel (ThreadPoolExecutor), saves stories as date-nested markdown. Frontend is VitePress static site deployed on Cloudflare Pages.

**Stack:** Python 3.11 (openai, jieba, wordcloud, ruamel.yaml) + TypeScript/Vue 3 (VitePress)

## STRUCTURE
```
everyday/
├── main.py                     # Entry: multi-threaded story generator
├── main.old.py                 # Legacy monolith (925 lines), not used
├── wordcloud_analysis.py       # Weekly word cloud + frequency report
├── check.py                    # Log file threshold archiver
├── requirements.txt            # 7 Python deps
├── package.json                # VitePress + plugins
├── .env                        # 7 API keys (gitignored)
├── stopwords_full.txt          # 2992 Chinese/English stopwords
├── config/
│   └── logger_setup.py         # Logger '每日故事', file+console
├── model_configs/              # Plugin-based AI model configs (13 files)
│   ├── __init__.py             # ACTIVE init: loads .env, fetches Jinshan, web search
│   └── *_config.py             # Per-model: API_KEY + CLIENT_PARAMS + CHAT_PARAMS + pipelines
├── preprocessor/
│   └── params_preprocessor.py  # Token estimation (Kimi only)
├── processors/
│   ├── file_processors.py      # save_to_md_file + index.md frontmatter update
│   └── format_processors.py    # H1 enforcement, image injection, code fence stripping
├── utils/
│   ├── mish_mash.py            # Heavy utility hub: download, YAML edit, UUID, web_search
│   └── metadata_utils.py       # Chat log persistence (append-only JSON + corruption recovery)
├── story/                      # VitePress site root + generated content
│   ├── 故事/                   # Stories: {年}年/{月}月/{日}日/{Weekday_HH-MM-SS}.{uuid3}.md
│   ├── 词云/                   # Weekly word cloud reports (59 markdown files)
│   ├── images/                 # 474 story JPGs + 59 word cloud PNGs
│   └── .vitepress/             # VitePress config, custom theme, Vue components
├── chat_logs/
│   └── story_records.json      # Append-only JSON array of all API calls
└── .github/workflows/
    ├── main.yml                # Daily cron: python main.py (UTC 23:00)
    ├── wordcloud-analysis.yml  # Weekly cron: python wordcloud_analysis.py (Wed)
    └── deploy.yml              # Disabled: SSH deploy of VitePress build
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add a new AI model | `model_configs/new_config.py` + `main.py:config_map` | See model_configs/AGENTS.md for the 6-symbol contract |
| Change story formatting | `processors/format_processors.py` | POSTPROCESSORS pipeline |
| Change file output path/naming | `processors/file_processors.py:save_to_md_file()` | Date-based directory + UUID filename |
| Debug API calls | `chat_logs/story_records.json` | Full request/response/timing per call |
| Adjust retry logic | `main.py:chat_ai()` | Exponential backoff, max_retries=5 |
| Modify VitePress site | `story/.vitepress/config.mts` | Sidebar, search, SEO, compression |
| Add Vue component | `story/.vitepress/components/` | ReasoningChainRenderer, WordCount |
| Rotate API keys | `.env` + GitHub Secrets | 7 providers |
| Archive oversized logs | `python check.py` | Moves story_records.json when >4.78MB |

## CODE MAP

### Entry Points
| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `__name__ == '__main__'` | entry | main.py:285 | Primary: loads configs, runs multi-threaded generation |
| `__name__ == '__main__'` | entry | wordcloud_analysis.py:182 | Weekly: jieba tokenization → word cloud → report |
| `__name__ == '__main__'` | entry | check.py:78 | Utility: archive oversized log files |
| `model_configs.__init__` | init | model_configs/__init__.py | Runs at import: loads .env, fetches Jinshan, web_search |

### Core Pipeline Functions
| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `chat_ai()` | func | main.py:21 | OpenAI-compatible API call with exponential backoff retry |
| `load_model_config()` | func | main.py:136 | Dynamic import of model_configs/{name}_config.py via importlib |
| `story_generator()` | func | main.py:178 | Per-model thread: PREPROCESSORS → chat_ai → POSTPROCESSORS → files |
| `run_multi_thread()` | func | main.py:239 | ThreadPoolExecutor, max_workers=min(32, cpu*4) |
| `save_to_md_file()` | func | processors/file_processors.py:20 | Date-nested file save + frontmatter update (zhipu only) |
| `ensure_first_line_is_h1()` | func | processors/format_processors.py:10 | Forces markdown H1 |
| `get_jinshan()` | func | utils/mish_mash.py:119 | Fetches daily quote from open.iciba.com |
| `web_search()` | func | utils/mish_mash.py:182 | Zhipu Web Search API for context enrichment |
| `modify_frontmatter()` | func | utils/mish_mash.py:48 | YAML frontmatter editor via ruamel.yaml |

### Key Module-Level Constants
| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `JINSHAN` | dict | model_configs/__init__.py | Daily quote: {note, fenxiang_img}, computed at import |
| `SEARCH_RESULT` | dict | model_configs/__init__.py | Web search context for quote, computed at import |
| `config_map` | dict | main.py:272 | Maps model name → loaded config dict |

## CONVENTIONS

### Import Order
stdlib → third-party → local. Absolute imports only. No blank lines between groups.

### Naming
- Files/functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- No classes anywhere — purely functional style

### Type Hints
Python 3.10+ union syntax (`dict | None`). Google-style docstrings with `Args:`/`Returns:`. Used in main.py, metadata_utils.py, check.py. Not in processors, preprocessor, or model configs.

### Error Handling
Always catch-and-return-None in `chat_ai()`. Exponential backoff: `initial_backoff * 2^retries`, capped at `max_backoff`. RateLimitError gets 2x wait + checks `e.retry_after`. Thread errors collected via `future.result()` + `traceback.format_exc()`.

### Logging
Logger name: `'每日故事'`. Acquire via `logging.getLogger('每日故事')` in submodules. Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`. Levels: info (flow), warning (recoverable), error (failure), critical (unexpected, with exc_info=True).

### File I/O
Atomic writes: write to `.tmp` → `os.replace(temp, target)`. JSON: read-array → append → rewrite-all. Corrupted JSON: rename to `.corrupted_<timestamp>`, start fresh.

### Strings
f-strings exclusively. Chinese primary for comments, docstrings, log messages.

## ANTI-PATTERNS (THIS PROJECT)

### NEVER
- **Commit `.env`** — contains live API keys. Already in `.gitignore`, keep it that way.
- **Use classes** — project is functional. No OOP patterns.
- **Use relative imports** — always absolute.
- **Let exceptions propagate through threads** — always catch in thread target, return None.
- **Edit `main.old.py`** — dead code, kept for history only.
- **Hardcode model names** — use config_map keys only.

### AVOID
- Lambda functions in POSTPROCESSORS/POSTPROCESSOR_FILES — use named functions for readability
- `chat_params.pop("RETRY")` mutates caller's dict — copy first if needed
- `random.shuffle(models_to_use)` makes runs non-deterministic — remove for reproducibility

### Known Issues
- No test infrastructure (no pytest, no test files)
- No linter/formatter (no ruff, black, mypy)
- `.env` on disk has API keys (gitignored but present locally)
- `deploy.yml` disabled via `if: false` — either re-enable or remove

## UNIQUE STYLES

### 1. Active `model_configs/__init__.py`
Not empty — performs initialization: loads `.env`, fetches Jinshan daily quote via HTTP, runs Zhipu web search. Exports `JINSHAN` and `SEARCH_RESULT` as module-level constants consumed by all config modules. One-time computation at import time.

### 2. Preprocessor/Postprocessor Pipeline
Each model config defines three lists of callables:
- `PREPROCESSORS` — transform `params` dict before API call
- `POSTPROCESSORS` — transform response dict after API call
- `POSTPROCESSOR_FILES` — persist response to filesystem

Orchestrated by `story_generator()` in main.py. Both named functions and inline lambdas supported.

### 3. Dynamic Model Config Loading
Models loaded via `importlib.import_module(f"model_configs.{name}_config")`. Each config file exports 6 standardized symbols: `API_KEY`, `CLIENT_PARAMS`, `CHAT_PARAMS`, `PREPROCESSORS`, `POSTPROCESSORS`, `POSTPROCESSOR_FILES`. No registry — discovery is filesystem-based.

### 4. Self-Modifying Frontmatter
After story generation, `save_to_md_file()` calls `modify_frontmatter()` to update `story/index.md`'s hero action link to the latest story. The doc site homepage auto-updates.

### 5. Dual-Format Story Files
Stories saved with optional `<ReasoningChainRenderer>` wrapper around AI's chain-of-thought reasoning, followed by the story body. Frontend Vue component renders this as collapsible section.

## COMMANDS
```bash
# Python (使用 conda 虚拟环境，activate 可能需要执行两次)
conda activate  && conda activate    # 激活虚拟环境
pip install -r requirements.txt                        # Install deps
python main.py                                          # Generate stories (needs .env keys)
python wordcloud_analysis.py                            # Generate word cloud + report
python check.py                                         # Archive oversized chat logs

# Frontend (VitePress)
npm install                         # Install Node deps
npm run docs:dev                    # Dev server → http://localhost:5173
npm run docs:build                  # Production build → story/.vitepress/dist/
npm run docs:preview                # Preview production build
```

## NOTES
- GitHub Actions run daily (23:00 UTC) and weekly (Wed 00:00 UTC) with timezone Asia/Shanghai.
- All 7 API keys must be set in both `.env` (local) and GitHub Secrets (CI).
- `story/index.md` hero link auto-updated by `save_to_md_file()` only for `model_name == "zhipu"`.
- `chat_logs/story_records.json` grows unboundedly — `check.py` monitors and archives at 4.78MB.
- Cloudflare Pages deployment is configured separately (not via the disabled `deploy.yml`).
- See `model_configs/AGENTS.md` for the config file contract and how to add new models.
