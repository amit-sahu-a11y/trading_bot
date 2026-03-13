"""
client.py - Handles all direct communication with the Binance Futures Testnet API.

Responsibilities:
- Building and signing API requests
- Sending HTTP requests
- Basic error handling for network and API errors
"""

import hashlib
import hmac
import logging
import time
from urllib.parse import urlencode

import requests

# All requests go to the testnet, not real Binance
BASE_URL = "https://testnet.binancefuture.com"

logger = logging.getLogger("trading_bot.client")


class BinanceClient:
    """
    A simple wrapper around the Binance Futures Testnet REST API.
    Handles authentication (HMAC-SHA256 signing) automatically.
    """

    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret

        # Use a session so the API key header is always included
        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        })

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _timestamp(self) -> int:
        """Return the current time in milliseconds (required by Binance)."""
        return int(time.time() * 1000)

    def _sign(self, params: dict) -> dict:
        """
        Add an HMAC-SHA256 signature to the params dict.
        Binance requires every authenticated request to be signed.
        """
        # Build a URL-encoded query string from the params
        query_string = urlencode(params)

        # Create the signature
        signature = hmac.new(
            key=self.api_secret.encode("utf-8"),
            msg=query_string.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

        params["signature"] = signature
        return params

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    def ping(self) -> bool:
        """
        Quick connectivity check. Returns True if the testnet is reachable.
        """
        url = f"{BASE_URL}/fapi/v1/ping"
        try:
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            logger.info("Ping successful — testnet is reachable.")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Ping failed: {e}")
            return False

    def place_order(self, **kwargs) -> dict:
        """
        Place an order on Binance Futures Testnet.

        All keyword arguments are passed directly as order parameters.
        Required by Binance: symbol, side, type, quantity (and price for LIMIT).

        Returns the JSON response from Binance as a Python dict.
        Raises an exception if the request fails.
        """
        url = f"{BASE_URL}/fapi/v1/order"

        # Add timestamp, then sign the full params dict
        params = {**kwargs, "timestamp": self._timestamp()}
        params = self._sign(params)

        logger.info(f"Sending order request → {url}")
        # Log params but hide the signature for cleanliness
        loggable = {k: v for k, v in params.items() if k != "signature"}
        logger.info(f"Order params: {loggable}")

        try:
            response = self.session.post(url, data=params, timeout=10)

            # Log the raw response before raising any error
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response body: {response.text}")

            # If Binance returned a 4xx / 5xx, raise an HTTPError
            response.raise_for_status()

            return response.json()

        except requests.exceptions.HTTPError:
            # Binance puts error details in the JSON body
            try:
                error_body = response.json()
                msg = error_body.get("msg", response.text)
                code = error_body.get("code", response.status_code)
                raise RuntimeError(
                    f"Binance API error (code {code}): {msg}"
                )
            except ValueError:
                raise RuntimeError(
                    f"HTTP {response.status_code}: {response.text}"
                )

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise RuntimeError(
                "Could not connect to Binance Testnet. "
                "Check your internet connection."
            ) from e

        except requests.exceptions.Timeout:
            logger.error("Request timed out.")
            raise RuntimeError(
                "Request to Binance Testnet timed out. Try again."
            )
