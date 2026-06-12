# 升级 DeepSeek 模型配置至 V4 系列

## 目标

将 DeepSeek 模型配置从旧版更新至 V4 系列，移除已废弃的 Reasoner 模型，新增 Flash 模型。

## 修改范围

- `model_configs/deepseek_r1_config.py` — **删除**：旧版 DeepSeek Reasoner（deepseek-reasoner）
- `model_configs/deepseek_v4_flash_config.py` — **新增**：DeepSeek V4 Flash（deepseek-v4-flash），使用散文风格 prompt
- `model_configs/deepseek_v3_config.py` → `deepseek_v4_pro_config.py` — **重命名**：文件名与模型名 `deepseek-v4-pro` 保持一致
- `tests/test_registry.py` — 更新测试，`deepseek_v3` → `deepseek_v4_pro`
- `README.md` / `model_configs/AGENTS.md` — 更新文件列表和引用

## 核心实现

- `deepseek_v4_flash_config.py`：使用 `get_jinshan_cached()` 获取每日一句素材，散文风格 prompt
- `deepseek_v4_pro_config.py`：仅文件名变更，内容沿用已有的 `deepseek-v4-pro` 模型配置（余华小说风格 + 联网搜索增强）

## 影响范围

- 模型注册表：`deepseek_v3` 不再可用，替换为 `deepseek_v4_pro`；新增 `deepseek_v4_flash`
- `main.py` 的 EXCLUDED_MODELS 不受影响（DeepSeek 模型不在排除列表中）

## 验证方式

```bash
pytest tests/test_registry.py -v
# 应通过 test_returns_config_for_deepseek_v4_pro 等所有 registry 测试
pytest -v
# 全部 28 个测试通过
```

## 已知限制

无。
