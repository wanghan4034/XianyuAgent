from statistics import median
from typing import Dict, List, Optional

from .models import Product


def summarize_prices(products: List[Product]) -> Dict[str, Optional[float]]:
    prices = [p.price for p in products if p.price is not None]
    if not prices:
        return {"count": len(products), "priced_count": 0, "min_price": None, "median_price": None, "max_price": None}

    return {
        "count": len(products),
        "priced_count": len(prices),
        "min_price": min(prices),
        "median_price": float(median(prices)),
        "max_price": max(prices),
    }


def _percentile(sorted_values: List[float], p: float) -> float:
    if not sorted_values:
        raise ValueError("sorted_values 不能为空")
    if len(sorted_values) == 1:
        return sorted_values[0]

    rank = (len(sorted_values) - 1) * p
    low = int(rank)
    high = min(low + 1, len(sorted_values) - 1)
    weight = rank - low
    return sorted_values[low] * (1 - weight) + sorted_values[high] * weight


def build_market_report(products: List[Product]) -> Dict[str, object]:
    prices = sorted([p.price for p in products if p.price is not None])
    if not prices:
        return {
            "price_summary": summarize_prices(products),
            "price_band": {"low": None, "high": None},
            "insight": "当前样本没有可用价格，建议更换关键词或图片重试。",
            "comparable_count": 0,
        }

    q1 = _percentile(prices, 0.25)
    q2 = _percentile(prices, 0.50)
    q3 = _percentile(prices, 0.75)

    return {
        "price_summary": summarize_prices(products),
        "price_band": {
            "low": round(q1, 2),
            "high": round(q3, 2),
        },
        "insight": (
            f"建议将目标售价锚定在 {round(q1, 2)} - {round(q3, 2)} 元区间，"
            f"其中市场中位价约 {round(q2, 2)} 元。"
        ),
        "comparable_count": len(prices),
    }
