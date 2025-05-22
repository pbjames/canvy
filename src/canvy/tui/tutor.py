from typing import ClassVar, override

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button


class TutorPage(Screen[None]):
    DEFAULT_CSS: ClassVar[str] = """"""

    @override
    def compose(self) -> ComposeResult:
        yield Button()
