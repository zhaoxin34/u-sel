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
        """Get title to display, with index number prefix for search."""
        base = self.title or self.output
        # 序号在 ItemWidget 中添加，这里返回原始 title
        # 让序号参与搜索：把序号作为 title 的一部分
        return base


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
