"""Adds config flow for Airly."""
import logging

import voluptuous as vol

from homeassistant.const import (
    CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME, CONF_SCAN_INTERVAL
)
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from homeassistant import config_entries, data_entry_flow

from .const import (
    DOMAIN, DEFAULT_NAME, CONF_LANGUAGE, DEFAULT_LANGUAGE, LANGUAGE_CODES
)

_LOGGER = logging.getLogger(__name__)


@callback
def configured_instances(hass):
    """Return a set of configured Airly instances."""
    return set(
        entry.data[CONF_NAME]
        for entry in hass.config_entries.async_entries(DOMAIN))


@config_entries.HANDLERS.register(DOMAIN)
class AirlyFlowHandler(data_entry_flow.FlowHandler):

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:
            if user_input[CONF_LANGUAGE] in LANGUAGE_CODES:
                if user_input[CONF_NAME] not in configured_instances(self.hass):
                    return self.async_create_entry(
                        title=user_input[CONF_NAME],
                        data=user_input,
                    )
                self._errors[CONF_NAME] = 'name_exists'
            else:
                self._errors['base'] = 'wrong_lang'

        return await self._show_config_form(
            name=DEFAULT_NAME,
            api_key='',
            latitude=self.hass.config.latitude,
            longitude=self.hass.config.longitude,
            language=DEFAULT_LANGUAGE
        )

    async def _show_config_form(self, name=None, api_key=None, latitude=None,
                                longitude=None, language=None):
        """Show the configuration form to edit location data."""
        return self.async_show_form(
            step_id='user',
            data_schema=vol.Schema({
                vol.Required(CONF_API_KEY, default=api_key): str,
                vol.Required(CONF_LATITUDE, default=latitude): cv.latitude,
                vol.Required(CONF_LONGITUDE, default=longitude): cv.longitude,
                vol.Optional(CONF_NAME, default=name): str,
                vol.Optional(CONF_LANGUAGE, default=language): str
            }),
            errors=self._errors
        )
