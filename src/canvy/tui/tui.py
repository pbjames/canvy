import logging
from typing import ClassVar, override

from textual.app import App, ComposeResult
from textual.binding import BindingType
from textual.containers import HorizontalGroup, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Button, Digits, Footer, Header

logger = logging.getLogger(__name__)


class Canvy(App[None]):
    BINDINGS: ClassVar[list[BindingType]] = []

    @override
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        # yield VerticalScroll(Stopwatch(), Stopwatch(), Stopwatch(), id="timers")


def run():
    app = Canvy()
    app.run()
