"""TUI application for usel using textual."""

import re
import sys
from dataclasses import dataclass
from typing import Literal

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.events import Key
from textual.widgets import Input, Static

from .models import Selection

# 新语法: {{意图[:提示语][|默认值]}}
# 示例: {{g|zellij}}, {{i:请输入端口|8080}}, {{g:选择容器|zellij}}
PLACEHOLDER_PATTERN = re.compile(
    r"\{\{(?P<intent>g|i)"
    r"(?::(?P<prompt>[^}|]+))?"
    r"(?:\|(?P<default>[^}]+))?"
    r"\}\}"
)

# 旧语法检测: {{word}} where word is not g or i
OLD_PLACEHOLDER_PATTERN = re.compile(r"\{\{(?P<old_word>\w+)\}\}")

MAX_DEPTH = 3


@dataclass
class Placeholder:
    """占位符解析结果。"""

    intent: str  # "g" or "i"
    prompt: str | None = None  # 提示语，可选
    default: str | None = None  # 默认值，用于 i 模式
    group_name: str | None = None  # g 模式的 group name


def check_old_syntax(output: str) -> None:
    """检查是否使用了旧语法，如果是则报错并提示迁移。"""
    for match in OLD_PLACEHOLDER_PATTERN.finditer(output):
        word = match.group("old_word")
        if word not in ("g", "i"):
            print(
                f"错误：检测到旧语法 '{{{{word}}}}'，请迁移到新语法 '{{{{g|{word}}}}}' 或 '{{{{i:提示语}}}}'",
                file=sys.stderr,
            )
            sys.exit(1)


def parse_placeholder(output: str) -> tuple[str, Placeholder] | None:
    """从 output 中提取第一个占位符，返回 (remaining, Placeholder) 或 None。"""
    match = PLACEHOLDER_PATTERN.search(output)
    if not match:
        return None

    intent = match.group("intent")
    prompt = match.group("prompt")
    default = match.group("default")

    placeholder = Placeholder(intent=intent)

    if intent == "g":
        # g 模式: {{g|group_name}} 或 {{g:提示语|group_name}}
        # 对于 g 模式，group_name 在 | 后面（default）
        # 提示语在 : 后面（prompt）
        placeholder.group_name = default  # group_name 来自 | 后面的值
        placeholder.prompt = prompt  # 提示语来自 : 后面的值（可选）
        placeholder.default = None
    else:
        # i 模式: {{i:提示语}} 或 {{i:提示语|默认值}}
        # 对于 i 模式，prompt 是提示语，default 是默认值
        placeholder.prompt = prompt
        placeholder.default = default
        placeholder.group_name = None

    remaining = output[: match.start()] + output[match.end() :]
    return remaining, placeholder


def replace_placeholder(output: str, placeholder: Placeholder, value: str) -> str:
    """替换 output 中第一个匹配的占位符为 value。"""
    # 构建占位符字符串进行替换
    if placeholder.intent == "g":
        if placeholder.prompt:
            ph = f"{{{{{placeholder.intent}:{placeholder.prompt}|{placeholder.group_name}}}}}"
        else:
            ph = f"{{{{{placeholder.intent}|{placeholder.group_name}}}}}"
    else:
        if placeholder.default:
            ph = f"{{{{{placeholder.intent}:{placeholder.prompt}|{placeholder.default}}}}}"
        else:
            ph = f"{{{{{placeholder.intent}:{placeholder.prompt}}}}}"
    return output.replace(ph, value, 1)


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

    Input {
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

    #prompt-area {
        height: auto;
        padding: 1 2;
        background: $panel;
        color: $text;
    }
    """

    def __init__(self, selections: list[Selection]) -> None:
        super().__init__()
        self._sorted_selections = sorted(selections, key=lambda s: (s.group, s.title))
        self._current_index: int = 0

        # 状态: searching=搜索模式, resolving_g=g模式, resolving_i=i模式
        self._mode: Literal["searching", "resolving_g", "resolving_i"] = "searching"
        self._current_output: str = ""
        self._current_placeholder: Placeholder | None = None  # 当前正在解析的占位符
        self._full_output: str = ""  # 完整的 output（包含占位符）
        self._depth: int = 0

        # 当前显示的选项（可能过滤过）
        self._display_selections: list[Selection] = []

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search...", id="search-input")
        yield Static("", id="prompt-area")
        yield Input(placeholder="", id="resolve-input")
        yield VerticalScroll(id="results")
        yield Static("↵ confirm  q quit", id="hint")

    def on_mount(self) -> None:
        """Initialize the app."""
        input_widget = self.query_one("#search-input", Input)
        input_widget.focus()
        self._mode = "searching"
        self._display_selections = list(self._sorted_selections)
        self._hide_resolve_ui()
        self._do_search("")

    def _hide_resolve_ui(self) -> None:
        """隐藏 resolve 模式的 UI 元素。"""
        prompt_area = self.query_one("#prompt-area", Static)
        prompt_area.update("")
        resolve_input = self.query_one("#resolve-input", Input)
        resolve_input.value = ""
        resolve_input.display = False
        search_input = self.query_one("#search-input", Input)
        search_input.display = True

    def _show_g_mode(self, prompt: str) -> None:
        """显示 g 模式的 UI。"""
        hint_text = f"{prompt} | {self._full_output}"
        prompt_area = self.query_one("#prompt-area", Static)
        prompt_area.update(f"[dim #FFC107]{hint_text}[/dim #FFC107]")
        resolve_input = self.query_one("#resolve-input", Input)
        resolve_input.display = False
        search_input = self.query_one("#search-input", Input)
        search_input.display = False

    def _show_i_mode(self, prompt: str, default: str | None) -> None:
        """显示 i 模式的 UI。"""
        hint_text = f"{prompt} | {self._full_output}"
        prompt_area = self.query_one("#prompt-area", Static)
        prompt_area.update(f"[dim #FFC107]{hint_text}[/dim #FFC107]")
        resolve_input = self.query_one("#resolve-input", Input)
        resolve_input.value = default or ""
        resolve_input.display = True
        resolve_input.focus()
        search_input = self.query_one("#search-input", Input)
        search_input.display = False

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if self._mode != "searching":
            return  # resolve 模式下忽略搜索
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
        if self._mode == "searching":
            base_selections = self._sorted_selections
        else:  # resolving_g or resolving_i
            if self._current_placeholder and self._current_placeholder.group_name:
                base_selections = self._get_group_selections(self._current_placeholder.group_name)
            else:
                base_selections = []

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

        for i, selection in enumerate(filtered):
            item = ItemWidget(selection, i, selected=(i == self._current_index))
            results.mount(item)

    def _get_group_selections(self, group: str | None) -> list[Selection]:
        """获取指定 group 的选项。"""
        if not group:
            return []
        return [s for s in self._sorted_selections if s.group == group]

    def _check_and_continue(self) -> bool:
        """检查 output 是否还有占位符，如有则进入对应的 resolve 模式。返回 False 表示已完成。"""
        # 检查旧语法
        check_old_syntax(self._current_output)

        result = parse_placeholder(self._current_output)
        if not result:
            return False  # 无占位符，输出完成

        remaining, placeholder = result
        # 保留完整的 output 用于替换
        self._full_output = self._current_output
        self._current_output = remaining
        self._current_placeholder = placeholder

        # 检查深度
        if self._depth >= MAX_DEPTH:
            print("错误：嵌套层数超过限制（3层）", file=sys.stderr)
            sys.exit(1)

        self._depth += 1

        if placeholder.intent == "g":
            # g 模式：从 group 选择
            group_name = placeholder.group_name
            if not group_name:
                print("错误：g 模式缺少 group name", file=sys.stderr)
                sys.exit(1)

            group_selections = self._get_group_selections(group_name)
            if not group_selections:
                print(f"错误：Group '{group_name}' 不存在或为空", file=sys.stderr)
                sys.exit(1)

            # 进入 g 模式
            self._mode = "resolving_g"
            self._display_selections = group_selections
            self._current_index = 0
            self._hide_resolve_ui()
            prompt = placeholder.prompt if placeholder.prompt else "请选择"
            self._show_g_mode(prompt)
            self._do_search("")
            return True

        else:  # i 模式
            # i 模式：手动输入
            self._mode = "resolving_i"
            self._display_selections = []
            self._current_index = 0
            prompt = placeholder.prompt or "请输入"
            self._show_i_mode(prompt, placeholder.default)
            self._do_search("")
            return True

    def on_key(self, event: Key) -> None:
        """Handle key events globally."""
        if self._mode == "resolving_i":
            # i 模式下只有回车有效
            if event.key == "enter":
                self._confirm_input()
            return

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
        """Confirm selection from group list."""
        results = self.query_one("#results", VerticalScroll)
        items = [w for w in results.children if isinstance(w, ItemWidget)]
        if not items or self._current_index >= len(items):
            return

        selected = items[self._current_index].selection

        # 清空输入框
        input_widget = self.query_one("#search-input", Input)
        input_widget.value = ""

        if self._mode == "searching":
            # 正常模式：设置 output，开始检查
            self._current_output = selected.output
            if not self._check_and_continue():
                # 无占位符，直接输出
                self.exit(result=self._current_output)
        else:  # resolving_g
            # g 模式：用选中值替换占位符，继续检查
            if self._current_placeholder is None:
                print("错误：内部状态错误", file=sys.stderr)
                sys.exit(1)
            # 替换占位符
            self._current_output = replace_placeholder(
                self._full_output, self._current_placeholder, selected.output
            )
            self._mode = "searching"
            self._current_placeholder = None
            self._hide_resolve_ui()
            # 继续检查是否有更多占位符
            if not self._check_and_continue():
                self.exit(result=self._current_output)

    def _confirm_input(self) -> None:
        """Confirm input from i mode."""
        resolve_input = self.query_one("#resolve-input", Input)
        value = resolve_input.value.strip()

        if not value:
            print("错误：输入不能为空", file=sys.stderr)
            sys.exit(1)

        # 清空输入框
        input_widget = self.query_one("#search-input", Input)
        input_widget.value = ""

        if self._current_placeholder is None:
            print("错误：内部状态错误", file=sys.stderr)
            sys.exit(1)

        # 替换占位符
        self._current_output = replace_placeholder(
            self._full_output, self._current_placeholder, value
        )
        self._mode = "searching"
        self._current_placeholder = None
        self._hide_resolve_ui()

        # 继续检查是否有更多占位符
        if not self._check_and_continue():
            self.exit(result=self._current_output)


def run_app(selections: list[Selection]) -> str | None:
    """Run the TUI app and return selected command."""
    app = USelApp(selections)
    return app.run()
