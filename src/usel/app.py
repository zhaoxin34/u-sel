"""TUI application for usel using textual."""

import re
import sys
from typing import Literal

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.events import Key
from textual.widgets import Input, Static

from .models import Selection

# 正则匹配 {{group_name}}
PLACEHOLDER_PATTERN = re.compile(r"\{\{(\w+)\}\}")
MAX_DEPTH = 3


def extract_group(output: str) -> str | None:
    """从 output 中提取第一个占位符的 group name。"""
    match = PLACEHOLDER_PATTERN.search(output)
    return match.group(1) if match else None


def replace_placeholder(output: str, group: str, value: str) -> str:
    """替换 output 中第一个匹配的 {{group}} 为 value。"""
    return output.replace(f"{{{{{group}}}}}", value, 1)


class ItemWidget(Static):
    """Wrapper for selection items to track selection state."""

    def __init__(self, selection: Selection, index: int, selected: bool = False) -> None:
        num = index + 1
        content = f"[dim #888888]{num:>3}. [/dim #888888][#C4E88D]{selection.display_title}[/#C4E88D]  [dim #FE747E]`{selection.output}`[/dim #FE747E]  [dim #4FD6BE]({selection.group})[/dim #4FD6BE]"
        super().__init__(content, markup=True)
        self.selection = selection
        self.index = index
        self.is_selected = selected
        if self.is_selected:
            self.add_class("selected-item")


class USelApp(App):
    """Search and select TUI application."""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]

    CSS = """
    Screen {
        background: $surface;
    }

    #search-input {
        width: 100%;
        border: none;
        background: $panel;
        padding: 1 2;
    }

    #results {
        height: 1fr;
    }

    ItemWidget {
        height: auto;
        padding: 0 1;
    }

    .selected-item {
        background: $primary;
        color: $text;
    }

    #hint {
        height: auto;
        background: $panel-darken-1;
        color: $text-muted;
    }

    .nesting-hint {
        height: auto;
        padding: 1 2;
        color: $warning;
    }
    """

    def __init__(self, selections: list[Selection]) -> None:
        super().__init__()
        self._sorted_selections = sorted(selections, key=lambda s: (s.group, s.title))
        self._current_index: int = 0

        # 嵌套模板状态
        self._mode: Literal["normal", "resolving"] = "normal"
        self._current_output: str = ""
        self._current_group: str | None = None
        self._depth: int = 0

        # 当前显示的选项（可能过滤过）
        self._display_selections: list[Selection] = []

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search...", id="search-input")
        yield VerticalScroll(id="results")
        yield Static("↵ confirm  q quit", id="hint")

    def on_mount(self) -> None:
        """Initialize the app."""
        input_widget = self.query_one("#search-input", Input)
        input_widget.focus()
        self._mode = "normal"
        self._display_selections = list(self._sorted_selections)
        self._do_search("")

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        self._current_index = 0
        self._do_search(event.value)

    def _do_search(self, query: str) -> None:
        """Perform search and update display."""
        # 数字快捷方式：输入纯数字直接跳转到对应项
        if query.isdigit():
            index = int(query) - 1
            self._current_index = max(0, min(index, len(self._display_selections) - 1))
            # 更新高亮
            results = self.query_one("#results", VerticalScroll)
            items = [w for w in results.children if isinstance(w, ItemWidget)]
            for i, widget in enumerate(items):
                if i == self._current_index:
                    widget.add_class("selected-item")
                else:
                    widget.remove_class("selected-item")
            return

        query_lower = query.lower()

        # 根据模式选择基础数据
        if self._mode == "normal":
            base_selections = self._sorted_selections
        else:  # resolving
            base_selections = self._get_group_selections(self._current_group)

        # 过滤（使用 display_title 包含序号）
        if query_lower:
            filtered = [
                s
                for s in base_selections
                if query_lower in s.display_title.lower()
                or query_lower in s.output.lower()
                or query_lower in s.group.lower()
            ]
        else:
            filtered = base_selections

        self._display_selections = filtered
        self._current_index = min(self._current_index, max(0, len(filtered) - 1))

        results = self.query_one("#results", VerticalScroll)
        results.remove_children()

        # 添加嵌套提示（如果正在嵌套）
        if self._mode == "resolving" and self._current_group:
            hint_text = f"正在解析 {{{{{self._current_group}}}}}... (第 {self._depth} 层)"
            results.mount(Static(hint_text, classes="nesting-hint"))

        for i, selection in enumerate(filtered):
            item = ItemWidget(selection, i, selected=(i == self._current_index))
            results.mount(item)

    def _get_group_selections(self, group: str | None) -> list[Selection]:
        """获取指定 group 的选项。"""
        if not group:
            return []
        return [s for s in self._sorted_selections if s.group == group]

    def _check_and_continue(self) -> bool:
        """检查 output 是否还有占位符，如有则进入嵌套模式。返回 False 表示已完成。"""
        group = extract_group(self._current_output)
        if not group:
            return False  # 无占位符，输出完成

        # 检查深度
        if self._depth >= MAX_DEPTH:
            print("错误：嵌套层数超过限制（3层）", file=sys.stderr)
            sys.exit(1)

        # 检查 group 是否存在
        group_selections = self._get_group_selections(group)
        if not group_selections:
            print(f"错误：Group '{group}' 不存在或为空", file=sys.stderr)
            sys.exit(1)

        # 进入嵌套模式
        self._mode = "resolving"
        self._current_group = group
        self._depth += 1
        self._display_selections = group_selections
        self._current_index = 0
        self._do_search("")
        return True

    def on_key(self, event: Key) -> None:
        """Handle key events globally."""
        if event.key == "up":
            self._move_selection(-1)
        elif event.key == "down":
            self._move_selection(1)
        elif event.key == "enter":
            self._confirm_selection()

    def _move_selection(self, direction: int) -> None:
        """Move selection by direction."""
        results = self.query_one("#results", VerticalScroll)
        items = [w for w in results.children if isinstance(w, ItemWidget)]
        if not items:
            return

        # Update index
        self._current_index = max(0, min(len(items) - 1, self._current_index + direction))

        # Update display
        for i, widget in enumerate(items):
            if i == self._current_index:
                widget.add_class("selected-item")
                widget.is_selected = True
            else:
                widget.remove_class("selected-item")
                widget.is_selected = False

    def _confirm_selection(self) -> None:
        """Confirm selection and exit."""
        results = self.query_one("#results", VerticalScroll)
        items = [w for w in results.children if isinstance(w, ItemWidget)]
        if not items or self._current_index >= len(items):
            return

        selected = items[self._current_index].selection

        if self._mode == "normal":
            # 正常模式：设置 output，开始检查
            self._current_output = selected.output
            if not self._check_and_continue():
                # 无占位符，直接输出
                self.exit(result=self._current_output)
        else:  # resolving
            # 嵌套模式：用选中值替换占位符，继续检查
            if self._current_group is None:
                print("错误：内部状态错误", file=sys.stderr)
                sys.exit(1)
            self._current_output = replace_placeholder(
                self._current_output, self._current_group, selected.output
            )
            self._mode = "normal"
            self._current_group = None
            # 继续检查是否有更多占位符
            if not self._check_and_continue():
                self.exit(result=self._current_output)


def run_app(selections: list[Selection]) -> str | None:
    """Run the TUI app and return selected command."""
    app = USelApp(selections)
    return app.run()
