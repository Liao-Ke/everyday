from unittest.mock import MagicMock

from core.pipeline import run_model


class TestRunModel:
    def test_returns_response_on_success(self, sample_config):
        mock_chat = MagicMock(return_value={"content": "# 故事\n正文"})
        result = run_model(sample_config, chat_fn=mock_chat)
        assert result is not None
        assert result["content"] == "# 故事\n正文"

    def test_returns_none_when_chat_fails(self, sample_config):
        mock_chat = MagicMock(return_value=None)
        result = run_model(sample_config, chat_fn=mock_chat)
        assert result is None

    def test_runs_preprocessors(self, sample_config):
        preprocessors_run = []

        def pre1(params):
            preprocessors_run.append("pre1")
            return params

        config = {**sample_config, "PREPROCESSORS": [pre1]}
        mock_chat = MagicMock(return_value={"content": "# 故事\n正文"})
        run_model(config, chat_fn=mock_chat)
        assert "pre1" in preprocessors_run

    def test_runs_postprocessors(self, sample_config, sample_response):
        postprocessors_run = []

        def post1(r):
            postprocessors_run.append("post1")
            return r

        config = {**sample_config, "POSTPROCESSORS": [post1]}
        mock_chat = MagicMock(return_value=sample_response)
        run_model(config, chat_fn=mock_chat)
        assert "post1" in postprocessors_run

    def test_runs_file_processors(self, sample_config, sample_response):
        file_processors_run = []

        def file_fn(_r, _cfg):
            file_processors_run.append("file")

        config = {**sample_config, "POSTPROCESSOR_FILES": [file_fn]}
        mock_chat = MagicMock(return_value=sample_response)
        run_model(config, chat_fn=mock_chat)
        assert "file" in file_processors_run
