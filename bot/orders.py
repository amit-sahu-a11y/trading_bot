"""
orders.py - Order placement logic.

This module sits between the CLI and the raw API client.
It knows how to build the right parameters for each order type.
"""

import logging

from bot.client import BinanceClient

logger = logging.getLogger("trading_bot.orders")


class OrderManager:
    """
    Handles placing different order types using a BinanceClient instance.
    Add new order types here without touching the CLI or client code.
    """

    def __init__(self, client: BinanceClient):
        self.client = client

    def place_market_order(self, symbol: str, side: str, quantity: float) -> dict:
        """
        Place a MARKET order — executes immediately at the best available price.

        Args:
            symbol:   e.g. "BTCUSDT"
            side:     "BUY" or "SELL"
            quantity: How many units to trade (e.g. 0.01 BTC)

        Returns:
            Binance API response dict
        """
        logger.info(
            f"Placing MARKET order | {side} {quantity} {symbol}"
        )
        return self.client.place_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=quantity,
        )

    def place_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
    ) -> dict:
        """
        Place a LIMIT order — executes only at the specified price or better.
        Uses GTC (Good Till Cancelled) time-in-force by default.

        Args:
            symbol:   e.g. "BTCUSDT"
            side:     "BUY" or "SELL"
            quantity: How many units to trade
            price:    The limit price

        Returns:
            Binance API response dict
        """
        logger.info(
            f"Placing LIMIT order | {side} {quantity} {symbol} @ {price}"
        )
        return self.client.place_order(
            symbol=symbol,
            side=side,
            type="LIMIT",
            quantity=quantity,
            price=price,
            timeInForce="GTC",   # Keep the order open until it fills or is cancelled
        )

    # ------------------------------------------------------------------
    # BONUS: Stop-Limit order
    # ------------------------------------------------------------------

    def place_stop_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        stop_price: float,
        limit_price: float,
    ) -> dict:
        """
        Place a STOP_LIMIT order.
        The order becomes active when the market hits stop_price,
        then executes as a limit order at limit_price.

        Args:
            symbol:      e.g. "BTCUSDT"
            side:        "BUY" or "SELL"
            quantity:    How many units to trade
            stop_price:  Price that triggers the order
            limit_price: Price at which to execute once triggered

        Returns:
            Binance API response dict
        """
        logger.info(
            f"Placing STOP_LIMIT order | {side} {quantity} {symbol} "
            f"| stop={stop_price} limit={limit_price}"
        )
        return self.client.place_order(
            symbol=symbol,
            side=side,
            type="STOP",         # Binance Futures uses "STOP" for stop-limit
            quantity=quantity,
            stopPrice=stop_price,
            price=limit_price,
            timeInForce="GTC",
        )
