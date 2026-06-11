import pytest

from utils.misc import process_reasoning_content, remove_leading_empty_line
from utils.uuid_utils import fixed_length_uuid


class TestFixedLengthUUID:
    def test_returns_correct_length(self):
        result = fixed_length_uuid(3)
        assert len(result) == 3

    def test_returns_hex_characters(self):
        result = fixed_length_uuid(6)
        assert all(c in "0123456789abcdef" for c in result)

    def test_even_length(self):
        result = fixed_length_uuid(8)
        assert len(result) == 8

    def test_raises_on_zero_length(self):
        with pytest.raises(ValueError):
            fixed_length_uuid(0)

    def test_raises_on_negative_length(self):
        with pytest.raises(ValueError):
            fixed_length_uuid(-1)


class TestRemoveLeadingEmptyLine:
    def test_removes_leading_newline(self):
        result = remove_leading_empty_line({"content": "\n\nHello"})
        assert result["content"] == "Hello"

    def test_no_leading_newline(self):
        result = remove_leading_empty_line({"content": "Hello\nWorld"})
        assert result["content"] == "Hello\nWorld"

    def test_only_whitespace_lines(self):
        result = remove_leading_empty_line({"content": "  \n\t\nHello"})
        assert result["content"] == "Hello"


class TestProcessReasoningContent:
    def test_extracts_reasoning(self):
        result = process_reasoning_content({"content": "<think>推理内容</think>\n# 故事标题\n正文"})
        assert result["reasoning_content"] == "推理内容"
        assert result["content"] == "\n# 故事标题\n正文"

    def test_no_think_tag(self):
        result = process_reasoning_content({"content": "# 故事标题\n正文"})
        assert "reasoning_content" not in result

    def test_non_string_content(self):
        result = process_reasoning_content({"content": 123})
        assert "reasoning_content" not in result
