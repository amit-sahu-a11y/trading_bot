# Binance Futures Testnet Trading Bot

A simple Python CLI tool for placing orders on the Binance Futures Testnet (USDT-M).

---

## Features

- Place **MARKET** and **LIMIT** orders on Binance Futures Testnet
- **Bonus**: STOP_LIMIT orders also supported
- Supports BUY and SELL on any USDT-M futures pair
- Input validation with clear error messages
- Structured logging to both terminal and log file
- Clean separation of concerns: client / orders / validators / CLI layers

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Handles HTTP requests + HMAC signing
│   ├── orders.py          # Order placement logic (MARKET, LIMIT, STOP_LIMIT)
│   ├── validators.py      # Validates all user inputs before sending to API
│   └── logging_config.py  # Sets up logging to file + terminal
├── cli.py                 # Entry point — argument parsing + orchestration
├── logs/
│   ├── market_order.log   # Sample log from a MARKET order
│   └── limit_order.log    # Sample log from a LIMIT order
├── .env.example           # Template for API credentials
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Get Testnet API Credentials

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in (create an account if needed)
3. Go to **API Management** and generate a new API Key + Secret
4. Copy both values — you'll need them in the next step

### 2. Clone / Download the Project

```bash
git clone https://github.com/yourusername/trading-bot.git
cd trading-bot
```

### 3. Create a Virtual Environment (recommended)

```bash
python -m venv venv

# On macOS / Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Add Your API Credentials

```bash
cp .env.example .env
```

Then open `.env` and fill in your credentials:

```env
API_KEY=your_testnet_api_key_here
API_SECRET=your_testnet_api_secret_here
```

---

## How to Run

All commands are run from the root `trading_bot/` folder.

### Place a MARKET Order

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

### Place a LIMIT Order

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 86000
```

### Place a STOP_LIMIT Order (Bonus)

The order activates when price hits `--stop-price`, then executes as a limit at `--price`.

```bash
python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.01 --stop-price 82000 --price 81900
```

### View Help

```bash
python cli.py --help
```

---

## Example Output

```
----------------------------------------
  ORDER REQUEST SUMMARY
----------------------------------------
  Symbol       : BTCUSDT
  Side         : BUY
  Order Type   : MARKET
  Quantity     : 0.01
----------------------------------------

2025-03-13 10:14:03 [INFO] trading_bot - Submitting MARKET order...
2025-03-13 10:14:04 [INFO] trading_bot.client - Response status: 200

----------------------------------------
  ORDER RESPONSE
----------------------------------------
  Order ID     : 3851264901
  Status       : FILLED
  Symbol       : BTCUSDT
  Side         : BUY
  Type         : MARKET
  Quantity     : 0.01
  Executed Qty : 0.01
  Avg Price    : 84213.70
----------------------------------------

[SUCCESS] Order placed successfully!
```

---

## Logging

Every run appends to `logs/trading_bot.log`. The log includes:

- API request parameters (signature is omitted for security)
- Raw response body from Binance
- Any errors with full details

Sample logs from a real testnet session are included in `logs/`:
- `logs/market_order.log` — BUY MARKET 0.01 BTCUSDT
- `logs/limit_order.log` — SELL LIMIT 0.01 BTCUSDT @ 86000

---

## Validation

The bot checks all inputs before sending anything to the API:

| Input    | Rule                                      |
|----------|-------------------------------------------|
| symbol   | Letters only, e.g. BTCUSDT                |
| side     | Must be BUY or SELL                       |
| type     | Must be MARKET, LIMIT, or STOP_LIMIT      |
| quantity | Positive number                           |
| price    | Positive number (required for LIMIT/STOP) |

If validation fails, you get a clear error message — no API call is made.

---

## Assumptions

- All orders are placed on the **USDT-M Futures Testnet** only (`https://testnet.binancefuture.com`)
- Quantity precision depends on the symbol's rules on Binance — if you get a precision error, try rounding to fewer decimal places (e.g. use `0.01` not `0.0100001`)
- LIMIT orders use **GTC** (Good Till Cancelled) time-in-force by default
- Credentials are loaded from `.env` in the project root

---

## Requirements

- Python 3.10+
- `requests` — HTTP client
- `python-dotenv` — loads `.env` file
