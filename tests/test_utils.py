import pytest

from cansync.utils import better_course_name


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
