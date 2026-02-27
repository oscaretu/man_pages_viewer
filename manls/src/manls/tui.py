from textual.app import App, ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.widgets import Header, Footer, Static, ListView, ListItem
from textual.binding import Binding


def escape_markup(text: str) -> str:
    """Escape characters that Rich interprets as markup.

    The $ character in man pages (like $if, $else in bash man page) is
    interpreted as Rich markup. Solution: use $$ to escape (double dollar sign)
    and pass markup=False to Static widgets.
    """
    return text.replace("$", "$$")


class ManPageViewer(App):
    CSS = """
    Screen {
        layout: horizontal;
    }

    #sidebar {
        width: 28;
        height: 100%;
        border: solid $primary;
        background: $surface;
    }

    #sidebar:focus-within {
        border: double $accent;
    }

    #main {
        width: 1fr;
        height: 100%;
        border: solid $primary;
        background: $surface;
    }

    #main:focus-within {
        border: double $accent;
    }

    #section_list {
        height: 100%;
    }

    #content_scroll {
        height: 100%;
        overflow-y: scroll;
    }

    ListItem {
        padding: 0 1;
    }

    ListItem:focus {
        background: $accent;
    }

    #section_title {
        text-style: bold;
        color: $accent;
        padding: 1 2;
        background: $panel;
    }

    #content_text {
        padding: 1 2;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        # Tab: show=True and priority=True are required to display in Footer
        # because Textual hides Tab by default. key_display ensures it shows as "tab".
        Binding(
            "tab", "switch_panel", "Switch", show=True, key_display="tab", priority=True
        ),
        Binding("j", "scroll_down", "Scroll Down"),
        Binding("k", "scroll_up", "Scroll Up"),
        # key_display replaces the default "pgdown"/"pgup" display in Footer
        # (without it, Footer shows "^pgdown"/"^pgup")
        Binding("pgdown", "scroll_page_down", "Page Down", key_display="pgdown"),
        Binding("pgup", "scroll_page_up", "Page Up", key_display="pgup"),
        Binding("home", "scroll_home", "Home"),
        Binding("end", "scroll_end", "End"),
    ]

    def __init__(self, man_page, **kwargs):
        super().__init__(**kwargs)
        self.man_page = man_page
        self.current_section_index = 0

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="sidebar"):
            sections = self.man_page.sections
            yield ListView(
                *[ListItem(Static(s.title, markup=False)) for s in sections],
                id="section_list",
            )
        with Container(id="main"):
            yield Static("", markup=False, id="section_title")
            yield ScrollableContainer(
                Static("", markup=False, id="content_text"), id="content_scroll"
            )
        yield Footer()

    def on_mount(self) -> None:
        list_view = self.query_one("#section_list", ListView)
        list_view.index = 0
        self.update_content()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id == "section_list":
            index = event.list_view.index
            if index is not None:
                self.current_section_index = index
                self.update_content()

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.list_view.id == "section_list":
            index = event.list_view.index
            if index is not None:
                self.current_section_index = index
                self.update_content()

    def update_content(self):
        if self.man_page.sections:
            section = self.man_page.sections[self.current_section_index]
            title = self.query_one("#section_title", Static)
            content = self.query_one("#content_text", Static)
            title.update(f"  {section.title}")
            content.update(escape_markup(str(section.content)))

    def action_switch_panel(self) -> None:
        # Use self.focused to detect which widget has focus, not a manual
        # panel_focus variable, to correctly handle keyboard input per panel.
        focused = self.focused
        if focused and focused.id == "section_list":
            self.set_focus(self.query_one("#content_scroll", ScrollableContainer))
        else:
            self.set_focus(self.query_one("#section_list", ListView))

    def action_scroll_down(self) -> None:
        focused = self.focused
        if focused and focused.id == "section_list":
            list_view = self.query_one("#section_list", ListView)
            if (
                list_view.index is not None
                and list_view.index < len(self.man_page.sections) - 1
            ):
                list_view.index += 1
        elif focused and focused.id == "content_scroll":
            scroll = self.query_one("#content_scroll", ScrollableContainer)
            scroll.scroll_down()

    def action_scroll_up(self) -> None:
        focused = self.focused
        if focused and focused.id == "section_list":
            list_view = self.query_one("#section_list", ListView)
            if list_view.index is not None and list_view.index > 0:
                list_view.index -= 1
        elif focused and focused.id == "content_scroll":
            scroll = self.query_one("#content_scroll", ScrollableContainer)
            scroll.scroll_up()

    def action_scroll_page_down(self) -> None:
        focused = self.focused
        if focused and focused.id == "section_list":
            list_view = self.query_one("#section_list", ListView)
            max_idx = len(self.man_page.sections) - 1
            if list_view.index is not None:
                list_view.index = min(list_view.index + 10, max_idx)
        elif focused and focused.id == "content_scroll":
            scroll = self.query_one("#content_scroll", ScrollableContainer)
            scroll.scroll_page_down()

    def action_scroll_page_up(self) -> None:
        focused = self.focused
        if focused and focused.id == "section_list":
            list_view = self.query_one("#section_list", ListView)
            if list_view.index is not None:
                list_view.index = max(list_view.index - 10, 0)
        elif focused and focused.id == "content_scroll":
            scroll = self.query_one("#content_scroll", ScrollableContainer)
            scroll.scroll_page_up()

    def action_scroll_home(self) -> None:
        focused = self.focused
        if focused and focused.id == "section_list":
            list_view = self.query_one("#section_list", ListView)
            list_view.index = 0
        elif focused and focused.id == "content_scroll":
            scroll = self.query_one("#content_scroll", ScrollableContainer)
            scroll.scroll_home()

    def action_scroll_end(self) -> None:
        focused = self.focused
        if focused and focused.id == "section_list":
            list_view = self.query_one("#section_list", ListView)
            list_view.index = len(self.man_page.sections) - 1
        elif focused and focused.id == "content_scroll":
            scroll = self.query_one("#content_scroll", ScrollableContainer)
            scroll.scroll_end()

    async def action_quit(self) -> None:
        self.exit()
