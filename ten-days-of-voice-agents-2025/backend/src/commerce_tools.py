import os
import json
from datetime import datetime
from livekit.agents import function_tool

BASE_DIR = os.path.dirname(__file__)
CATALOG_PATH = os.path.join(BASE_DIR, "catalog.json")
ORDERS_PATH = os.path.join(BASE_DIR, "orders.json")


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


@function_tool
async def list_products(filters: dict | None = None):
    data = _load_json(CATALOG_PATH)
    products = data["items"]

    if filters:
        if "category" in filters:
            products = [p for p in products if p["category"] == filters["category"]]

        if "max_price" in filters:
            products = [p for p in products if p["price"] <= filters["max_price"]]

        if "color" in filters:
            products = [p for p in products if p.get("color") == filters["color"]]

    return {"products": products}


@function_tool
async def create_order(line_items: list, buyer: dict):
    data = _load_json(CATALOG_PATH)
    catalog = {item["id"]: item for item in data["items"]}

    orders_file = _load_json(ORDERS_PATH)

    total = 0
    order_details = []

    for item in line_items:
        pid = item["product_id"]
        qty = item["quantity"]
        product = catalog.get(pid)

        if not product:
            continue

        total += product["price"] * qty
        order_details.append({
            "product_id": pid,
            "name": product["name"],
            "quantity": qty,
            "unit_price": product["price"]
        })

    order_id = len(orders_file["orders"]) + 1

    new_order = {
        "id": order_id,
        "buyer": buyer,
        "items": order_details,
        "total": total,
        "currency": "INR",
        "timestamp": datetime.utcnow().isoformat()
    }

    orders_file["orders"].append(new_order)
    _save_json(ORDERS_PATH, orders_file)

    return {"order": new_order}


@function_tool
async def last_order():
    data = _load_json(ORDERS_PATH)

    if not data["orders"]:
        return {"error": "no_orders"}

    return {"order": data["orders"][-1]}
