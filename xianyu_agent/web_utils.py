from pathlib import Path

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def is_allowed_image(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def parse_max_items(raw_value: str, default: int = 20, min_value: int = 1, max_value: int = 100) -> int:
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        return default
    return max(min_value, min(value, max_value))
