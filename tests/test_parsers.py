from xianyu_agent.parsers import extract_next_data, extract_products_from_next_data


def test_extract_products_from_next_data():
    html = '''
    <html><head></head><body>
    <script id="__NEXT_DATA__" type="application/json">
    {
      "props": {
        "pageProps": {
          "items": [
            {
              "itemId": "123",
              "title": "iPhone 14 Pro 256G",
              "price": "¥4500",
              "city": "杭州",
              "itemUrl": "https://www.goofish.com/item?id=123",
              "sellerNick": "数码小店"
            },
            {
              "itemId": "124",
              "title": "iPhone 13",
              "price": "2999",
              "city": "上海",
              "itemUrl": "https://www.goofish.com/item?id=124",
              "sellerNick": "二手优选"
            }
          ]
        }
      }
    }
    </script>
    </body></html>
    '''

    data = extract_next_data(html)
    products = extract_products_from_next_data(data, max_items=10)

    assert len(products) == 2
    assert products[0].item_id == "123"
    assert products[0].price == 4500.0
    assert products[1].title == "iPhone 13"
