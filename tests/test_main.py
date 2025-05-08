import pytest

from canvy.main import add_https

# TODO: Not dying to add these unit tests soo


@pytest.mark.parametrize(
    "url,expected",
    [
        ("canvas.test.ac", "https://canvas.test.ac"),
        ("https://test.canvas.com", "https://test.canvas.com"),
        ("http://test-insecure.com", "http://test-insecure.com"),
    ],
)
def test_add_https(url: str, expected: str):
    assert add_https(url) == expected

def test_requires_config():
    ...
