from __future__ import annotations

import re
from typing import Dict

IMAGE_SEARCH_TEXT_HINTS = (
    "以图搜",
    "拍照搜",
    "图片搜索",
    "搜同款",
    "图搜",
    "相机",
)


def detect_image_search_support_from_html(html: str) -> Dict[str, object]:
    lowered = html.lower()
    has_file_input = bool(re.search(r"<input[^>]+type=[\"']file[\"']", lowered))
    matched_hints = [hint for hint in IMAGE_SEARCH_TEXT_HINTS if hint in html]
    return {
        "has_file_input": has_file_input,
        "matched_text_hints": matched_hints,
        "supported": has_file_input or bool(matched_hints),
    }
