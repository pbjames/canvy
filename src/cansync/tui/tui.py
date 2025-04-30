from typing import ClassVar, override

from textual.app import App, ComposeResult
from textual.binding import BindingType
from textual.widgets import Footer, Header


class StopwatchApp(App[None]):
    BINDINGS: ClassVar[list[BindingType]] = [("d", "toggle_dark", "Toggle dark mode")]

    @override
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def action_toggle_dark(self):
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


def run():
    app = StopwatchApp()
    app.run()
