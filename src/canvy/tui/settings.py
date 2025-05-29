from typing import ClassVar, override

from canvy.tui.const import CanvyMode
from canvy.types import CanvyConfig, ModelProvider
from canvy.utils import get_config
from textual import on
from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.screen import Screen
from textual.widgets import Button, Input, Static


class ProviderWidget(Static):
    config: CanvyConfig
    provider_type: ModelProvider

    DEFAULT_CSS: ClassVar[str] = """
    ProviderWidget {
        layout: vertical;
        width: 100%;
        height: auto;
        border: heavy $primary;
        padding: 1;
        margin-bottom: 1;
    }

    ProviderWidget.valid {
        background: rgba(0, 255, 0, 0.15);
        border: heavy green;
    }

    ProviderWidget.invalid {
        background: rgba(128, 128, 128, 0.15);
        border: heavy gray;
    }

    ProviderWidget > Static {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        margin-bottom: 1;
    }

    ProviderWidget Input {
        margin: 0 1;
    }
    """

    def __init__(self, config: CanvyConfig, provider: ModelProvider) -> None:
        super().__init__()
        self.config = config
        self.provider_type = provider
        self.refresh_validation_state()

    def is_valid(self) -> bool:
        if self.provider_type == ModelProvider.OPENAI:
            return bool(self.config.openai_key)
        elif self.provider_type == ModelProvider.ANTHRO:
            return bool(self.config.anthropic_key)
        elif self.provider_type == ModelProvider.OLLAMA:
            return bool(self.config.ollama_model)
        else:
            return False

    def refresh_validation_state(self) -> None:
        self.remove_class("valid")
        self.remove_class("invalid")
        self.add_class("valid" if self.is_valid() else "invalid")

    @override
    def compose(self) -> ComposeResult:
        yield Static(f"{self.provider_type.value} Configuration")
        if self.provider_type == ModelProvider.OPENAI:
            yield Input(
                value=self.config.openai_key,
                placeholder="Enter OpenAI API key",
                id="openai_key",
                password=True,
            )
        elif self.provider_type == ModelProvider.ANTHRO:
            yield Input(
                value=self.config.anthropic_key,
                placeholder="Enter Anthropic API key",
                id="anthropic_key", 
                password=True,
            )
        elif self.provider_type == ModelProvider.OLLAMA:
            yield Input(
                value=self.config.ollama_model,
                placeholder="Enter Ollama model name",
                id="ollama_model",
            )
        yield Button("Save", id="save_button", variant="primary")


class SettingsPage(Screen[None]):
    DEFAULT_CSS: ClassVar[str] = """
    SettingsPage {
        layout: vertical;
        align: center middle;
    }
    
    #settings_container {
        layout: vertical;
        border-title-align: center;
        max-width: 50%;
        min-width: 60;
        border: heavy $primary;
        padding: 2;
        background: $surface;
    }

    Input {
        margin: 1 0;
    }

    Button {
        margin: 1;
    }

    #button_group {
        margin-top: 2;
    }
    """

    config: CanvyConfig

    def __init__(self, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(name, id, classes)
        self.config = get_config()

    @override
    def compose(self) -> ComposeResult:
        with Static(id="settings_container") as container:
            container.border_title = "Settings"
            for provider in ModelProvider:
                if provider != ModelProvider.NONE:
                    yield ProviderWidget(self.config, provider)
            with HorizontalGroup(id="button_group"):
                yield Button("Save", id="save_button", variant="primary")
                yield Button("Cancel", id="quit_button", variant="error")

    def _update_config_from_inputs(self) -> None:
        if openai_input := self.query_one("#openai_key", Input):
            self.config.openai_key = openai_input.value
        if anthropic_input := self.query_one("#anthropic_key", Input):
            self.config.anthropic_key = anthropic_input.value
        if ollama_input := self.query_one("#ollama_model", Input):
            self.config.ollama_model = ollama_input.value

    @on(Button.Pressed, "#save_button")
    def save_settings(self) -> None:
        self._update_config_from_inputs()
        for widget in self.query(ProviderWidget):
            widget.refresh_validation_state()
        self.notify("Settings saved successfully!", severity="information")

    @on(Button.Pressed, "#quit_button")
    def quit(self):
        self.app.switch_mode(CanvyMode.MAIN)

    @on(Input.Changed)
    def on_input_changed(self) -> None:
        self._update_config_from_inputs()
        for widget in self.query(ProviderWidget):
            widget.refresh_validation_state()
