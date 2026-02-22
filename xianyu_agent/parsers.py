import json
import re
from html import unescape
from typing import Any, Dict, Iterable, List, Optional

from .models import Product


NEXT_DATA_PATTERN = re.compile(
    r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE
)


def _to_float(text: Optional[str]) -> Optional[float]:
    if not text:
        return None
    cleaned = re.sub(r"[^\d.]", "", text)
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _strip_tags(text: str) -> str:
    return unescape(re.sub(r"<[^>]+>", "", text)).strip()


def extract_next_data(html: str) -> Dict[str, Any]:
    match = NEXT_DATA_PATTERN.search(html)
    if not match:
        return {}
    payload = match.group(1).strip()
    if not payload:
        return {}
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return {}


def _walk_dict(node: Any) -> Iterable[Dict[str, Any]]:
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk_dict(value)
    elif isinstance(node, list):
        for item in node:
            yield from _walk_dict(item)


def extract_products_from_next_data(data: Dict[str, Any], max_items: int = 20) -> List[Product]:
    products: List[Product] = []
    seen_ids = set()

    for node in _walk_dict(data):
        title = node.get("title") or node.get("itemTitle")
        price = node.get("price") or node.get("itemPrice")
        item_id = str(node.get("itemId") or node.get("id") or "").strip() or None
        item_url = node.get("itemUrl") or node.get("url")
        location = node.get("city") or node.get("location")
        seller = node.get("sellerNick") or node.get("userNick") or node.get("seller")

        if not title:
            continue
        if item_id and item_id in seen_ids:
            continue

        products.append(
            Product(
                title=str(title).strip(),
                price=_to_float(str(price)) if price is not None else None,
                location=str(location).strip() if location else None,
                item_url=str(item_url).strip() if item_url else None,
                seller=str(seller).strip() if seller else None,
                item_id=item_id,
            )
        )
        if item_id:
            seen_ids.add(item_id)
        if len(products) >= max_items:
            return products

    return products


def extract_products_from_dom(html: str, max_items: int = 20) -> List[Product]:
    """Regex fallback parser when JSON payload is unavailable."""
    pattern = re.compile(
        r'<a[^>]*href="(?P<href>[^"]+)"[^>]*>(?P<body>.*?)</a>', re.DOTALL | re.IGNORECASE
    )

    products: List[Product] = []
    for match in pattern.finditer(html):
        body = match.group("body")
        href = unescape(match.group("href"))

        title_match = re.search(r'(?:title|item-title)[^>]*>(.*?)</', body, re.DOTALL | re.IGNORECASE)
        price_match = re.search(r'(?:¥|￥)\s*([\d.]+)', body)

        title = _strip_tags(title_match.group(1)) if title_match else _strip_tags(body)
        if len(title) < 4:
            continue

        products.append(
            Product(
                title=title,
                price=float(price_match.group(1)) if price_match else None,
                location=None,
                item_url=href,
                seller=None,
                item_id=None,
            )
        )
        if len(products) >= max_items:
            break

    return products
