from pathlib import Path

import pytest

from cansync.types import CansyncConfig, ModelProvider
from tests.conftest import vanilla_config


# TODO: FINISH
def test_verify_accessible_path(tmp_path: Path):
    with pytest.raises(ValueError):
        CansyncConfig.verify_accessible_path(Path("/"))
    with pytest.raises(PermissionError):
        CansyncConfig.verify_accessible_path(Path("/home/sigmaboy123"))
    assert CansyncConfig.verify_accessible_path(tmp_path) == tmp_path


def test_serialize_path(tmp_path: Path):
    assert CansyncConfig.serialize_path(vanilla_config(tmp_path), tmp_path) == str(
        tmp_path
    )


def test_serialize_provider(tmp_path: Path):
    assert (
        CansyncConfig.serialize_provider(vanilla_config(tmp_path), ModelProvider.OPENAI)
        == "OpenAI"
    )
