"""Mock order tracking data for development and demos."""

ORDERS = {
    "FF1001": {
        "status": "OUT_FOR_DELIVERY",
        "estimated_delivery": "Today",
    },
    "FF1002": {
        "status": "DELIVERED",
        "estimated_delivery": "Delivered yesterday",
    },
    "FF1003": {
        "status": "PROCESSING",
        "estimated_delivery": "Tomorrow",
    },
}


def get_order_status(order_id: str) -> dict:
    """Return order status for a given order ID, or an error if not found."""
    return ORDERS.get(order_id, {"error": "Order not found"})
