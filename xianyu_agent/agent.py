from pathlib import Path
from typing import Dict, List
from urllib.parse import quote

from .capability import IMAGE_SEARCH_TEXT_HINTS, detect_image_search_support_from_html
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

    def _load_goofish_homepage_html(self) -> str:
        try:
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
            page.wait_for_timeout(1500)
            html = page.content()
            browser.close()
        return html

    def probe_image_search_support(self) -> Dict[str, object]:
        html = self._load_goofish_homepage_html()
        result = detect_image_search_support_from_html(html)
        result["site"] = "https://www.goofish.com/"
        return result

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

    @staticmethod
    def _try_upload_with_existing_inputs(page, image_path: str) -> bool:
        file_input_candidates = [
            'input[type="file"]',
            'input[accept*="image"]',
            'input[accept*="png"]',
            'input[accept*="jpg"]',
        ]

        for selector in file_input_candidates:
            locator = page.locator(selector).first
            if locator.count() > 0:
                locator.set_input_files(image_path)
                return True
        return False

    @staticmethod
    def _try_upload_by_triggering_file_chooser(page, image_path: str) -> bool:
        trigger_selectors = [
            'button:has-text("以图搜")',
            'button:has-text("拍照搜")',
            'button:has-text("图搜")',
            '[role="button"]:has-text("以图搜")',
            '[aria-label*="以图搜"]',
            '[title*="以图搜"]',
        ]

        for selector in trigger_selectors:
            locator = page.locator(selector).first
            if locator.count() == 0:
                continue
            try:
                with page.expect_file_chooser(timeout=2000) as fc_info:
                    locator.click()
                fc_info.value.set_files(image_path)
                return True
            except Exception:
                continue

        # fallback: click generic text hints and retry direct file-input search
        for hint in IMAGE_SEARCH_TEXT_HINTS:
            locator = page.get_by_text(hint).first
            if locator.count() == 0:
                continue
            try:
                locator.click(timeout=1500)
                page.wait_for_timeout(400)
            except Exception:
                continue
            if XianyuAgent._try_upload_with_existing_inputs(page, image_path):
                return True

        return False

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
            page.wait_for_timeout(1500)

            resolved_path = str(image_file.resolve())
            uploaded = self._try_upload_with_existing_inputs(page, resolved_path)
            if not uploaded:
                uploaded = self._try_upload_by_triggering_file_chooser(page, resolved_path)

            if not uploaded:
                html = page.content()
                browser.close()
                support_result = detect_image_search_support_from_html(html)
                raise RuntimeError(
                    "未在页面找到图片上传控件（已尝试直接 input 与触发按钮两种策略）。"
                    f" 检测结果: {support_result}"
                    "。建议先用关键词模式进行估价，或检查当前账号/地区页面是否放开网页以图搜。"
                )

            try:
                page.wait_for_load_state("networkidle", timeout=self.timeout_ms)
                page.wait_for_timeout(2500)
            except PlaywrightTimeoutError:
                pass

            html = page.content()
            browser.close()

        return self._parse_products(html, max_items=max_items)
