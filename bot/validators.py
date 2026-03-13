"""
Input validation for order parameters.
All functions raise ValueError with a clear message if something is wrong.
"""

VALID_SIDES = ["BUY", "SELL"]
VALID_ORDER_TYPES = ["MARKET", "LIMIT"]


def validate_symbol(symbol: str) -> str:
    """
    Symbol must be a non-empty string made only of letters.
    Example valid inputs: btcusdt, ETHUSDT
    """
    if not symbol:
        raise ValueError("Symbol cannot be empty.")
    # Remove spaces just in case the user added any
    symbol = symbol.strip().upper()
    if not symbol.isalpha():
        raise ValueError(
            f"Invalid symbol '{symbol}'. "
            "Use only letters, e.g. BTCUSDT or ETHUSDT."
        )
    return symbol


def validate_side(side: str) -> str:
    """
    Side must be BUY or SELL (case-insensitive).
    """
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(
            f"Invalid side '{side}'. "
            f"Allowed values: {', '.join(VALID_SIDES)}"
        )
    return side


def validate_order_type(order_type: str) -> str:
    """
    Order type must be MARKET or LIMIT (case-insensitive).
    """
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. "
            f"Allowed values: {', '.join(VALID_ORDER_TYPES)}"
        )
    return order_type


def validate_quantity(quantity: str) -> float:
    """
    Quantity must be a positive number.
    Accepts strings like '0.01' or '5'.
    """
    try:
        qty = float(quantity)
    except (TypeError, ValueError):
        raise ValueError(
            f"Invalid quantity '{quantity}'. Must be a number, e.g. 0.01"
        )
    if qty <= 0:
        raise ValueError(
            f"Quantity must be greater than 0. Got: {qty}"
        )
    return qty


def validate_price(price: str) -> float:
    """
    Price must be a positive number.
    Only required for LIMIT orders.
    """
    try:
        p = float(price)
    except (TypeError, ValueError):
        raise ValueError(
            f"Invalid price '{price}'. Must be a number, e.g. 30000.5"
        )
    if p <= 0:
        raise ValueError(
            f"Price must be greater than 0. Got: {p}"
        )
    return p
