import logging.config
import os
from itertools import chain
from pathlib import Path

import pytest
from canvasapi.file import File
from canvasapi.requester import ResourceDoesNotExist

from canvy.const import LOGGING_CONFIG
from canvy.types import canvyConfig, ModelProvider
from canvy.utils import (
    better_course_name,
    create_dir,
    delete_config,
    download_structured,
    get_config,
    provider,
    set_config,
    setup_logging,
)
from tests.conftest import (
    CANVAS_TEST_KEY,
    CANVAS_TEST_URL,
    PROVIDER_TEST_KEYS,
    PROVIDER_TEST_MAPPING,
    PROVIDER_TEST_MODELS,
    vanilla_config,
)

logger = logging.getLogger(__name__)


def test_setup_logging(monkeypatch: pytest.MonkeyPatch):
    def mock_dictconfig[T](conf: T) -> T:
        return conf

    monkeypatch.setattr(logging.config, "dictConfig", mock_dictconfig)
    assert setup_logging() == LOGGING_CONFIG  # Unbelievably cursed


@pytest.mark.parametrize(
    "name,expected",
    [
        ("(12) Course", "Course"),
        ("Course (12381)", "Course"),
        ("", ""),
        ("Course12 cool course", "Course12 cool course"),
    ],
)
def test_better_course_name(name: str, expected: str):
    assert better_course_name(name) == expected


def test_create_dir(tmp_path: Path):
    new_path = tmp_path / "1c03177a-e4f6-4ae3-9c36-25b1e0880002"
    create_dir(new_path)
    assert new_path.exists() and new_path.owner() == os.getlogin() and new_path.is_dir()


def test_get_config(tmp_path: Path):
    new_path = tmp_path / "test_config.toml"
    doc_path = tmp_path / "Documents"
    os.makedirs(doc_path)
    with open(new_path, "w") as fp:
        fp.write(
            f"""\
canvas_key = "{CANVAS_TEST_KEY}"
canvas_url = "{CANVAS_TEST_URL}"
openai_key = ""
ollama_model = ""
storage_path = "{doc_path}"
default_provider = "OpenAI"
"""
        )
    equivalent = vanilla_config(doc_path)
    assert get_config(new_path) == equivalent


def test_set_config(tmp_path: Path):
    new_path = tmp_path / "test_config.toml"
    new_path.touch()
    doc_path = tmp_path / "Documents"
    os.makedirs(doc_path)
    expected_contents = f"""\
canvas_key = "{CANVAS_TEST_KEY}"
canvas_url = "{CANVAS_TEST_URL}"
openai_key = ""
ollama_model = ""
storage_path = "{doc_path}"
default_provider = "Ollama"
"""
    config = canvyConfig(
        canvas_key=CANVAS_TEST_KEY,
        canvas_url=CANVAS_TEST_URL,
        storage_path=doc_path,
        default_provider=ModelProvider.OLLAMA,
    )
    set_config(config, new_path)
    with open(new_path) as fp:
        assert fp.read() == expected_contents


def test_delete_config(tmp_path: Path):
    new_path = tmp_path / "delete_me.bin"
    new_path.touch()
    delete_config(new_path)
    assert not new_path.exists()


def test_download_structured(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    new_path = tmp_path / "course" / "slides.pdf"
    new_path.parent.mkdir()
    file = File(None, {"filename": "slides.pdf"})

    def mock_download(fn: Path):
        fn.touch()

    monkeypatch.setattr(file, "download", mock_download)
    res = download_structured(file, "course", storage_dir=tmp_path, force=False)
    assert new_path.exists() and new_path.is_file() and res


def test_download_structured_no_access(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    new_path = tmp_path / "course" / "slides.pdf"
    new_path.parent.mkdir()
    file = File(None, {"filename": "slides.pdf"})

    def mock_download(_: Path):
        e = "hello"
        raise ResourceDoesNotExist(e)

    monkeypatch.setattr(file, "download", mock_download)
    res = download_structured(file, "course", storage_dir=tmp_path, force=False)
    assert not new_path.exists() and not res


def test_download_structured_force(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    new_path = tmp_path / "course" / "slides.pdf"
    new_path.parent.mkdir()
    new_path.touch()
    file = File(None, {"filename": "slides.pdf"})

    def mock_download(fn: Path):
        fn.write_text("hello")

    monkeypatch.setattr(file, "download", mock_download)
    res = download_structured(file, "course", storage_dir=tmp_path, force=True)
    assert (
        new_path.exists()
        and new_path.is_file()
        and new_path.read_text() == "hello"
        and res
    )


def test_download_structured_shouldve_force(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    new_path = tmp_path / "course" / "slides.pdf"
    new_path.parent.mkdir()
    new_path.touch()
    file = File(None, {"filename": "slides.pdf"})

    def mock_download(fn: Path):
        fn.write_text("hello")

    monkeypatch.setattr(file, "download", mock_download)
    assert not download_structured(file, "course", storage_dir=tmp_path, force=False)


@pytest.mark.parametrize(
    "def_provider,key",
    chain(
        *[
            [
                (provider.value, ""),
                (provider.value, PROVIDER_TEST_KEYS[provider.value]),
            ]
            for provider in [ModelProvider.OPENAI, ModelProvider.OLLAMA]
        ]
    ),
)
def test_provider(tmp_path: Path, def_provider: str, key: str):
    setup_logging()
    logger.info(f"{def_provider}: {key}")
    args = {
        "canvas_key": CANVAS_TEST_KEY,
        "canvas_url": CANVAS_TEST_URL,
        "storage_path": tmp_path,
        "default_provider": def_provider,
    }
    args.update({PROVIDER_TEST_MAPPING[def_provider]: key})
    if not key:
        with pytest.raises(ValueError) as excinfo:
            provider(canvyConfig(**args))  # pyright: ignore[reportArgumentType]
        assert def_provider in str(excinfo.value)
    else:
        assert isinstance(
            provider(canvyConfig(**args)),  # pyright: ignore[reportArgumentType]
            PROVIDER_TEST_MODELS[def_provider],
        )
