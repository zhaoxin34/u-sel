"""Tests for placeholder parsing functionality."""

import pytest

from usel.app import (
    OLD_PLACEHOLDER_PATTERN,
    PLACEHOLDER_PATTERN,
    Placeholder,
    check_old_syntax,
    parse_placeholder,
    replace_placeholder,
)


class TestPlaceholderPattern:
    """Test the new placeholder regex pattern."""

    def test_g_mode_basic(self):
        """Test basic g mode: {{g|group}}"""
        match = PLACEHOLDER_PATTERN.search("docker {{g|zellij}} run")
        assert match is not None
        assert match.group("intent") == "g"
        assert match.group("prompt") is None
        assert match.group("default") == "zellij"

    def test_g_mode_with_prompt(self):
        """Test g mode with prompt: {{g:选择容器|zellij}}"""
        match = PLACEHOLDER_PATTERN.search("docker {{g:选择容器|zellij}} run")
        assert match is not None
        assert match.group("intent") == "g"
        assert match.group("prompt") == "选择容器"
        assert match.group("default") == "zellij"

    def test_i_mode_with_prompt(self):
        """Test i mode with prompt: {{i:提示语}}"""
        match = PLACEHOLDER_PATTERN.search("echo {{i:请输入端口}}")
        assert match is not None
        assert match.group("intent") == "i"
        assert match.group("prompt") == "请输入端口"
        assert match.group("default") is None

    def test_i_mode_with_default(self):
        """Test i mode with default: {{i:提示语|默认值}}"""
        match = PLACEHOLDER_PATTERN.search("echo {{i:请输入端口|8080}}")
        assert match is not None
        assert match.group("intent") == "i"
        assert match.group("prompt") == "请输入端口"
        assert match.group("default") == "8080"

    def test_multiple_placeholders(self):
        """Test multiple placeholders in one string."""
        text = "docker run -p {{i:端口|8080}} -v {{g|volumes}}:/data"
        matches = list(PLACEHOLDER_PATTERN.finditer(text))
        assert len(matches) == 2


class TestOldPlaceholderPattern:
    """Test old syntax detection."""

    def test_old_syntax_detected(self):
        """Test that old syntax {{word}} is detected."""
        match = OLD_PLACEHOLDER_PATTERN.search("echo {{old_group}}")
        assert match is not None
        assert match.group("old_word") == "old_group"

    def test_new_syntax_not_detected(self):
        """Test that new syntax is not detected as old."""
        match = OLD_PLACEHOLDER_PATTERN.search("{{g|zellij}}")
        assert match is None


class TestParsePlaceholder:
    """Test placeholder parsing function."""

    def test_parse_g_mode(self):
        """Test parsing g mode."""
        result = parse_placeholder("{{g|zellij}}")
        assert result is not None
        remaining, placeholder = result
        assert remaining == ""
        assert placeholder.intent == "g"
        assert placeholder.group_name == "zellij"

    def test_parse_g_mode_with_text(self):
        """Test parsing g mode with surrounding text."""
        result = parse_placeholder("docker run {{g|zellij}}")
        assert result is not None
        remaining, placeholder = result
        assert remaining == "docker run "
        assert placeholder.intent == "g"
        assert placeholder.group_name == "zellij"

    def test_parse_g_mode_with_prompt(self):
        """Test parsing g mode with prompt."""
        result = parse_placeholder("{{g:选择容器|zellij}}")
        assert result is not None
        remaining, placeholder = result
        assert remaining == ""
        assert placeholder.intent == "g"
        assert placeholder.group_name == "zellij"
        assert placeholder.prompt == "选择容器"

    def test_parse_i_mode(self):
        """Test parsing i mode."""
        result = parse_placeholder("{{i:请输入端口}}")
        assert result is not None
        remaining, placeholder = result
        assert remaining == ""
        assert placeholder.intent == "i"
        assert placeholder.prompt == "请输入端口"

    def test_parse_i_mode_with_default(self):
        """Test parsing i mode with default value."""
        result = parse_placeholder("{{i:请输入端口|8080}}")
        assert result is not None
        remaining, placeholder = result
        assert remaining == ""
        assert placeholder.intent == "i"
        assert placeholder.prompt == "请输入端口"
        assert placeholder.default == "8080"

    def test_no_placeholder(self):
        """Test parsing string without placeholder."""
        result = parse_placeholder("echo hello")
        assert result is None

    def test_multiple_placeholders(self):
        """Test parsing multiple placeholders sequentially."""
        # First placeholder
        result1 = parse_placeholder("{{i:端口|8080}} -v {{g|volumes}}")
        assert result1 is not None
        remaining1, placeholder1 = result1
        assert placeholder1.intent == "i"
        assert placeholder1.prompt == "端口"

        # Second placeholder
        result2 = parse_placeholder(remaining1)
        assert result2 is not None
        remaining2, placeholder2 = result2
        assert remaining2 == " -v "
        assert placeholder2.intent == "g"
        assert placeholder2.group_name == "volumes"


class TestReplacePlaceholder:
    """Test placeholder replacement function."""

    def test_replace_g_mode(self):
        """Test replacing g mode placeholder."""
        placeholder = Placeholder(intent="g", group_name="zellij")
        result = replace_placeholder("docker {{g|zellij}} run", placeholder, "pi -c")
        assert result == "docker pi -c run"

    def test_replace_g_mode_with_prompt(self):
        """Test replacing g mode placeholder with prompt."""
        placeholder = Placeholder(intent="g", prompt="选择命令", group_name="zellij")
        result = replace_placeholder("{{g:选择命令|zellij}}", placeholder, "pi -c")
        assert result == "pi -c"

    def test_replace_i_mode(self):
        """Test replacing i mode placeholder."""
        placeholder = Placeholder(intent="i", prompt="端口号")
        result = replace_placeholder("echo {{i:端口号}}", placeholder, "9000")
        assert result == "echo 9000"

    def test_replace_i_mode_with_default(self):
        """Test replacing i mode placeholder with default."""
        placeholder = Placeholder(intent="i", prompt="端口号", default="8080")
        result = replace_placeholder("{{i:端口号|8080}}", placeholder, "9000")
        assert result == "9000"


class TestCheckOldSyntax:
    """Test old syntax detection function."""

    def test_old_syntax_raises_error(self):
        """Test that old syntax raises SystemExit."""
        with pytest.raises(SystemExit):
            check_old_syntax("echo {{old_group}}")

    def test_new_syntax_no_error(self):
        """Test that new syntax does not raise error."""
        # Should not raise
        check_old_syntax("{{g|zellij}}")
        check_old_syntax("{{i:请输入}}")

    def test_valid_single_letter_no_error(self):
        """Test that {{g}} and {{i}} don't raise error (valid intents)."""
        check_old_syntax("{{g}}")
        check_old_syntax("{{i:提示语}}")
