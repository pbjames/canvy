from time import monotonic
from typing import ClassVar, override

from textual.app import App, ComposeResult
from textual.binding import BindingType
from textual.containers import HorizontalGroup, VerticalScroll
from textual.reactive import reactive
from textual.timer import Timer
from textual.widgets import Button, Digits, Footer, Header


class TimeDisplay(Digits):
    """
    Sigma
    """

    start_time: reactive[float] = reactive(monotonic)
    time: reactive[float] = reactive(0.0)
    total: reactive[float] = reactive(0.0)
    update_timer: Timer | None = None

    def on_mount(self) -> None:
        self.update_timer = self.set_interval(1 / 60, self.update_time, pause=True)

    def update_time(self) -> None:
        self.time = self.total + (monotonic() - self.start_time)

    def watch_time(self, time: float) -> None:
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        self.update(f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}")

    def start(self) -> None:
        self.start_time = monotonic()
        if self.update_timer is not None:
            self.update_timer.resume()

    def stop(self) -> None:
        if self.update_timer is not None:
            self.update_timer.pause()
        self.total += monotonic() - self.start_time
        self.time = self.total

    def reset(self) -> None:
        self.total = 0
        self.time = 0


class Stopwatch(HorizontalGroup):

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Event handler called when a button is pressed.
        """
        button_id = event.button.id
        time_display = self.query_one(TimeDisplay)
        if button_id == "start":
            time_display.start()
            self.add_class("started")
        elif button_id == "stop":
            time_display.stop()
            self.remove_class("started")
        elif button_id == "reset":
            time_display.reset()

    @override
    def compose(self) -> ComposeResult:
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("Reset", id="reset")
        yield TimeDisplay("00:00:00:00")


class StopwatchApp(App[None]):
    CSS = """
    Stopwatch {
        background: $boost;
        height: 5;
        margin: 1;
        min-width: 50;
        padding: 1;
    }

    TimeDisplay {
        text-align: center;
        color: $foreground-muted;
        height: 3;
    }

    Button {
        width: 16;
    }

    #start {
        dock: left;
    }

    #stop {
        dock: left;
        display: none;
    }

    #reset {
        dock: right;
    }

    .started {
        background: $success-muted;
        color: $text;
    }

    .started TimeDisplay {
        color: $foreground;
    }

    .started #start {
        display: none
    }

    .started #stop {
        display: block
    }

    .started #reset {
        visibility: hidden
    }
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        ("a", "add_stopwatch", "Add"),
        ("r", "remove_stopwatch", "Remove"),
    ]

    @override
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield VerticalScroll(Stopwatch(), Stopwatch(), Stopwatch(), id="timers")

    def action_add_stopwatch(self) -> None:
        new_stopwatch = Stopwatch()
        self.query_one("#timers").mount(new_stopwatch)
        new_stopwatch.scroll_visible()

    def action_remove_stopwatch(self) -> None:
        timers = self.query("Stopwatch")
        if timers:
            timers.last().remove()


def run():
    app = StopwatchApp()
    app.run()
