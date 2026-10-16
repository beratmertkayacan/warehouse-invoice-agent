from app.data_store import ORDERS, STOCK, get_order, get_stock, get_warehouse


def test_get_order_returns_known_order():
    order = get_order("ORD-2001")

    assert order is not None
    assert order["customerId"] == "CUST-1001"
    assert order["quantity"] == 10


def test_get_order_returns_none_for_unknown_order():
    assert get_order("ORD-9999") is None


def test_get_stock_returns_item_for_known_pair():
    item = get_stock("WH-IST-01", "PROD-002")

    assert item is not None
    assert item["availableQuantity"] == 5


def test_get_stock_returns_none_for_unknown_pair():
    assert get_stock("WH-ANK-01", "PROD-002") is None


def test_get_warehouse_returns_none_for_unknown_id():
    assert get_warehouse("WH-XXX-99") is None


def test_returned_order_is_a_copy():
    order = get_order("ORD-2001")
    order["quantity"] = 999

    assert get_order("ORD-2001")["quantity"] == 10


def test_every_stock_item_uses_a_known_warehouse():
    for item in STOCK:
        assert get_warehouse(item["warehouseId"]) is not None


def test_order_numbers_are_unique():
    numbers = [order["orderNumber"] for order in ORDERS]

    assert len(numbers) == len(set(numbers))
