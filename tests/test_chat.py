from unittest.mock import MagicMock, patch

from core.chat import chat_ai


class TestChatAI:
    def test_returns_none_on_api_error(self):
        with patch("core.chat.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = Exception("API error")
            mock_openai.return_value = mock_client

            result = chat_ai(
                api_key="test",
                client_params={},
                chat_params={"model": "test", "messages": []},
                max_retries=0,
            )
            assert result is None

    def test_does_not_retry_when_retry_false(self):
        with patch("core.chat.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = Exception("API error")
            mock_openai.return_value = mock_client

            result = chat_ai(
                api_key="test",
                client_params={},
                chat_params={"model": "test", "messages": [], "RETRY": False},
                max_retries=3,
            )
            assert result is None

    def test_returns_response_content(self):
        mock_choice = MagicMock()
        mock_choice.message.model_dump.return_value = {"content": "# 故事标题\n正文内容"}
        mock_choice.message.content = "# 故事标题\n正文内容"

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        with patch("core.chat.OpenAI") as mock_openai, patch("core.chat.save_chat_metadata"):
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            result = chat_ai(
                api_key="test",
                client_params={},
                chat_params={"model": "test", "messages": []},
                max_retries=0,
            )
            assert result is not None
            assert result["content"] == "# 故事标题\n正文内容"
