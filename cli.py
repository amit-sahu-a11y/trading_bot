

import argparse
import os
import sys

from dotenv import dotenv_values

from bot.client import BinanceClient
from bot.logging_config import setup_logging
from bot.orders import OrderManager
from bot.validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_symbol,
)


# ---------------------------------------------------------------------------
# Pretty-print helpers
# ---------------------------------------------------------------------------

def print_separator(char: str = "-", width: int = 40):
    print(char * width)


def print_order_summary(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float = None,
    stop_price: float = None,
):
    print()
    print_separator()
    print("  ORDER REQUEST SUMMARY")
    print_separator()
    print(f"  Symbol       : {symbol}")
    print(f"  Side         : {side}")
    print(f"  Order Type   : {order_type}")
    print(f"  Quantity     : {quantity}")
    if stop_price is not None:
        print(f"  Stop Price   : {stop_price}")
    if price is not None:
        print(f"  Limit Price  : {price}")
    print_separator()
    print()


def print_order_response(response: dict):
    print()
    print_separator()
    print("  ORDER RESPONSE")
    print_separator()
    print(f"  Order ID     : {response.get('orderId', 'N/A')}")
    print(f"  Client OID   : {response.get('clientOrderId', 'N/A')}")
    print(f"  Status       : {response.get('status', 'N/A')}")
    print(f"  Symbol       : {response.get('symbol', 'N/A')}")
    print(f"  Side         : {response.get('side', 'N/A')}")
    print(f"  Type         : {response.get('type', 'N/A')}")
    print(f"  Quantity     : {response.get('origQty', 'N/A')}")
    print(f"  Executed Qty : {response.get('executedQty', 'N/A')}")
    print(f"  Avg Price    : {response.get('avgPrice', 'N/A')}")
    if response.get("price"):
        print(f"  Limit Price  : {response.get('price', 'N/A')}")
    if response.get("stopPrice"):
        print(f"  Stop Price   : {response.get('stopPrice', 'N/A')}")
    print_separator()
    print()


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place orders on Binance Futures Testnet (USDT-M)",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01\n"
            "  python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 30000\n"
            "  python cli.py --symbol ETHUSDT --side BUY --type STOP_LIMIT --quantity 0.1 --stop-price 2000 --price 1990\n"
        ),
    )

    parser.add_argument(
        "--symbol",
        required=True,
        metavar="SYMBOL",
        help="Trading pair symbol, e.g. BTCUSDT",
    )
    parser.add_argument(
        "--side",
        required=True,
        choices=["BUY", "SELL", "buy", "sell"],
        metavar="SIDE",
        help="Order side: BUY or SELL",
    )
    parser.add_argument(
        "--type",
        required=True,
        dest="order_type",
        choices=["MARKET", "LIMIT", "STOP_LIMIT", "market", "limit", "stop_limit"],
        metavar="TYPE",
        help="Order type: MARKET, LIMIT, or STOP_LIMIT",
    )
    parser.add_argument(
        "--quantity",
        required=True,
        metavar="QTY",
        help="Amount to buy or sell, e.g. 0.01",
    )
    parser.add_argument(
        "--price",
        metavar="PRICE",
        help="Limit price (required for LIMIT and STOP_LIMIT orders)",
    )
    parser.add_argument(
        "--stop-price",
        dest="stop_price",
        metavar="STOP_PRICE",
        help="Stop trigger price (required for STOP_LIMIT orders)",
    )

    return parser


# ---------------------------------------------------------------------------
# Load API credentials from .env
# ---------------------------------------------------------------------------

def load_credentials() -> tuple[str, str]:
    """
    Load API_KEY and API_SECRET.
    Looks in .env file first, then environment variables.
    """
    config = dotenv_values(".env")
    api_key = config.get("API_KEY") or os.getenv("API_KEY")
    api_secret = config.get("API_SECRET") or os.getenv("API_SECRET")

    if not api_key or not api_secret:
        print(
            "[ERROR] API_KEY and API_SECRET are missing.\n"
            "Create a .env file with:\n"
            "  API_KEY=your_key\n"
            "  API_SECRET=your_secret\n"
        )
        sys.exit(1)

    return api_key, api_secret



def main():
    logger = setup_logging()
    parser = build_parser()
    args = parser.parse_args()

 
    try:
        symbol = validate_symbol(args.symbol)
        side = validate_side(args.side)
        order_type = validate_order_type(args.order_type)
        quantity = validate_quantity(args.quantity)

        price = None
        stop_price = None

        if order_type == "LIMIT":
            if not args.price:
                parser.error("--price is required for LIMIT orders.")
            price = validate_price(args.price)

        elif order_type == "STOP_LIMIT":
            if not args.price:
                parser.error("--price (limit price) is required for STOP_LIMIT orders.")
            if not args.stop_price:
                parser.error("--stop-price is required for STOP_LIMIT orders.")
            price = validate_price(args.price)
            stop_price = validate_price(args.stop_price)

    except ValueError as e:
        logger.error(f"Input validation failed: {e}")
        print(f"\n[ERROR] {e}\n")
        sys.exit(1)

    # --- Show what we're about to do ---
    print_order_summary(symbol, side, order_type, quantity, price, stop_price)

    # --- Load credentials and set up client ---
    api_key, api_secret = load_credentials()
    client = BinanceClient(api_key, api_secret)
    manager = OrderManager(client)

    # --- Optional: ping the testnet first ---
    logger.info("Checking connectivity to Binance Testnet...")
    if not client.ping():
        print("[ERROR] Cannot reach Binance Testnet. Check your internet connection.")
        sys.exit(1)

    # --- Place the order ---
    try:
        logger.info(f"Submitting {order_type} order...")

        if order_type == "MARKET":
            response = manager.place_market_order(symbol, side, quantity)

        elif order_type == "LIMIT":
            response = manager.place_limit_order(symbol, side, quantity, price)

        elif order_type == "STOP_LIMIT":
            response = manager.place_stop_limit_order(
                symbol, side, quantity, stop_price, price
            )

        print_order_response(response)
        print("[SUCCESS] Order placed successfully!")
        logger.info(f"Order success | ID={response.get('orderId')} | Status={response.get('status')}")

    except RuntimeError as e:
        logger.error(f"Order failed: {e}")
        print(f"\n[FAILURE] Order failed: {e}\n")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n[FAILURE] Unexpected error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
