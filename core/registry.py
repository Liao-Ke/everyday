import importlib
import logging
import pkgutil

import model_configs

REQUIRED_SYMBOLS = ["API_KEY", "CLIENT_PARAMS", "CHAT_PARAMS", "PREPROCESSORS", "POSTPROCESSORS", "POSTPROCESSOR_FILES"]


class ModelRegistry:
    _configs: dict[str, dict] = {}

    @classmethod
    def discover(cls) -> dict[str, dict]:
        if cls._configs:
            return cls._configs
        logger = logging.getLogger("每日故事")
        for _imp, modname, _ispkg in pkgutil.iter_modules(model_configs.__path__):
            if modname.startswith("_") or not modname.endswith("_config"):
                continue
            try:
                mod = importlib.import_module(f"model_configs.{modname}")
                config = {}
                for sym in REQUIRED_SYMBOLS:
                    config[sym] = getattr(mod, sym, None)
                config["name"] = modname.removesuffix("_config")
                api_key = config.get("API_KEY")
                if api_key:
                    cls._configs[config["name"]] = config
            except Exception as e:
                logger.warning(f"加载模型配置 {modname} 失败: {e}")
        return cls._configs

    @classmethod
    def get(cls, name: str) -> dict | None:
        return cls._configs.get(name)

    @classmethod
    def names(cls) -> list[str]:
        return list(cls._configs.keys())
