import json
from livekit.agents import function_tool, RunContext

# Global state (simple approach for Day 2)
ORDER_STATE = {
    "drinkType": None,
    "size": None,
    "milk": None,
    "extras": [],
    "name": None,
}

@function_tool
async def update_order(context: RunContext, field: str, value: str):
    """Update one field in the coffee order."""
    global ORDER_STATE

    if field == "extras":
        ORDER_STATE["extras"].append(value)
    else:
        ORDER_STATE[field] = value

    return f"Updated {field} to {value}."


@function_tool
async def is_order_complete(context: RunContext):
    """Check if all required fields are filled."""
    global ORDER_STATE
    for key, value in ORDER_STATE.items():
        if value in [None, "", []]:
            return False
    return True


@function_tool
async def save_order(context: RunContext):
    """Save the order to a JSON file."""
    global ORDER_STATE
    with open("coffee_order.json", "w") as f:
        json.dump(ORDER_STATE, f, indent=4)

    return "Order saved."
