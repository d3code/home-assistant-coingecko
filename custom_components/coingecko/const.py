"""Constants for the CoinGecko integration."""

DOMAIN = "coingecko"
DEFAULT_SCAN_INTERVAL = 900  # 15 minutes in seconds

# API Configuration
API_BASE_URL = "https://api.coingecko.com/api/v3"
SIMPLE_PRICE_ENDPOINT = "/simple/price"

# Configuration keys
CONF_SCAN_INTERVAL = "scan_interval"
CONF_COIN_ID = "coin_id"
CONF_CURRENCY = "currency"
