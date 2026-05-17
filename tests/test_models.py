"""Tests for usel models."""

from usel.models import Config, Selection


def test_selection_creation():
    """Test creating a Selection object."""
    selection = Selection(
        title="Test Command",
        group="test",
        output="test-cmd",
    )
    assert selection.title == "Test Command"
    assert selection.group == "test"
    assert selection.output == "test-cmd"


def test_config_from_list():
    """Test creating Config from a list of dictionaries."""
    data = [
        {
            "title": "cmd1",
            "group": "group1",
            "output": "output1",
        },
        {
            "title": "cmd2",
            "group": "group2",
            "output": "output2",
        },
    ]
    config = Config.from_list(data)

    assert len(config.items) == 2
    assert config.items[0].title == "cmd1"
    assert config.items[1].title == "cmd2"


def test_config_from_list_with_missing_fields():
    """Test Config handles missing fields gracefully."""
    data = [
        {"title": "cmd1"},
        {"title": "cmd2", "group": "group2"},
    ]
    config = Config.from_list(data)

    assert len(config.items) == 2
    assert config.items[0].title == "cmd1"
    assert config.items[0].group == ""  # Default empty string
    assert config.items[1].group == "group2"


def test_config_from_empty_list():
    """Test Config handles empty list."""
    config = Config.from_list([])
    assert len(config.items) == 0
