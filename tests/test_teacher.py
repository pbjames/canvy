from pathlib import Path

from cansync.const import PS_DIRNAME
from cansync.scripts.teacher import make_problem_sheet, validate_typst
from tests.conftest import vanilla_config


def test_validate_typst():
    assert validate_typst("content")[0]


def test_validate_typst_failure():
    res, body = validate_typst("#func(")
    assert not res and b"error: unclosed delimiter" in body


def test_make_problem_sheet(tmp_path: Path):
    config = vanilla_config(tmp_path)
    func = make_problem_sheet(config)
    func(
        "test.pdf",
        "class",
        "title",
        # INFO: This content is only valid because of the # -> = conversion
        """
# hello everynyan
## how are you
### fine thank you
""",
    )
    file_bytes = (tmp_path / PS_DIRNAME / "test.pdf").read_bytes()
    assert b"hello everynyan" in file_bytes
    assert b"how are you" in file_bytes
    assert b"fine thank you" in file_bytes


def test_canvas_files(): ...


def test_retrieve_knowledge(): ...


def test_teacher(): ...
