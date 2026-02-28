from xianyu_agent.web_utils import is_allowed_image, parse_max_items


def test_is_allowed_image() -> None:
    assert is_allowed_image("a.jpg") is True
    assert is_allowed_image("b.PNG") is True
    assert is_allowed_image("c.gif") is False


def test_parse_max_items_with_bounds_and_fallback() -> None:
    assert parse_max_items("10") == 10
    assert parse_max_items("0") == 1
    assert parse_max_items("999") == 100
    assert parse_max_items("abc") == 20
