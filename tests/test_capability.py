from xianyu_agent.capability import detect_image_search_support_from_html


def test_detect_image_search_support_with_file_input() -> None:
    html = '<html><body><input type="file" accept="image/*"></body></html>'
    result = detect_image_search_support_from_html(html)
    assert result["has_file_input"] is True
    assert result["supported"] is True


def test_detect_image_search_support_with_text_hint() -> None:
    html = '<html><body><button>以图搜</button></body></html>'
    result = detect_image_search_support_from_html(html)
    assert "以图搜" in result["matched_text_hints"]
    assert result["supported"] is True
