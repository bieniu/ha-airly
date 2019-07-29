"""Adds config flow for HACS."""
import voluptuous as vol

from homeassistant.const import (
    CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME, CONF_SCAN_INTERVAL
)
import homeassistant.helpers.config_validation as cv
from homeassistant import config_entries, data_entry_flow


DOMAIN = 'airly'
DEFAULT_NAME = 'Airly'

@config_entries.HANDLERS.register(DOMAIN)
class AirlyFlowHandler(data_entry_flow.FlowHandler):

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input={}):
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:
            if user_input[CONF_NAME] not in \
                    self.hass.config_entries.async_entries(DOMAIN):
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input,
                )

            self._errors[CONF_NAME] = 'name_exists'

        return await self._show_config_form(
            name=DEFAULT_NAME,
            api_key = 'xxxxxxxxxxxxxxxxxxxx',
            latitude=self.hass.config.latitude,
            longitude=self.hass.config.longitude
            )

    async def _show_config_form(self, name=None, api_key=None, latitude=None, longitude=None):
        """Show the configuration form to edit location data."""

        return self.async_show_form(
            step_id='user',
            data_schema=vol.Schema({
                vol.Required(CONF_API_KEY, default=api_key): str,
                vol.Required(CONF_LATITUDE, default=latitude): cv.latitude,
                vol.Required(CONF_LONGITUDE, default=longitude): cv.longitude,
                vol.Optional(CONF_NAME, default=name): str
            }),
            errors=self._errors
        )


        # if user_input is not None:
        #     if CONF_NAME in user_input:
        #         name = user_input[CONF_NAME]
        #     if CONF_API_KEY in user_input:
        #         api_key = user_input[CONF_API_KEY]
        #     if CONF_LATITUDE in user_input:
        #         latitude = user_input[CONF_LATITUDE]
        #     if CONF_LONGITUDE in user_input:
        #         longitude = user_input[CONF_LONGITUDE]
        #     if CONF_LANGUAGE in user_input:
        #         latitude = user_input[CONF_LANGUAGE]
        #     # if CONF_SCAN_INTERVAL in user_input:
        #     #     scan_interval = user_input[CONF_SCAN_INTERVAL]

        # data_schema = {
        #     vol.Required(CONF_API_KEY, default=api_key): cv.string,
        #     vol.Inclusive(
        #         CONF_LATITUDE,
        #         'coordinates',
        #         'Latitude and longitude must exist together',
        #         default=latitude
        #     ): cv.latitude,
        #     vol.Inclusive(
        #         CONF_LONGITUDE,
        #         'coordinates',
        #         'Latitude and longitude must exist together',
        #         default=longitude
        #     ): cv.longitude,
        #     vol.Optional(CONF_LANGUAGE,
        #                 default=language): vol.In(LANGUAGE_CODES),
        #     # vol.Optional(CONF_MONITORED_CONDITIONS,
        #     #             default=DEFAULT_MONITORED_CONDITIONS):
        #     #     vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
        #     vol.Optional(CONF_NAME, default=name): cv.string,
        #     # vol.Optional(CONF_SCAN_INTERVAL, default=scan_interval):
        #     #     cv.time_period
        # }

    #     return self.async_show_form(
    #         step_id='user', data_schema=vol.Schema(data_schema))

    # async def async_step_import(self, user_input):
    #     """Import a config entry.
    #     Special type of import, we're not actually going to store any data.
    #     Instead, we're going to rely on the values that are in config file.
    #     """

    #     return self.async_create_entry(title='configuration.yaml', data={})