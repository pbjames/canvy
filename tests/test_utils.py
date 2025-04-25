import os
from pathlib import Path

import pytest

from cansync.types import CansyncConfig, ModelProvider
from cansync.utils import (
    better_course_name,
    create_dir,
    delete_config,
    get_config,
    set_config,
)
from tests.conftest import CANVAS_TEST_KEY, CANVAS_TEST_URL


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


# TODO: Make a fake canvas for it
def test_download_structured():
    assert True
