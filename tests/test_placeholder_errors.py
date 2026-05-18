"""Tests for error handling in placeholder functionality."""

import pytest

from usel.app import Placeholder, check_old_syntax, parse_placeholder


class TestOldSyntaxError:
    """Test error handling for old syntax."""

    def test_old_syntax_raises_error(self):
        """Test that old syntax raises SystemExit with correct message."""
        with pytest.raises(SystemExit) as exc_info:
            check_old_syntax("echo {{old_group}}")
        assert exc_info.value.code == 1

    def test_old_syntax_with_multiple_placeholders(self):
        """Test that first old syntax triggers error."""
        with pytest.raises(SystemExit):
            check_old_syntax("echo {{old}} and {{another}}")

    def test_g_intent_no_error(self):
        """Test that {{g}} single letter intent does not raise error."""
        # Should not raise
        check_old_syntax("{{g}}")

    def test_i_intent_no_error(self):
        """Test that {{i}} single letter intent does not raise error."""
        # Should not raise
        check_old_syntax("{{i:提示语}}")

    def test_valid_new_syntax_no_error(self):
        """Test that valid new syntax does not raise error."""
        # Should not raise
        check_old_syntax("{{g|zellij}}")
        check_old_syntax("{{i:请输入端口}}")
        check_old_syntax("{{i:请输入端口|8080}}")
        check_old_syntax("{{g:选择容器|zellij}}")


class TestGroupNotFoundError:
    """Test error handling for non-existent groups."""

    def test_parse_returns_none_for_no_placeholder(self):
        """Test that parse returns None when no placeholder found."""
        result = parse_placeholder("echo hello")
        assert result is None

    def test_group_name_can_be_any_string(self):
        """Test that any string can be a group name (validation happens in app)."""
        result = parse_placeholder("{{g|mygroup}}")
        assert result is not None
        remaining, placeholder = result
        assert placeholder.intent == "g"
        assert placeholder.group_name == "mygroup"


class TestEmptyInputError:
    """Test error handling for empty input in i mode."""

    def test_empty_input_validation_in_placeholder(self):
        """Test that empty input validation happens at runtime, not parse time."""
        result = parse_placeholder("{{i:请输入}}")
        assert result is not None
        _, placeholder = result
        assert placeholder.prompt == "请输入"
        assert placeholder.default is None
        # Validation of empty input happens in _confirm_input()

    def test_i_mode_with_empty_default(self):
        """Test i mode with empty default value (not allowed in syntax)."""
        # Empty default after | is not valid syntax, parse returns None
        result = parse_placeholder("{{i:请输入|}}")
        assert result is None


class TestNestingDepthLimit:
    """Test nesting depth limit handling."""

    def test_placeholder_extraction_is_depth_agnostic(self):
        """Test that parse_placeholder doesn't track depth (done in app)."""
        # Note: prompt cannot contain }} so we use simple values without spaces
        result1 = parse_placeholder("{{i:a}}{{g|b}}{{i:c}}")
        assert result1 is not None
        remaining1, p1 = result1
        assert p1.intent == "i"
        assert p1.prompt == "a"
        result2 = parse_placeholder(remaining1)
        assert result2 is not None
        remaining2, p2 = result2
        assert p2.intent == "g"
        assert p2.group_name == "b"
        result3 = parse_placeholder(remaining2)
        assert result3 is not None
        remaining3, p3 = result3
        assert p3.intent == "i"
        assert p3.prompt == "c"
        assert remaining3 == ""


class TestReplacePlaceholderError:
    """Test error handling in placeholder replacement."""

    def test_replace_with_valid_placeholder(self):
        """Test normal replacement works."""
        from usel.app import replace_placeholder

        p = Placeholder(intent="i", prompt="端口")
        result = replace_placeholder("{{i:端口}}", p, "8080")
        assert result == "8080"

    def test_replace_g_mode(self):
        """Test g mode replacement."""
        from usel.app import replace_placeholder

        p = Placeholder(intent="g", group_name="pi")
        result = replace_placeholder("cmd {{g|pi}}", p, "pi -c")
        assert result == "cmd pi -c"

    def test_replace_with_prompt(self):
        """Test replacement with prompt in placeholder."""
        from usel.app import replace_placeholder

        p = Placeholder(intent="g", prompt="选择命令", group_name="pi")
        result = replace_placeholder("{{g:选择命令|pi}}", p, "pi -c")
        assert result == "pi -c"
