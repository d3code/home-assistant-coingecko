"""Config flow for CoinGecko integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_SCAN_INTERVAL,
    CONF_COIN_ID,
    CONF_CURRENCY,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=60, max=86400)
        ),
        vol.Required(CONF_COIN_ID, default="bitcoin"): str,
        vol.Required(CONF_CURRENCY, default="aud"): str,
    }
)

STEP_OPTIONS_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=60, max=86400)
        ),
        vol.Required(CONF_COIN_ID, default="bitcoin"): str,
        vol.Required(CONF_CURRENCY, default="aud"): str,
    }
)


class CoinGeckoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CoinGecko."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        # Validate coin ID and currency
        coin_id = user_input[CONF_COIN_ID].strip().lower()
        currency = user_input[CONF_CURRENCY].strip().lower()
        
        if not coin_id:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
                errors={"base": "no_coin_id"},
            )
        
        if not currency:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
                errors={"base": "no_currency"},
            )

        return self.async_create_entry(
            title=f"CoinGecko {coin_id.upper()}/{currency.upper()}",
            data={
                CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                CONF_COIN_ID: coin_id,
                CONF_CURRENCY: currency,
            },
        )

    async def async_step_import(self, import_info: dict[str, Any]) -> FlowResult:
        """Handle import from configuration.yaml."""
        return await self.async_step_user(import_info)


class CoinGeckoOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for CoinGecko."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Validate coin ID and currency
            coin_id = user_input[CONF_COIN_ID].strip().lower()
            currency = user_input[CONF_CURRENCY].strip().lower()
            
            if not coin_id:
                return self.async_show_form(
                    step_id="init",
                    data_schema=STEP_OPTIONS_DATA_SCHEMA,
                    errors={"base": "no_coin_id"},
                )
            
            if not currency:
                return self.async_show_form(
                    step_id="init",
                    data_schema=STEP_OPTIONS_DATA_SCHEMA,
                    errors={"base": "no_currency"},
                )

            return self.async_create_entry(
                title="",
                data={
                    CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                    CONF_COIN_ID: coin_id,
                    CONF_CURRENCY: currency,
                },
            )

        # Pre-populate with current values
        current_data = self.config_entry.data
        schema = STEP_OPTIONS_DATA_SCHEMA.extend(
            {
                vol.Required(
                    CONF_SCAN_INTERVAL, default=current_data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
                ): vol.All(vol.Coerce(int), vol.Range(min=60, max=86400)),
                vol.Required(
                    CONF_COIN_ID,
                    default=current_data.get(CONF_COIN_ID, "bitcoin"),
                ): str,
                vol.Required(
                    CONF_CURRENCY,
                    default=current_data.get(CONF_CURRENCY, "aud"),
                ): str,
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)


