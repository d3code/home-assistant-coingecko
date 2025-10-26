"""Sensor platform for CoinGecko integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_COIN_ID, CONF_CURRENCY

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up CoinGecko sensor entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    coin_id = config_entry.data.get(CONF_COIN_ID, "bitcoin")
    currency = config_entry.data.get(CONF_CURRENCY, "aud")
    
    # Create a single sensor for the coin/currency pair
    trading_pair = f"{coin_id.upper()}{currency.upper()}"
    entity = CoinGeckoSensor(coordinator, trading_pair)
    
    async_add_entities([entity])


class CoinGeckoSensor(CoordinatorEntity, SensorEntity):
    """Representation of a CoinGecko sensor."""

    def __init__(self, coordinator, trading_pair: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._trading_pair = trading_pair
        self._attr_name = f"CoinGecko {trading_pair}"
        self._attr_unique_id = f"coingecko_{trading_pair.lower()}"
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_attribution = "Data provided by CoinGecko"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if not self.coordinator.data or self._trading_pair not in self.coordinator.data:
            return None
        
        data = self.coordinator.data[self._trading_pair]
        return data.get("price")

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement."""
        if not self.coordinator.data or self._trading_pair not in self.coordinator.data:
            return None
        
        data = self.coordinator.data[self._trading_pair]
        return data.get("currency")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data or self._trading_pair not in self.coordinator.data:
            return {}
        
        data = self.coordinator.data[self._trading_pair]
        
        attributes = {
            "coin_id": data.get("coin_id"),
            "currency": data.get("currency"),
            "last_updated": self.coordinator.last_update_success.isoformat() if hasattr(self.coordinator.last_update_success, 'isoformat') else None,
        }
        
        # Add optional attributes if available
        if change_24h := data.get("change_24h"):
            attributes["change_24h"] = round(change_24h, 2)
        
        if volume_24h := data.get("volume_24h"):
            attributes["volume_24h"] = volume_24h
        
        if market_cap := data.get("market_cap"):
            attributes["market_cap"] = market_cap
        
        return attributes
