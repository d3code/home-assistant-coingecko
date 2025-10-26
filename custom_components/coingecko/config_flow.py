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
    CONF_TRADING_PAIRS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=60, max=86400)
        ),
        vol.Required(CONF_TRADING_PAIRS, default="BTCAUD"): str,
    }
)

STEP_OPTIONS_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=60, max=86400)
        ),
        vol.Required(CONF_TRADING_PAIRS, default="BTCAUD"): str,
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

        # Validate trading pairs format
        trading_pairs_str = user_input[CONF_TRADING_PAIRS]
        if not trading_pairs_str or not trading_pairs_str.strip():
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
                errors={"base": "no_trading_pairs"},
            )

        # Parse trading pairs
        try:
            trading_pairs = [pair.strip().upper() for pair in trading_pairs_str.split(",") if pair.strip()]
        except Exception:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
                errors={"base": "invalid_pair_format"},
            )

        if not trading_pairs:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
                errors={"base": "no_trading_pairs"},
            )

        # Validate trading pair format (should be like BTCAUD, ETHUSD, etc.)
        for pair in trading_pairs:
            if len(pair) < 6 or not pair.isalpha():
                return self.async_show_form(
                    step_id="user",
                    data_schema=STEP_USER_DATA_SCHEMA,
                    errors={"base": "invalid_pair_format"},
                )

        return self.async_create_entry(
            title="CoinGecko",
            data={
                CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                CONF_TRADING_PAIRS: trading_pairs,
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
            # Validate trading pairs format
            trading_pairs_str = user_input[CONF_TRADING_PAIRS]
            if not trading_pairs_str or not trading_pairs_str.strip():
                return self.async_show_form(
                    step_id="init",
                    data_schema=STEP_OPTIONS_DATA_SCHEMA,
                    errors={"base": "no_trading_pairs"},
                )

            # Parse trading pairs
            try:
                trading_pairs = [pair.strip().upper() for pair in trading_pairs_str.split(",") if pair.strip()]
            except Exception:
                return self.async_show_form(
                    step_id="init",
                    data_schema=STEP_OPTIONS_DATA_SCHEMA,
                    errors={"base": "invalid_pair_format"},
                )

            if not trading_pairs:
                return self.async_show_form(
                    step_id="init",
                    data_schema=STEP_OPTIONS_DATA_SCHEMA,
                    errors={"base": "no_trading_pairs"},
                )

            # Validate trading pair format
            for pair in trading_pairs:
                if len(pair) < 6 or not pair.isalpha():
                    return self.async_show_form(
                        step_id="init",
                        data_schema=STEP_OPTIONS_DATA_SCHEMA,
                        errors={"base": "invalid_pair_format"},
                    )

            return self.async_create_entry(
                title="",
                data={
                    CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                    CONF_TRADING_PAIRS: trading_pairs,
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
                    CONF_TRADING_PAIRS,
                    default=",".join(current_data.get(CONF_TRADING_PAIRS, ["BTCAUD"])),
                ): str,
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)


# Register the options flow handler
@config_entries.HANDLERS.register(DOMAIN)
class CoinGeckoOptionsFlowHandler(config_entries.OptionsFlowHandler):
    """Handle options flow for CoinGecko."""
    
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow handler."""
        super().__init__(config_entry)
        self._options_flow = CoinGeckoOptionsFlow(config_entry)
    
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""
        return await self._options_flow.async_step_init(user_input)


