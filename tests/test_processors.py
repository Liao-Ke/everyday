from processors.format_processors import ensure_first_line_is_h1


class TestEnsureFirstLineIsH1:
    def test_adds_h1_when_missing(self):
        result = ensure_first_line_is_h1({"content": "故事内容"})
        assert result["content"].startswith("# ")

    def test_preserves_existing_h1(self):
        result = ensure_first_line_is_h1({"content": "# 标题\n正文"})
        assert result["content"] == "# 标题\n正文"

    def test_handles_empty_content(self):
        result = ensure_first_line_is_h1({"content": ""})
        assert result["content"] == ""

    def test_handles_content_with_newlines(self):
        result = ensure_first_line_is_h1({"content": "\n\n正文内容"})
        assert result["content"].startswith("# ")
