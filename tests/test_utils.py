import logging.config
import os
from itertools import chain
from pathlib import Path

import pytest
from canvasapi.file import File
from canvasapi.requester import ResourceDoesNotExist

from cansync.const import LOGGING_CONFIG
from cansync.types import CansyncConfig, ModelProvider
from cansync.utils import (
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
    PROVIDER_TEST_MAPPING,
    PROVIDER_TEST_MODELS,
    PROVIDER_TEST_VALUES,
)


def test_setup_logging(monkeypatch: pytest.MonkeyPatch):
    def mock_dictconfig(conf):
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
default_provider = "Ollama"
"""
        )
    equivalent = CansyncConfig(
        canvas_key=CANVAS_TEST_KEY,
        canvas_url=CANVAS_TEST_URL,
        openai_key="",
        ollama_model="",
        storage_path=doc_path,
        default_provider=ModelProvider.OLLAMA,
    )
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
    config = CansyncConfig(
        canvas_key=CANVAS_TEST_KEY,
        canvas_url=CANVAS_TEST_URL,
        openai_key="",
        ollama_model="",
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
    "p,value",
    next(
        iter(
            chain(
                [(provider, ""), (provider, PROVIDER_TEST_VALUES[provider.value])]
                for provider in ModelProvider
            )
        )
    ),
)
def test_provider(tmp_path: Path, p: ModelProvider, value: str):
    args = {
        "canvas_key": CANVAS_TEST_KEY,
        "canvas_url": CANVAS_TEST_URL,
        "openai_key": "",
        "ollama_model": "",
        "storage_path": tmp_path,
        "default_provider": p.value,
    }
    args.update({PROVIDER_TEST_MAPPING[p.value]: value})
    if not value:
        with pytest.raises(ValueError) as excinfo:
            provider(CansyncConfig(**args))
        assert p.value in str(excinfo.value)
    else:
        assert isinstance(
            provider(CansyncConfig(**args)), PROVIDER_TEST_MODELS[p.value]
        )
