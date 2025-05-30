from collections.abc import Callable
from pathlib import Path
from typing import ClassVar, Final, override

from canvy.const import API_KEY_REGEX, URL_REGEX
from canvy.tui.const import CanvyMode
from canvy.types import CanvyConfig, ModelProvider
from canvy.utils import get_config, set_config
from textual import on
from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.screen import Screen
from textual.widgets import Button, Input, OptionList, Static
import logging
import re

from textual.widgets.option_list import Option


logger = logging.getLogger(__name__)

ConfigMutator = Callable[[CanvyConfig], CanvyConfig]


class Provider(Static):
    config: CanvyConfig
    provider_type: ModelProvider

    DEFAULT_CSS: ClassVar[
        str
    ] = """
    Provider {
        layout: vertical;
        width: 100%;
        height: auto;
        border: hkey $primary;
        margin: 1;
    }

    Provider.valid {
        background: rgba(0, 255, 0, 0.16);
        border: hkey green;
    }

    Provider.invalid {
        background: rgba(128, 128, 128, 0.08);
        border: hkey gray;
    }

    Provider > Static {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        margin-bottom: 1;
    }

    Provider Input {
        margin: 0 1;
    }
    """

    @override
    def compose(self) -> ComposeResult:
        yield Static(f"{self.provider_type.value}")
        if self.provider_type is ModelProvider.OPENAI:
            yield Input(
                value=self.config.openai_key,
                placeholder="Enter OpenAI API key",
                id="openai_key",
                password=True,
            )
        elif self.provider_type is ModelProvider.ANTHRO:
            yield Input(
                value=self.config.anthropic_key,
                placeholder="Enter Anthropic API key",
                id="anthropic_key",
                password=True,
            )
        elif self.provider_type is ModelProvider.OLLAMA:
            yield Input(
                value=self.config.ollama_model,
                placeholder="Enter Ollama model name",
                id="ollama_model",
            )

    def __init__(self, config: CanvyConfig, provider: ModelProvider) -> None:
        super().__init__()
        self.config = config
        self.provider_type = provider

    def config_mutator(self, config: CanvyConfig):
        if self.provider_type is ModelProvider.OPENAI:
            config.openai_key = self.config.openai_key
        elif self.provider_type is ModelProvider.ANTHRO:
            config.anthropic_key = self.config.anthropic_key
        elif self.provider_type is ModelProvider.OLLAMA:
            config.ollama_model = self.config.ollama_model
        return config

    def on_mount(self):
        self.refresh_validation_state()

    @property
    def valid(self) -> bool:
        # TODO: Update this
        input_widget = self.query_exactly_one(Input)
        return bool(input_widget.value)

    def refresh_validation_state(self) -> None:
        self.remove_class("valid")
        self.remove_class("invalid")
        self.add_class("valid" if self.valid else "invalid")

    @on(Input.Changed)
    def on_input_changed(self) -> None:
        self.refresh_validation_state()


class Canvas(Static):
    config: Final[CanvyConfig]
    border_title: str

    DEFAULT_CSS: ClassVar[
        str
    ] = """
    Canvas {
        layout: vertical;
        width: 100%;
        height: auto;
        border: hkey $primary;
        margin: 1;
    }

    Canvas.valid {
        background: rgba(0, 255, 0, 0.16);
        border: hkey green;
    }

    Canvas.invalid {
        background: rgba(128, 128, 128, 0.08);
        border: hkey gray;
    }

    Canvas > Static {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        margin-bottom: 1;
    }

    Canvas Input {
        margin: 1;
    }
    """

    def __init__(self, config: CanvyConfig):
        self.config = config
        super().__init__()

    @override
    def compose(self) -> ComposeResult:
        yield Static("Canvas")
        yield Input(self.config.canvas_url, "Canvas URL: ", id="url_input")
        yield Input(
            self.config.canvas_key,
            "Canvas API Key: ",
            id="canvas_key_input",
            password=True,
        )

    def on_mount(self):
        self.refresh_validation_state()

    def config_mutator(self, config: CanvyConfig):
        url_input = self.query_exactly_one("#url_input", expect_type=Input)
        key_input = self.query_exactly_one("#canvas_key_input", expect_type=Input)
        config.canvas_url = url_input.value
        config.canvas_key = key_input.value
        return config

    @property
    def valid(self) -> bool:
        url_input = self.query_exactly_one("#url_input", expect_type=Input)
        url_input = CanvyConfig.add_https(url_input.value)
        key_input = self.query_exactly_one("#canvas_key_input", expect_type=Input).value
        return (
            re.match(CanvyConfig.add_https(URL_REGEX), url_input) is not None
            and re.match(API_KEY_REGEX, key_input) is not None
        )

    @on(Input.Changed)
    def on_input_changed(self) -> None:
        self.refresh_validation_state()

    def refresh_validation_state(self) -> None:
        self.remove_class("valid")
        self.remove_class("invalid")
        self.add_class("valid" if self.valid else "invalid")


class StoragePath(Static):
    config: CanvyConfig
    border_title: str

    DEFAULT_CSS: ClassVar[
        str
    ] = """
    StoragePath {
        layout: vertical;
        width: 100%;
        height: auto;
        border: hkey $primary;
        margin: 1;
    }

    StoragePath.valid {
        background: rgba(0, 255, 0, 0.16);
        border: hkey green;
    }

    StoragePath.invalid {
        background: rgba(128, 128, 128, 0.08);
        border: hkey gray;
    }

    StoragePath > Static {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        margin-bottom: 1;
    }

    StoragePath Input {
        margin: 1;
    }
    """

    @override
    def compose(self) -> ComposeResult:
        yield Static("Storage Path")
        with VerticalGroup() as container:
            yield Input(str(self.config.storage_path), "Path: ", id="path_input")

    def on_mount(self):
        self.refresh_validation_state()

    def __init__(self, config: CanvyConfig):
        self.config = config
        super().__init__()

    @property
    def valid(self):
        path_input = self.query_exactly_one(Input)
        try:
            return CanvyConfig.verify_accessible_path(Path(path_input.value))
        except Exception as e:
            logger.debug(f"Invalid storage provided{e}")
            return False

    def config_mutator(self, config: CanvyConfig):
        path_input = self.query_exactly_one(Input)
        config.storage_path = Path(path_input.value)
        return config

    @on(Input.Changed)
    def on_input_changed(self) -> None:
        self.refresh_validation_state()

    def refresh_validation_state(self) -> None:
        self.remove_class("valid")
        self.remove_class("invalid")
        self.add_class("valid" if self.valid else "invalid")


class DefaultProvider(Static):
    config: CanvyConfig
    selected: ModelProvider
    border_title: str

    DEFAULT_CSS: ClassVar[
        str
    ] = """
    DefaultProvider {
        layout: vertical;
        width: 100%;
        height: auto;
        border: hkey $primary;
        margin: 1;
    }
    """

    @override
    def compose(self) -> ComposeResult:
        yield Static()
        with VerticalGroup():
            yield OptionList(*list(Option(p, id=p) for p in ModelProvider))

    def on_mount(self):
        self.border_title = "Default Provider"

    def __init__(self, config: CanvyConfig):
        self.config = config
        self.selected = config.default_provider
        super().__init__()

    def config_mutator(self, config: CanvyConfig):
        config.default_provider = self.selected
        return config

    @on(OptionList.OptionSelected)
    def update_selected(self, event: OptionList.OptionSelected):
        self.selected = ModelProvider(event.option.id)



class SettingsPage(Screen[None]):
    config: CanvyConfig

    DEFAULT_CSS: ClassVar[
        str
    ] = """
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
        margin: 0 2;
    }

    #button_group {
        margin-top: 2;
    }
    """

    def __init__(
        self, name: str | None = None, id: str | None = None, classes: str | None = None
    ) -> None:
        super().__init__(name, id, classes)
        self.config = get_config()

    @override
    def compose(self) -> ComposeResult:
        with VerticalGroup(id="settings_container") as container:
            container.border_title = "Settings"
            yield Canvas(self.config)
            for provider in ModelProvider:
                if provider != ModelProvider.NONE:
                    yield Provider(self.config, provider)
            yield StoragePath(self.config)
            yield DefaultProvider(self.config)
            with HorizontalGroup(id="button_group"):
                yield Button("Save", id="save_button", variant="primary")
                yield Button("Back", id="quit_button", variant="error")

    @on(Button.Pressed, "#save_button")
    def save_settings(self) -> None:
        providers = self.query(Provider)
        canvas = self.query_exactly_one(Canvas)
        storage = self.query_exactly_one(StoragePath)
        default_prov = self.query_exactly_one(DefaultProvider)
        mutations: list[ConfigMutator] = []
        mutations.extend(provider.config_mutator for provider in providers)
        mutations.append(canvas.config_mutator)
        mutations.append(storage.config_mutator)
        mutations.append(default_prov.config_mutator)
        for mu in mutations:
            self.config = mu(self.config)
        try:
            new_config = self.config.model_validate(self.config.model_dump())
            set_config(new_config)
            self.notify("Saved successfully.", severity="information")
        except Exception as e:
            self.notify("Error saving settings!", severity="error")
            logger.info(f"Error saving settings: {e}")
        self.quit()

    @on(Button.Pressed, "#quit_button")
    def quit(self):
        self.app.switch_mode(CanvyMode.MAIN)
