from collections.abc import Generator
from pathlib import Path

import pytest
from canvasapi.canvas import Canvas, Course
from canvasapi.file import File
from canvasapi.module import Module, ModuleItem

from canvy.scripts.downloader import download
from canvy.types import ModuleItemType
from tests.conftest import vanilla_config


@pytest.fixture
def canvas(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Canvas:
    config = vanilla_config(tmp_path)
    file_id = 98173

    def gen_module_items() -> Generator[ModuleItem, None, None]:
        module_item_1 = ModuleItem(
            None,
            {"id": 1, "type": str(ModuleItemType.ATTACHMENT), "content_id": file_id},
        )
        module_item_2 = ModuleItem(
            None,
            {"id": 2, "type": str(ModuleItemType.PAGE), "page_url": "some-test-page"},
        )
        yield module_item_1
        # yield module_item_2

    def gen_modules() -> Generator[Module, None, None]:
        module_1 = Module(None, {"id": 12, "name": "Cool 1"})
        monkeypatch.setattr(module_1, "get_module_items", gen_module_items)
        yield module_1

    def gen_courses(*_, **_a) -> Generator[Course, None, None]:
        course_1 = Course(
            None, {"id": 1, "course_code": "TEST", "name": "Chill course about testing"}
        )
        monkeypatch.setattr(course_1, "get_modules", gen_modules)
        yield course_1

    def fake_file_retrieval(_, id: int) -> File:
        file_1 = File(
            None, {"id": file_id, "filename": "slides.pdf", "display_name": "slides"}
        )

        def mock_download(fn: Path):
            fn.touch()

        monkeypatch.setattr(file_1, "download", mock_download)
        return file_1

    monkeypatch.setattr(Canvas, "get_courses", gen_courses)
    monkeypatch.setattr(Canvas, "get_file", fake_file_retrieval)
    return Canvas(config.canvas_url, config.canvas_key)


def test_extract_files_from_page(tmp_path: Path, canvas: Canvas):
    download(canvas, "https://canvas.test.ac.uk", storage_dir=tmp_path)
    fn_path = tmp_path / "Chill course about testing" / "Cool 1" / "slides.pdf"
    assert fn_path.exists() and fn_path.is_file()
