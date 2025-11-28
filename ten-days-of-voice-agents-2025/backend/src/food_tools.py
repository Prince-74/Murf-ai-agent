# backend/src/food_tools.py
import os
import json
import asyncio
from datetime import datetime
from livekit.agents import function_tool

BASE = os.path.join(os.path.dirname(__file__), "..", "shared-data")
CATALOG_PATH = os.path.join(BASE, "catalog.json")
RECIPES_PATH = os.path.join(BASE, "recipes.json")
ORDERS_PATH = os.path.join(BASE, "orders.json")
CART_STATE_PATH = os.path.join(BASE, "cart_state.json")  # single-session cart storage

# --- helpers (use threads for file IO) ---
async def _read_json(path, default):
    def _sync():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return default
        except Exception:
            return default
    return await asyncio.to_thread(_sync)

async def _write_json(path, data):
    def _sync():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
    await asyncio.to_thread(_sync)


# --- tools ---

@function_tool
async def list_catalog():
    """Return full catalog (items list)."""
    data = await _read_json(CATALOG_PATH, {"items": []})
    return {"items": data.get("items", [])}


@function_tool
async def find_item(item_name: str):
    """Return item object (first match) or None."""
    data = await _read_json(CATALOG_PATH, {"items": []})
    for it in data.get("items", []):
        if it.get("name", "").lower() == item_name.lower():
            return {"item": it}
    # fuzzy-ish fallback by token
    for it in data.get("items", []):
        if item_name.lower() in it.get("name", "").lower():
            return {"item": it}
    return {"item": None}


@function_tool
async def add_to_cart(item: str, quantity: int = 1):
    """Add quantity of item to the cart state."""
    catalog = await _read_json(CATALOG_PATH, {"items": []})
    items = catalog.get("items", [])
    found = None
    for it in items:
        if it.get("name", "").lower() == item.lower() or item.lower() in it.get("name","").lower():
            found = it
            break
    if not found:
        return {"error": "item_not_found", "item": item}

    cart_state = await _read_json(CART_STATE_PATH, {"cart": {}})
    cart = cart_state.get("cart", {})

    key = found["name"]
    cart[key] = cart.get(key, 0) + max(1, int(quantity))
    cart_state["cart"] = cart
    await _write_json(CART_STATE_PATH, cart_state)
    return {"ok": True, "cart": cart}


@function_tool
async def remove_from_cart(item: str):
    cart_state = await _read_json(CART_STATE_PATH, {"cart": {}})
    cart = cart_state.get("cart", {})
    matched = None
    for k in list(cart.keys()):
        if k.lower() == item.lower() or item.lower() in k.lower():
            matched = k
            break
    if not matched:
        return {"error": "not_in_cart", "item": item}
    del cart[matched]
    cart_state["cart"] = cart
    await _write_json(CART_STATE_PATH, cart_state)
    return {"ok": True, "cart": cart}


@function_tool
async def update_quantity(item: str, quantity: int):
    cart_state = await _read_json(CART_STATE_PATH, {"cart": {}})
    cart = cart_state.get("cart", {})
    matched = None
    for k in list(cart.keys()):
        if k.lower() == item.lower() or item.lower() in k.lower():
            matched = k
            break
    if not matched:
        return {"error": "not_in_cart", "item": item}
    if quantity <= 0:
        del cart[matched]
    else:
        cart[matched] = int(quantity)
    cart_state["cart"] = cart
    await _write_json(CART_STATE_PATH, cart_state)
    return {"ok": True, "cart": cart}


@function_tool
async def get_cart():
    cart_state = await _read_json(CART_STATE_PATH, {"cart": {}})
    return {"cart": cart_state.get("cart", {})}


@function_tool
async def save_order(customer_name: str = "Guest", address: str = ""):
    """
    Save current cart as an order entry in orders.json. Returns created order.
    """
    cart_state = await _read_json(CART_STATE_PATH, {"cart": {}})
    cart = cart_state.get("cart", {})
    if not cart:
        return {"error": "cart_empty"}

    catalog = await _read_json(CATALOG_PATH, {"items": []})
    prices = {it["name"]: it.get("price", 0) for it in catalog.get("items", [])}

    items_list = []
    total = 0
    for name, qty in cart.items():
        price = prices.get(name, 0)
        items_list.append({"name": name, "quantity": qty, "unit_price": price, "line_total": price * qty})
        total += price * qty

    orders = await _read_json(ORDERS_PATH, {"orders": []})
    next_id = 1
    if orders.get("orders"):
        last = orders["orders"][-1]
        next_id = last.get("id", 0) + 1

    order_obj = {
        "id": next_id,
        "customer_name": customer_name,
        "address": address,
        "order": items_list,
        "total": total,
        "timestamp": datetime.utcnow().isoformat()
    }

    orders.setdefault("orders", []).append(order_obj)
    await _write_json(ORDERS_PATH, orders)

    # clear cart
    await _write_json(CART_STATE_PATH, {"cart": {}})

    return {"ok": True, "order": order_obj}


@function_tool
async def list_recipes():
    data = await _read_json(RECIPES_PATH, {})
    return {"recipes": data}


@function_tool
async def add_recipe_items_to_cart(recipe_name: str, servings: int = 1):
    recipes = await _read_json(RECIPES_PATH, {})
    mapping = recipes.get(recipe_name.lower()) or recipes.get(recipe_name) or recipes.get(recipe_name.title())
    if not mapping:
        return {"error": "recipe_not_found", "recipe": recipe_name}

    # basic: add each ingredient once per serving
    result = {"added": []}
    for ing in mapping:
        await add_to_cart(ing, max(1, int(servings)))
        result["added"].append({"item": ing, "qty": servings})
    cart = (await _read_json(CART_STATE_PATH, {"cart": {}})).get("cart", {})
    result["cart"] = cart
    return result
