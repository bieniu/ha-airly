"""The Airly component."""
import asyncio
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
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    ATTR_CAQI,
    ATTR_CAQI_ADVICE,
    ATTR_CAQI_DESCRIPTION,
    ATTR_CAQI_LEVEL,
    CONF_LANGUAGE,
    CONF_USE_NEAREST,
    COORDINATOR,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    NO_AIRLY_SENSORS,
    UNDO_UPDATE_LISTENER,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """"Old way of setting up Airly integrations."""
    return True


async def async_setup_entry(hass, config_entry):
    """Set up Airly as config entry."""
    api_key = config_entry.data[CONF_API_KEY]
    latitude = config_entry.data[CONF_LATITUDE]
    longitude = config_entry.data[CONF_LONGITUDE]
    language = config_entry.data[CONF_LANGUAGE]
    use_nearest = config_entry.data.get(CONF_USE_NEAREST, False)

    # For backwards compat, set unique ID
    if config_entry.unique_id is None:
        hass.config_entries.async_update_entry(
            config_entry, unique_id=f"{latitude}-{longitude}"
        )

    try:
        scan_interval = timedelta(seconds=config_entry.options[CONF_SCAN_INTERVAL])
    except KeyError:
        scan_interval = timedelta(seconds=DEFAULT_SCAN_INTERVAL)

    websession = async_get_clientsession(hass)

    coordinator = AirlyDataUpdateCoordinator(
        hass,
        websession,
        api_key,
        latitude,
        longitude,
        language,
        scan_interval,
        use_nearest,
    )
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    undo_listener = config_entry.add_update_listener(update_listener)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = {
        COORDINATOR: coordinator,
        UNDO_UPDATE_LISTENER: undo_listener,
    }

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, component)
        )

    return True


async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(config_entry, component)
                for component in PLATFORMS
            ]
        )
    )

    hass.data[DOMAIN][config_entry.entry_id][UNDO_UPDATE_LISTENER]()

    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok


async def update_listener(hass, config_entry):
    """Update listener."""
    await hass.config_entries.async_reload(config_entry.entry_id)


class AirlyDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Airly data API."""

    def __init__(
        self,
        hass,
        session,
        api_key,
        latitude,
        longitude,
        language,
        scan_interval,
        use_nearest,
    ):
        """Initialize."""
        self.airly = Airly(api_key, session, language=language)
        self.language = language
        self.latitude = latitude
        self.longitude = longitude
        self.use_nearest = use_nearest

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=scan_interval)

    async def _async_update_data(self):
        """Update data via library."""
        data = {}
        if self.use_nearest:
            measurements = self.airly.create_measurements_session_nearest(
                self.latitude, self.longitude, max_distance_km=5
            )
        else:
            measurements = self.airly.create_measurements_session_point(
                self.latitude, self.longitude
            )
        with timeout(20):
            try:
                await measurements.update()
            except (AirlyError, ClientConnectorError) as error:
                raise UpdateFailed(error) from error

        values = measurements.current["values"]
        index = measurements.current["indexes"][0]
        standards = measurements.current["standards"]

        if index["description"] == NO_AIRLY_SENSORS:
            raise UpdateFailed("Can't retrieve data: no Airly sensors in this area")
        for value in values:
            data[value["name"]] = value["value"]
        for standard in standards:
            data[f"{standard['pollutant']}_LIMIT"] = standard["limit"]
            data[f"{standard['pollutant']}_PERCENT"] = standard["percent"]
        data[ATTR_CAQI] = index["value"]
        data[ATTR_CAQI_LEVEL] = index["level"].lower().replace("_", " ")
        data[ATTR_CAQI_DESCRIPTION] = index["description"]
        data[ATTR_CAQI_ADVICE] = index["advice"]
        return data
