"""Adds config flow for Airly."""
import aiohttp
import voluptuous as vol

from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from homeassistant import config_entries, data_entry_flow

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    CONF_LANGUAGE,
    DEFAULT_LANGUAGE,
    LANGUAGE_CODES,
    NO_AIRLY_SENSORS,
)


@callback
def configured_instances(hass):
    """Return a set of configured Airly instances."""
    return set(
        entry.data[CONF_NAME] for entry in hass.config_entries.async_entries(DOMAIN)
    )


@config_entries.HANDLERS.register(DOMAIN)
class AirlyFlowHandler(data_entry_flow.FlowHandler):
    """Config flow for Airly."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:
            api_key_valid = await self._test_api_key(user_input["api_key"])
            if api_key_valid:
                location_valid = await self._test_location(
                    user_input["api_key"],
                    user_input["latitude"],
                    user_input["longitude"],
                )
                if location_valid:
                    if user_input[CONF_LANGUAGE] in LANGUAGE_CODES:
                        if user_input[CONF_NAME] not in configured_instances(self.hass):
                            return self.async_create_entry(
                                title=user_input[CONF_NAME], data=user_input
                            )
                        self._errors[CONF_NAME] = "name_exists"
                    else:
                        self._errors["base"] = "wrong_lang"
                else:
                    self._errors["base"] = "wrong_location"
            else:
                self._errors["base"] = "auth"

        return await self._show_config_form(
            name=DEFAULT_NAME,
            api_key="",
            latitude=self.hass.config.latitude,
            longitude=self.hass.config.longitude,
            language=DEFAULT_LANGUAGE,
        )

    async def _show_config_form(
        self, name=None, api_key=None, latitude=None, longitude=None, language=None
    ):
        """Show the configuration form to edit data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY, default=api_key): str,
                    vol.Required(CONF_LATITUDE, default=latitude): cv.latitude,
                    vol.Required(CONF_LONGITUDE, default=longitude): cv.longitude,
                    vol.Optional(CONF_NAME, default=name): str,
                    vol.Optional(CONF_LANGUAGE, default=language): str,
                }
            ),
            errors=self._errors,
        )

    async def _test_api_key(self, api_key):
        """Return true if api_key is valid."""
        from airly import Airly
        from airly.exceptions import AirlyError

        async with aiohttp.ClientSession() as http_session:
            try:
                airly = Airly(api_key, http_session)
                measurements = airly.create_measurements_session_point(
                    latitude=52.24131, longitude=20.99101
                )

                await measurements.update()
                return True
            except AirlyError:
                pass
            return False

    async def _test_location(self, api_key, latitude, longitude):
        """Return true if location is valid."""
        from airly import Airly

        async with aiohttp.ClientSession() as http_session:
            airly = Airly(api_key, http_session)
            measurements = airly.create_measurements_session_point(
                latitude=latitude, longitude=longitude
            )

            await measurements.update()
            current = measurements.current
            if current["indexes"][0]["description"] == NO_AIRLY_SENSORS:
                return False
            return True
