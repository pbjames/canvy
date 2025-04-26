from pathlib import Path
from cansync.scripts.teacher import make_problem_sheet, validate_typst
from cansync.types import CansyncConfig, ModelProvider

from tests.conftest import CANVAS_TEST_KEY, CANVAS_TEST_URL


def test_validate_typst():
    assert validate_typst("content")[0]


def test_validate_typst_false():
    res, body = validate_typst("#func(")
    assert not res and b"error: unclosed delimiter" in body


def test_make_problem_sheet(tmp_path: Path):
    config = CansyncConfig(
        canvas_key=CANVAS_TEST_KEY,
        canvas_url=CANVAS_TEST_URL,
        storage_path=tmp_path,
        default_provider=ModelProvider.OPENAI,
    )
    func = make_problem_sheet(config)


def test_canvas_files(): ...


def test_retrieve_knowledge(): ...


def test_teacher(): ...
