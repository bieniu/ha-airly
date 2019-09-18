"""Adds config flow for Airly."""
import async_timeout
import voluptuous as vol
from airly import Airly
from airly.exceptions import AirlyError

from homeassistant import config_entries
from homeassistant.const import (
    CONF_API_KEY,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .const import (
    _LOGGER,
    CONF_LANGUAGE,
    DEFAULT_LANGUAGE,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LANGUAGE_CODES,
    NO_AIRLY_SENSORS,
)


@callback
def configured_instances(hass):
    """Return a set of configured Airly instances."""
    return set(
        entry.data[CONF_NAME] for entry in hass.config_entries.async_entries(DOMAIN)
    )


class AirlyFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Airly."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        websession = async_get_clientsession(self.hass)

        if user_input is not None:
            if user_input[CONF_NAME] in configured_instances(self.hass):
                self._errors[CONF_NAME] = "name_exists"
            api_key_valid = await self._test_api_key(websession, user_input["api_key"])
            if not api_key_valid:
                self._errors["base"] = "auth"
            else:
                location_valid = await self._test_location(
                    websession,
                    user_input["api_key"],
                    user_input["latitude"],
                    user_input["longitude"],
                )
                if not location_valid:
                    self._errors["base"] = "wrong_location"

            if not self._errors:
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )

        return self._show_config_form(
            name=DEFAULT_NAME,
            api_key="",
            latitude=self.hass.config.latitude,
            longitude=self.hass.config.longitude,
            language=DEFAULT_LANGUAGE,
        )

    def _show_config_form(
        self, name=None, api_key=None, latitude=None, longitude=None, language=None
    ):
        """Show the configuration form to edit data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY, default=api_key): str,
                    vol.Optional(
                        CONF_LATITUDE, default=self.hass.config.latitude
                    ): cv.latitude,
                    vol.Optional(
                        CONF_LONGITUDE, default=self.hass.config.longitude
                    ): cv.longitude,
                    vol.Optional(CONF_NAME, default=name): str,
                    vol.Optional(CONF_LANGUAGE, default=language): vol.In(
                        LANGUAGE_CODES
                    ),
                }
            ),
            errors=self._errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return AirlyOptionsFlowHandler(config_entry)

    async def async_step_import(self, import_config):
        """Import a config entry from configuration.yaml."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        _LOGGER.warning(
            "Airly configuration from configuration.yaml was imported to \
            integrations. You can safely remove configuration from configuration.yaml."
        )
        return self.async_create_entry(title="configuration.yaml", data=import_config)

    async def _test_api_key(self, client, api_key):
        """Return true if api_key is valid."""

        with async_timeout.timeout(10):
            airly = Airly(api_key, client)
            measurements = airly.create_measurements_session_point(
                latitude=52.24131, longitude=20.99101
            )
            try:
                await measurements.update()
            except AirlyError:
                return False
            return True

    async def _test_location(self, client, api_key, latitude, longitude):
        """Return true if location is valid."""

        with async_timeout.timeout(10):
            airly = Airly(api_key, client)
            measurements = airly.create_measurements_session_point(
                latitude=latitude, longitude=longitude
            )

            await measurements.update()
        current = measurements.current
        if current["indexes"][0]["description"] == NO_AIRLY_SENSORS:
            return False
        return True


class AirlyOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        """Initialize Airly options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): int
                }
            ),
        )
