"""Tests for fuzzy search functionality."""

from usel.app import build_highlighted_text, fuzzy_search
from usel.models import Selection


class TestBuildHighlightedText:
    """Test the build_highlighted_text function."""

    def test_empty_indices(self):
        """Test with no indices - returns original text."""
        text = "hello world"
        result = build_highlighted_text(text, [])
        assert result == "hello world"

    def test_single_char_match(self):
        """Test single character highlight."""
        text = "hello"
        result = build_highlighted_text(text, [0])  # highlight 'h'
        assert "[#FFD700]h[/#FFD700]" in result
        assert "ello" in result

    def test_multiple_chars_match(self):
        """Test multiple character highlight."""
        text = "new float pane"
        result = build_highlighted_text(text, [0, 4, 10])  # n, f, p
        assert "[#FFD700]n[/#FFD700]" in result
        assert "[#FFD700]f[/#FFD700]" in result
        assert "[#FFD700]p[/#FFD700]" in result

    def test_consecutive_chars(self):
        """Test consecutive characters highlight - each char wrapped individually."""
        text = "new"
        result = build_highlighted_text(text, [0, 1, 2])  # all chars
        # Each character is wrapped individually
        assert result == "[#FFD700]n[/#FFD700][#FFD700]e[/#FFD700][#FFD700]w[/#FFD700]"

    def test_gap_between_highlights(self):
        """Test with gaps between highlights."""
        text = "abcdef"
        result = build_highlighted_text(text, [0, 3, 5])  # a, d, f
        assert "[#FFD700]a[/#FFD700]bc[#FFD700]d[/#FFD700]e[#FFD700]f[/#FFD700]" == result


class TestFuzzySearch:
    """Test the fuzzy_search function."""

    def _make_selection(self, title: str, output: str = "output", group: str = "test") -> Selection:
        """Helper to create a Selection object."""
        return Selection(title=title, group=group, output=output)

    def test_empty_query_returns_all(self):
        """Test that empty query returns all selections."""
        selections = [
            self._make_selection("apple"),
            self._make_selection("banana"),
        ]
        results = fuzzy_search("", selections)
        assert len(results) == 2
        # Should return selections with empty indices and zero score
        assert results[0][0].display_title == "apple"
        assert results[0][1] == []  # empty indices

    def test_exact_match(self):
        """Test exact matching."""
        selections = [self._make_selection("apple")]
        results = fuzzy_search("apple", selections)
        assert len(results) == 1
        assert results[0][0].display_title == "apple"

    def test_subsequence_match(self):
        """Test fuzzy subsequence matching."""
        selections = [self._make_selection("new float pane")]
        results = fuzzy_search("nfp", selections)
        assert len(results) == 1
        assert results[0][0].display_title == "new float pane"

    def test_partial_word_match(self):
        """Test partial word matching with space."""
        selections = [self._make_selection("new float pane")]
        results = fuzzy_search("n p", selections)  # with space
        assert len(results) == 1
        assert results[0][0].display_title == "new float pane"

    def test_gap_in_subsequence(self):
        """Test matching with gaps in the subsequence."""
        # fuzzy finder matches non-contiguous subsequences
        selections = [self._make_selection("flag")]
        results = fuzzy_search("flg", selections)
        assert len(results) == 1

    def test_score_ordering(self):
        """Test results are ordered by score."""
        selections = [
            self._make_selection("renew"),
            self._make_selection("new file"),
            self._make_selection("new pane"),
        ]
        results = fuzzy_search("new", selections)
        assert len(results) == 3
        # "new pane" should score higher (exact word boundary match)
        assert results[0][0].display_title in ["new pane", "new file"]

    def test_multi_field_search_title(self):
        """Test search matches in title field."""
        selections = [
            self._make_selection("pi session", group="pi"),
        ]
        results = fuzzy_search("pi", selections)
        assert len(results) == 1
        assert results[0][0].display_title == "pi session"

    def test_multi_field_search_output(self):
        """Test search matches in output field."""
        selections = [
            self._make_selection("command", output="zellij action"),
        ]
        results = fuzzy_search("zellij", selections)
        assert len(results) == 1

    def test_no_match(self):
        """Test when no items match."""
        selections = [
            self._make_selection("apple"),
            self._make_selection("banana"),
        ]
        results = fuzzy_search("xyz", selections)
        # No results since xyz doesn't match anything
        assert len(results) == 0

    def test_best_field_wins(self):
        """Test that best matching field determines result."""
        selections = [
            self._make_selection("test", output="banana apple"),
        ]
        results = fuzzy_search("apple", selections)
        assert len(results) == 1
        # Should use output field since it has better match


class TestFuzzySearchEdgeCases:
    """Edge case tests for fuzzy search."""

    def _make_selection(self, title: str) -> Selection:
        return Selection(title=title, group="test", output="output")

    def test_empty_selections(self):
        """Test with empty selections list."""
        results = fuzzy_search("test", [])
        assert len(results) == 0

    def test_special_characters(self):
        """Test matching with special characters."""
        selections = [self._make_selection("hello-world")]
        results = fuzzy_search("hello", selections)
        assert len(results) == 1

    def test_camelcase(self):
        """Test matching camelCase words."""
        selections = [self._make_selection("newFloatPane")]
        results = fuzzy_search("nfp", selections)
        assert len(results) == 1

    def test_long_query(self):
        """Test with query longer than target."""
        selections = [self._make_selection("hi")]
        results = fuzzy_search("hello", selections)
        # No match since query is longer than target
        assert len(results) == 0
