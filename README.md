# CoinGecko Home Assistant Integration

A Home Assistant custom component that integrates with the CoinGecko API to provide cryptocurrency price sensors.

## Features

- **Real-time cryptocurrency prices** from CoinGecko's free API
- **Configurable trading pairs** (e.g., BTCAUD, ETHUSD, DOGEUSD)
- **Adjustable polling interval** (default: 15 minutes)
- **UI-based configuration** - no YAML required
- **Reconfigurable** - modify settings after installation
- **Multiple currencies supported** (USD, EUR, AUD, JPY, etc.)
- **Additional data** available as sensor attributes (24h change, volume, market cap)

## Installation

### Via HACS (Recommended)

1. Add this repository to HACS:
   - Go to HACS → Integrations
   - Click the three dots menu → Custom repositories
   - Add repository: `https://github.com/lukesands/home-assistant-coingecko`
   - Category: Integration
2. Install "CoinGecko" from HACS
3. Restart Home Assistant
4. Go to Settings → Devices & Services → Add Integration
5. Search for "CoinGecko" and follow the setup wizard

### Manual Installation

1. Download the latest release
2. Copy the `custom_components/coingecko` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant
4. Go to Settings → Devices & Services → Add Integration
5. Search for "CoinGecko" and follow the setup wizard

## Configuration

### Initial Setup

1. **Trading Pairs**: Enter comma-separated trading pairs (e.g., `BTCAUD,ETHUSD,DOGEUSD`)
2. **Update Interval**: Set how often to fetch new data (60-86400 seconds, default: 900)

### Trading Pair Format

Trading pairs should be in the format `COINCURRENCY` where:
- `COIN` is the cryptocurrency symbol (3+ characters, e.g., BTC, ETH, DOGE)
- `CURRENCY` is the target currency (3+ characters, e.g., USD, AUD, EUR)

Examples:
- `BTCAUD` - Bitcoin to Australian Dollar
- `ETHUSD` - Ethereum to US Dollar
- `DOGEUSD` - Dogecoin to US Dollar
- `ADAEUR` - Cardano to Euro

### Supported Cryptocurrencies

The integration supports 100+ cryptocurrencies including:
- Bitcoin (BTC)
- Ethereum (ETH)
- Cardano (ADA)
- Polkadot (DOT)
- Chainlink (LINK)
- Litecoin (LTC)
- And many more...

### Supported Currencies

The integration supports 50+ fiat currencies including:
- USD, EUR, GBP, JPY
- AUD, CAD, CHF, CNY
- HKD, NZD, SEK, NOK
- And many more...

## Usage

After configuration, you'll have sensor entities for each trading pair:

- **Entity ID**: `sensor.coingecko_btc_aud`
- **Name**: `CoinGecko BTCAUD`
- **State**: Current price (e.g., 45,230.50)
- **Unit**: Currency code (e.g., AUD)

### Sensor Attributes

Each sensor includes additional attributes:

- `coin_id`: CoinGecko's internal coin identifier
- `currency`: Target currency code
- `last_updated`: Timestamp of last update
- `change_24h`: 24-hour price change percentage
- `volume_24h`: 24-hour trading volume
- `market_cap`: Market capitalization

### Example Automations

```yaml
# Alert when Bitcoin price drops below $40,000 AUD
automation:
  - alias: "Bitcoin Price Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.coingecko_btc_aud
        below: 40000
    action:
      - service: notify.mobile_app_your_phone
        data:
          message: "Bitcoin price dropped below $40,000 AUD!"

# Log Ethereum price every hour
automation:
  - alias: "Log Ethereum Price"
    trigger:
      - platform: time_pattern
        minutes: 0
    action:
      - service: system_log.write
        data:
          message: "ETH Price: {{ states('sensor.coingecko_eth_usd') }} USD"
```

## Reconfiguration

To modify your settings after initial setup:

1. Go to Settings → Devices & Services
2. Find "CoinGecko" integration
3. Click the three dots menu → Configure
4. Modify trading pairs or update interval
5. Click Submit

## Troubleshooting

### Common Issues

**"No valid trading pairs configured"**
- Ensure trading pairs are in correct format (e.g., BTCAUD, not BTC-AUD)
- Check that coin symbols are supported
- Verify currency codes are supported

**"API request failed"**
- Check your internet connection
- CoinGecko API might be temporarily unavailable
- Check Home Assistant logs for detailed error messages

**Sensors not updating**
- Verify the update interval is reasonable (not too frequent)
- Check Home Assistant logs for API errors
- Ensure trading pairs are valid

### Logs

Enable debug logging to troubleshoot issues:

```yaml
logger:
  logs:
    custom_components.coingecko: debug
```

## API Information

This integration uses CoinGecko's free public API:
- **Base URL**: `https://api.coingecko.com/api/v3/`
- **Rate Limits**: 10-50 calls/minute (varies)
- **No API key required** for basic usage
- **Data Source**: CoinGecko aggregates data from multiple exchanges

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This integration is not affiliated with CoinGecko. Cryptocurrency prices are provided for informational purposes only. Always verify prices from multiple sources before making financial decisions.
