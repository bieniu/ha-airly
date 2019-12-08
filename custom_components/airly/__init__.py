"""The Airly component."""
from asyncio import TimeoutError
from datetime import timedelta
import logging

from aiohttp.client_exceptions import ClientConnectorError
from airly import Airly
from airly.exceptions import AirlyError
from async_timeout import timeout

from homeassistant.const import (
    CONF_API_KEY,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_SCAN_INTERVAL,
)
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import Throttle

from .const import (
    ATTR_CAQI,
    ATTR_CAQI_ADVICE,
    ATTR_CAQI_DESCRIPTION,
    ATTR_CAQI_LEVEL,
    CONF_LANGUAGE,
    DATA_CLIENT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    NO_AIRLY_SENSORS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up configured Airly."""
    hass.data[DOMAIN] = {}
    hass.data[DOMAIN][DATA_CLIENT] = {}
    return True


async def async_setup_entry(hass, config_entry):
    """Set up Airly as config entry."""
    api_key = config_entry.data[CONF_API_KEY]
    latitude = config_entry.data[CONF_LATITUDE]
    longitude = config_entry.data[CONF_LONGITUDE]
    language = config_entry.data[CONF_LANGUAGE]
    try:
        scan_interval = config_entry.options[CONF_SCAN_INTERVAL]
    except KeyError:
        scan_interval = DEFAULT_SCAN_INTERVAL

    websession = async_get_clientsession(hass)

    airly = AirlyData(
        websession,
        api_key,
        latitude,
        longitude,
        language,
        scan_interval=timedelta(seconds=scan_interval),
    )

    await airly.async_update()

    if not airly.data:
        raise ConfigEntryNotReady()

    hass.data[DOMAIN][DATA_CLIENT][config_entry.entry_id] = airly

    config_entry.add_update_listener(update_listener)
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config_entry, "sensor")
    )
    return True


async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")
    return True


async def update_listener(hass, entry):
    """Update listener."""
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.async_add_job(hass.config_entries.async_forward_entry_setup(entry, "sensor"))


class AirlyData:
    """Define an object to hold sensor data."""

    def __init__(self, session, api_key, latitude, longitude, language, **kwargs):
        """Initialize."""
        self.latitude = latitude
        self.longitude = longitude
        self.language = language
        self.airly = Airly(api_key, session, language=self.language)
        self.data = {}

        self.async_update = Throttle(kwargs[CONF_SCAN_INTERVAL])(self._async_update)

    async def _async_update(self):
        """Update Airly data."""
        try:
            with timeout(20):
                measurements = self.airly.create_measurements_session_point(
                    self.latitude, self.longitude
                )
                await measurements.update()

            values = measurements.current["values"]
            standards = measurements.current["standards"]
            index = measurements.current["indexes"][0]

            if index["description"] == NO_AIRLY_SENSORS[self.language]:
                _LOGGER.error("Can't retrieve data: no Airly sensors in this area")
                return
            for value in values:
                self.data[value["name"]] = value["value"]
            for standard in standards:
                self.data[f"{standard['pollutant']}_LIMIT"] = standard["limit"]
                self.data[f"{standard['pollutant']}_PERCENT"] = standard["percent"]
            self.data[ATTR_CAQI] = index["value"]
            self.data[ATTR_CAQI_LEVEL] = index["level"].lower().replace("_", " ")
            self.data[ATTR_CAQI_DESCRIPTION] = index["description"]
            self.data[ATTR_CAQI_ADVICE] = index["advice"]
            _LOGGER.debug("Data retrieved from Airly")
        except TimeoutError:
            _LOGGER.error("Asyncio Timeout Error")
        except (ValueError, AirlyError, ClientConnectorError) as error:
            _LOGGER.error(error)
            self.data = {}
