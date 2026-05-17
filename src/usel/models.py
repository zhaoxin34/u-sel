"""Data models for usel."""

from dataclasses import dataclass


@dataclass
class Selection:
    """Represents a single selection item."""

    title: str
    group: str
    output: str

    @property
    def display_title(self) -> str:
        """Get title to display, fallback to output if empty."""
        return self.title or self.output


@dataclass
class Config:
    """Configuration loaded from sels.yml."""

    items: list[Selection]

    def get_sorted(self) -> list["Selection"]:
        """Return items sorted by group, then title."""
        return sorted(self.items, key=lambda s: (s.group, s.title))

    @classmethod
    def from_list(cls, data: list[dict]) -> "Config":
        """Create Config from a list of dictionaries."""
        items = [
            Selection(
                title=item.get("title", ""),
                group=item.get("group", ""),
                output=item.get("output", ""),
            )
            for item in data
        ]
        return cls(items=items)
