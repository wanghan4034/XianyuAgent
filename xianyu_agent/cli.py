import argparse
import json

from .agent import XianyuAgent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="咸鱼商品抓取 Agent")
    parser.add_argument("keyword", help="搜索关键词，如：iPhone 15")
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

    agent = XianyuAgent(headless=not args.headed)
    products = agent.crawl_keyword(args.keyword, max_items=args.max_items)
    print(json.dumps([item.to_dict() for item in products], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
