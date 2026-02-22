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
