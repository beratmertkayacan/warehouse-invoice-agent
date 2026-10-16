import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_json(file_name: str) -> list[dict]:
    path = DATA_DIR / file_name
    with path.open(encoding="utf-8") as file:
        return json.load(file)


WAREHOUSES = load_json("warehouses.json")
STOCK = load_json("stock.json")
ORDERS = load_json("orders.json")


def get_warehouse(warehouse_id: str) -> dict | None:
    for warehouse in WAREHOUSES:
        if warehouse["warehouseId"] == warehouse_id:
            return dict(warehouse)
    return None


def get_order(order_number: str) -> dict | None:
    for order in ORDERS:
        if order["orderNumber"] == order_number:
            return dict(order)
    return None


def get_stock(warehouse_id: str, product_id: str) -> dict | None:
    for item in STOCK:
        if item["warehouseId"] == warehouse_id and item["productId"] == product_id:
            return dict(item)
    return None
