from typing import List
from urllib.parse import quote

from .models import Product
from .parsers import extract_next_data, extract_products_from_dom, extract_products_from_next_data


class XianyuAgent:
    def __init__(self, headless: bool = True, timeout_ms: int = 30000):
        self.headless = headless
        self.timeout_ms = timeout_ms

    def crawl_keyword(self, keyword: str, max_items: int = 20) -> List[Product]:
        try:
            from playwright.sync_api import sync_playwright
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "缺少 playwright 依赖，请先执行: pip install playwright && python -m playwright install chromium"
            ) from exc

        search_url = f"https://www.goofish.com/search?keyword={quote(keyword)}"

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=self.headless)
            context = browser.new_context()
            page = context.new_page()
            page.goto(search_url, wait_until="domcontentloaded", timeout=self.timeout_ms)
            page.wait_for_timeout(3000)
            html = page.content()
            browser.close()

        next_data = extract_next_data(html)
        products = extract_products_from_next_data(next_data, max_items=max_items)
        return products or extract_products_from_dom(html, max_items=max_items)
