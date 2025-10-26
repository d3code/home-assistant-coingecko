"""The CoinGecko integration."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_BASE_URL,
    CONF_SCAN_INTERVAL,
    CONF_TRADING_PAIRS,
    COIN_MAPPINGS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    SIMPLE_PRICE_ENDPOINT,
    SUPPORTED_CURRENCIES,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up CoinGecko from a config entry."""
    coordinator = CoinGeckoDataUpdateCoordinator(hass, entry)
    
    # Try to refresh data, but don't fail setup if it doesn't work initially
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.warning("Failed to refresh data on setup: %s", err)
        # Continue with setup even if initial refresh fails

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True




async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_close()

    return unload_ok


class CoinGeckoDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching CoinGecko data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.entry = entry
        self.session: aiohttp.ClientSession | None = None
        
        scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            trading_pairs = self.entry.data.get(CONF_TRADING_PAIRS, ["BTCAUD"])
            
            # Ensure trading_pairs is a list
            if isinstance(trading_pairs, str):
                trading_pairs = [trading_pairs]
            
            if not trading_pairs:
                raise UpdateFailed("No trading pairs configured")
            
            # Create session if it doesn't exist
            if self.session is None:
                timeout = aiohttp.ClientTimeout(total=30)
                self.session = aiohttp.ClientSession(timeout=timeout)
            
            # Parse trading pairs and prepare API request
            coin_ids = []
            currencies = []
            
            for pair in trading_pairs:
                coin_symbol = pair[:3]  # First 3 characters (e.g., BTC)
                currency_symbol = pair[3:]  # Rest (e.g., AUD)
                
                # Use coin symbol directly as CoinGecko ID (lowercase)
                coin_id = coin_symbol.lower()
                
                # Convert currency to lowercase for API
                currency = currency_symbol.lower()
                
                coin_ids.append(coin_id)
                if currency not in currencies:
                    currencies.append(currency)
            
            if not coin_ids or not currencies:
                raise UpdateFailed("No valid trading pairs configured")
            
            # Make API request
            url = f"{API_BASE_URL}{SIMPLE_PRICE_ENDPOINT}"
            params = {
                "ids": ",".join(coin_ids),
                "vs_currencies": ",".join(currencies),
                "include_24hr_change": "true",
                "include_24hr_vol": "true",
                "include_market_cap": "true",
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    raise UpdateFailed(f"API request failed with status {response.status}")
                
                try:
                    data = await response.json()
                except aiohttp.ContentTypeError as err:
                    raise UpdateFailed(f"Invalid JSON response from API: {err}")
                except Exception as err:
                    raise UpdateFailed(f"Failed to parse API response: {err}")
                
                # Process and structure the data
                processed_data = {}
                for pair in trading_pairs:
                    coin_symbol = pair[:3].upper()
                    currency_symbol = pair[3:].upper()
                    coin_id = coin_symbol.lower()  # Use coin symbol directly
                    currency = currency_symbol.lower()
                    
                    if coin_id in data:
                        coin_data = data[coin_id]
                        if currency in coin_data:
                            processed_data[pair] = {
                                "price": coin_data[currency],
                                "coin_id": coin_id,
                                "currency": currency_symbol,
                                "change_24h": coin_data.get(f"{currency}_24h_change"),
                                "volume_24h": coin_data.get(f"{currency}_24h_vol"),
                                "market_cap": coin_data.get(f"{currency}_market_cap"),
                            }
                
                return processed_data
                
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with CoinGecko API: {err}")
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}")

    async def async_close(self) -> None:
        """Close the session."""
        if self.session:
            await self.session.close()
            self.session = None
