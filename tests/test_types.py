from pathlib import Path

import pytest

from canvy.types import CanvyConfig, ModelProvider
from tests.conftest import vanilla_config


def test_verify_accessible_path(tmp_path: Path):
    with pytest.raises(ValueError):
        CanvyConfig.verify_accessible_path(Path("/"))
    with pytest.raises(PermissionError):
        CanvyConfig.verify_accessible_path(Path("/home/sigmaboy123"))
    with pytest.raises(FileExistsError):
        file_path = tmp_path / "touched"
        file_path.touch()
        CanvyConfig.verify_accessible_path(file_path)
    assert CanvyConfig.verify_accessible_path(tmp_path) == tmp_path


def test_serialize_path(tmp_path: Path):
    assert CanvyConfig.serialize_path(vanilla_config(tmp_path), tmp_path) == str(
        tmp_path
    )


def test_serialize_provider(tmp_path: Path):
    assert (
        CanvyConfig.serialize_provider(vanilla_config(tmp_path), ModelProvider.OPENAI)
        == "OpenAI"
    )


@pytest.mark.parametrize(
    "url,expected",
    [
        ("canvas.test.ac", "https://canvas.test.ac"),
        ("https://test.canvas.com", "https://test.canvas.com"),
        ("http://test-insecure.com", "http://test-insecure.com"),
    ],
)
def test_add_https(url: str, expected: str):
    assert CanvyConfig.add_https(url) == expected
