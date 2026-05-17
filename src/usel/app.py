"""TUI application for usel using textual."""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.events import Key
from textual.widgets import Header, Input, Static

from .models import Selection


class ItemWidget(Static):
    """Wrapper for selection items to track selection state."""

    def __init__(self, selection: Selection, index: int, selected: bool = False) -> None:
        content = f"[#C4E88D]{selection.display_title}[/#C4E88D]  [dim #FE747E]`{selection.output}`[/dim #FE747E]  [dim #4FD6BE]({selection.group})[/dim #4FD6BE]"
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
    """

    def __init__(self, selections: list[Selection]) -> None:
        super().__init__()
        self._sorted_selections = sorted(selections, key=lambda s: (s.group, s.title))
        self._current_index: int = 0

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="Search...", id="search-input")
        yield VerticalScroll(id="results")
        yield Static("↵ confirm  q quit", id="hint")

    def on_mount(self) -> None:
        """Initialize the app."""
        input_widget = self.query_one("#search-input", Input)
        input_widget.focus()
        self._do_search("")  # 显示初始列表

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        self._current_index = 0
        self._do_search(event.value)

    def _do_search(self, query: str) -> None:
        """Perform search and update display."""
        query_lower = query.lower()

        if query:
            filtered = [
                s
                for s in self._sorted_selections
                if query_lower in s.title.lower()
                or query_lower in s.output.lower()
                or query_lower in s.group.lower()
            ]
        else:
            filtered = self._sorted_selections

        results = self.query_one("#results", VerticalScroll)
        # Clear and rebuild
        results.remove_children()
        for i, selection in enumerate(filtered):
            item = ItemWidget(selection, i, selected=(i == self._current_index))
            results.mount(item)

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
        if items and 0 <= self._current_index < len(items):
            self.exit(result=items[self._current_index].selection.output)


def run_app(selections: list[Selection]) -> str | None:
    """Run the TUI app and return selected command."""
    app = USelApp(selections)
    return app.run()
