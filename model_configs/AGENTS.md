# model_configs — AI Model Plugin System

## OVERVIEW
Plugin-based AI model configuration. Each provider gets one `.py` file exposing a standardized 6-symbol contract. `main.py` discovers and loads them dynamically via `importlib`. No registry — just create a file matching the naming convention.

## STRUCTURE
```
model_configs/
├── __init__.py                # ACTIVE: loads .env, fetches Jinshan, web search → exports JINSHAN, SEARCH_RESULT
├── deepseek_v4_pro_config.py    # DeepSeek V4 Pro (余华 style)
├── deepseek_v4_flash_config.py  # DeepSeek V4 Flash
├── zhipu_config.py            # Zhipu GLM-4.7 Flash
├── zhipu_4_5_flash_config.py  # Zhipu GLM-4.5 Flash
├── zhipu_z1_flash_config.py   # Zhipu GLM-Z1 Flash (reasoning)
├── doubao_config.py           # Doubao 1.5 Pro
├── doubao_think_config.py     # Doubao thinking model (stdout output)
├── qwen_config.py             # Qwen 3-235B thinking
├── kimi_config.py             # Kimi thinking (刘慈欣 style, token estimation)
├── kimi_k2_config.py          # Kimi K2 (genre-blending)
├── experience_modelscope_config.py  # ModelScope (random model selection)
└── gemini_config.py           # Gemini 2.5 Pro (via zetatechs proxy)
```

## 6-Symbol Contract

Every config module MUST export these 6 symbols:

| Symbol | Type | Required | Purpose |
|--------|------|----------|---------|
| `API_KEY` | `str \| None` | Yes | `os.getenv("API_KEY_XXX")` |
| `CLIENT_PARAMS` | `dict` | Yes | OpenAI client kwargs: `{"base_url": "..."}` |
| `CHAT_PARAMS` | `dict` | Yes | Chat completion kwargs: `model`, `messages`, optional `stream`, `temperature`, `max_tokens`, `extra_body` |
| `PREPROCESSORS` | `list[Callable]` | No | Functions: `params → params` before API call |
| `POSTPROCESSORS` | `list[Callable]` | No | Functions: `response_dict → response_dict` after API call |
| `POSTPROCESSOR_FILES` | `list[Callable]` | No | Functions: `(response_dict, model_name) → None` to persist output |

## HOW TO ADD A NEW MODEL

1. **Create** `model_configs/{name}_config.py` with all 6 symbols
2. **Add** `from model_configs import JINSHAN, SEARCH_RESULT` (use these for prompt building)
3. **Register** in `main.py:config_map`: `"display-name": load_model_config("{name}")`
4. **Set API key** in `.env` and GitHub Secrets

**Minimal config:**
```python
import os
from model_configs import JINSHAN
from processors.file_processors import save_to_md_file
from processors.format_processors import ensure_first_line_is_h1

API_KEY = os.getenv("API_KEY_NEW")
CLIENT_PARAMS = {"base_url": "https://api.example.com"}
CHAT_PARAMS = {
    "model": "model-id",
    "messages": [
        {"role": "system", "content": "你是故事创作者"},
        {"role": "user", "content": f'创作一篇小说来解读"{JINSHAN["note"]}"'}
    ]
}
PREPROCESSORS = []
POSTPROCESSORS = [ensure_first_line_is_h1]
POSTPROCESSOR_FILES = [save_to_md_file]
```

## SHARED STATE: JINSHAN & SEARCH_RESULT

`from model_configs import JINSHAN, SEARCH_RESULT` provides:
- `JINSHAN: dict` — `{"note": "daily quote text", "fenxiang_img": "image URL"}` fetched once at import time
- `SEARCH_RESULT: dict` — Zhipu web search results for the daily quote (use `json.dumps()` to inject into prompts)

Not all configs import `SEARCH_RESULT`. Only those needing web context:
deepseek_v4_pro, deepseek_v4_flash, qwen, gemini, zhipu_4_5_flash, zhipu_z1_flash, experience_modelscope.

## PREPROCESSOR / POSTPROCESSOR

**Standard combinations:**

| Pattern | PREPROCESSORS | POSTPROCESSORS | POSTPROCESSOR_FILES |
|---------|:---:|:---:|:---:|
| Simple story | `[]` | `[ensure_first_line_is_h1]` | `[save_to_md_file]` |
| Token-aware (Kimi) | `[estimate_tokens]` | `[ensure_first_line_is_h1]` | `[save_to_md_file]` |
| Reasoning chain | `[]` | `[process_reasoning_content, ensure_first_line_is_h1]` | `[save_to_md_file]` |
| Image + formatting | `[]` | `[ensure_first_line_is_h1, insert_content_in_fourth_line, process_string]` | `[save_to_md_file]` |
| Stdout-only (debug) | `[]` | `[ensure_first_line_is_h1]` | `[lambda r,n: print(n, r["content"])]` |

**Available preprocessor functions:**
- `preprocessor.params_preprocessor.estimate_tokens` — adjusts `max_tokens` based on estimated prompt length (Kimi only)

**Available postprocessor functions:**
- `processors.format_processors.ensure_first_line_is_h1` — enforces H1 heading
- `processors.format_processors.insert_content_in_fourth_line` — injects Jinshan image at line 4
- `processors.format_processors.process_string` — strips code fences ` ``` `
- `processors.format_processors.format_story` — wraps with separator lines
- `utils.mish_mash.process_reasoning_content` — extracts `<think>` tags into `reasoning_content`
- `utils.mish_mash.remove_leading_empty_line` — trims leading blank lines

**Available file processor:**
- `processors.file_processors.save_to_md_file` — main file output

## ANTI-PATTERNS (THIS DIR)

- **Don't hardcode API keys** — use `os.getenv()` only
- **Don't mutate `CHAT_PARAMS` at import time** — it's shared across threads
- **Don't use lambdas for complex postprocessors** — named functions are testable
- **Don't skip `ensure_first_line_is_h1`** — needed for VitePress sidebar title parsing
- **Don't forget to add to `config_map` in main.py** after creating a config file
