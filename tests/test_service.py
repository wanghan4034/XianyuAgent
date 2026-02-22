from xianyu_agent.models import Product
from xianyu_agent.service import summarize_prices


def test_summarize_prices():
    products = [
        Product("a", 100.0, None, None, None, None),
        Product("b", 200.0, None, None, None, None),
        Product("c", None, None, None, None, None),
    ]

    result = summarize_prices(products)
    assert result["count"] == 3
    assert result["priced_count"] == 2
    assert result["min_price"] == 100.0
    assert result["median_price"] == 150.0
    assert result["max_price"] == 200.0
