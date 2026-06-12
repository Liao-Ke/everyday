from core.registry import ModelRegistry


class TestModelRegistry:
    def test_imports_without_error(self):
        assert ModelRegistry is not None

    def test_discover_returns_dict(self):
        configs = ModelRegistry.discover()
        assert isinstance(configs, dict)

    def test_returns_config_for_deepseek_v4_pro(self):
        configs = ModelRegistry.discover()
        assert "deepseek_v4_pro" in configs
        assert configs["deepseek_v4_pro"]["API_KEY"] is not None

    def test_returns_config_for_zhipu(self):
        configs = ModelRegistry.discover()
        assert "zhipu" in configs
        assert configs["zhipu"]["API_KEY"] is not None

    def test_each_config_has_required_symbols(self):
        configs = ModelRegistry.discover()
        for name, cfg in configs.items():
            assert "API_KEY" in cfg, f"{name} missing API_KEY"
            assert "CLIENT_PARAMS" in cfg, f"{name} missing CLIENT_PARAMS"
            assert "CHAT_PARAMS" in cfg, f"{name} missing CHAT_PARAMS"
