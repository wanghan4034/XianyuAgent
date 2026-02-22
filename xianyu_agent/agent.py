from pathlib import Path
from typing import List
from urllib.parse import quote

from .models import Product
from .parsers import extract_next_data, extract_products_from_dom, extract_products_from_next_data


class XianyuAgent:
    def __init__(self, headless: bool = True, timeout_ms: int = 30000):
        self.headless = headless
        self.timeout_ms = timeout_ms

    def _parse_products(self, html: str, max_items: int) -> List[Product]:
        next_data = extract_next_data(html)
        products = extract_products_from_next_data(next_data, max_items=max_items)
        return products or extract_products_from_dom(html, max_items=max_items)

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

        return self._parse_products(html, max_items=max_items)

    def crawl_image(self, image_path: str, max_items: int = 20) -> List[Product]:
        """Upload an image in goofish web and parse search results."""
        image_file = Path(image_path)
        if not image_file.exists():
            raise FileNotFoundError(f"图片不存在: {image_path}")

        try:
            from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
            from playwright.sync_api import sync_playwright
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "缺少 playwright 依赖，请先执行: pip install playwright && python -m playwright install chromium"
            ) from exc

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=self.headless)
            context = browser.new_context()
            page = context.new_page()
            page.goto("https://www.goofish.com/", wait_until="domcontentloaded", timeout=self.timeout_ms)

            file_input_candidates = [
                'input[type="file"]',
                'input[accept*="image"]',
            ]

            file_input_found = False
            for selector in file_input_candidates:
                locator = page.locator(selector).first
                if locator.count() > 0:
                    locator.set_input_files(str(image_file.resolve()))
                    file_input_found = True
                    break

            if not file_input_found:
                browser.close()
                raise RuntimeError("未在页面找到图片上传控件，请先确认当前闲鱼网页支持以图搜。")

            try:
                page.wait_for_load_state("networkidle", timeout=self.timeout_ms)
                page.wait_for_timeout(2500)
            except PlaywrightTimeoutError:
                # continue with whatever page content is available
                pass

            html = page.content()
            browser.close()

        return self._parse_products(html, max_items=max_items)
