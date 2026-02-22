import argparse
import json

from .agent import XianyuAgent
from .service import summarize_prices


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="咸鱼商品抓取 Agent")
    parser.add_argument("keyword", nargs="?", help="搜索关键词，如：iPhone 15")
    parser.add_argument("--image", help="本地图片路径：用于以图搜")
    parser.add_argument("--max-items", type=int, default=20, help="最多抓取商品数")
    parser.add_argument(
        "--headed",
        action="store_true",
        help="开启可视化浏览器（默认 headless）",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.keyword and not args.image:
        parser.error("请提供 keyword 或 --image")

    agent = XianyuAgent(headless=not args.headed)
    products = (
        agent.crawl_image(args.image, max_items=args.max_items)
        if args.image
        else agent.crawl_keyword(args.keyword, max_items=args.max_items)
    )

    print(
        json.dumps(
            {
                "summary": summarize_prices(products),
                "items": [item.to_dict() for item in products],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
