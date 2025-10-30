import getpass
import logging.config
import os
from pathlib import Path

import pytest
from canvasapi.file import File
from canvasapi.requester import ResourceDoesNotExist

from canvy.const import LOGGING_CONFIG
from canvy.types import CanvyConfig
from canvy.utils import (
    better_course_name,
    create_dir,
    delete_config,
    download_structured,
    get_config,
    has_config,
    set_config,
    setup_logging,
)
from tests.conftest import (
    CANVAS_TEST_KEY,
    CANVAS_TEST_URL,
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
    assert (
        new_path.exists()
        and new_path.owner() == getpass.getuser()
        and new_path.is_dir()
    )


def test_get_config(tmp_path: Path):
    new_path = tmp_path / "test_config.toml"
    doc_path = tmp_path / "Documents"
    os.makedirs(doc_path)
    with open(new_path, "w") as fp:
        fp.write(
            f"""\
canvas_key = "{CANVAS_TEST_KEY}"
canvas_url = "{CANVAS_TEST_URL}"
storage_path = "{doc_path}"
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
storage_path = "{doc_path}"
selected_courses = []
"""
    config = CanvyConfig(
        canvas_key=CANVAS_TEST_KEY,
        canvas_url=CANVAS_TEST_URL,
        storage_path=doc_path,
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


def test_download_structured_weirdpath(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    corrected_path = tmp_path / "Un_certain" / "slides.pdf"
    corrected_path.parent.mkdir()
    file = File(None, {"filename": "slides.pdf"})

    def mock_download(fn: Path):
        fn.touch()

    monkeypatch.setattr(file, "download", mock_download)
    res = download_structured(file, "Un/certain", storage_dir=tmp_path, force=False)
    assert corrected_path.exists() and corrected_path.is_file() and res


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


def test_has_config(tmp_path: Path):
    tmp_file_path = tmp_path / "config.toml"
    config = vanilla_config(tmp_path)
    set_config(config, tmp_file_path)
    assert has_config(tmp_file_path)
    delete_config(tmp_file_path)
    assert not has_config(tmp_file_path)
    assert not has_config(tmp_path / "doesntexist")
