from pathlib import Path

from canvy.types import CanvyConfig

CANVAS_TEST_KEY = (
    "1000~aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
)
CANVAS_TEST_URL = "https://university.canvas.com"


def vanilla_config(path: Path) -> CanvyConfig:
    """
    canvyConfig(
        canvas_key=CANVAS_TEST_KEY,
        canvas_url=CANVAS_TEST_URL,
        storage_path=path,
        selected_courses=[]
    )
    """
    return CanvyConfig(
        canvas_key=CANVAS_TEST_KEY,
        canvas_url=CANVAS_TEST_URL,
        storage_path=path,
    )
