from datetime import timedelta
import logging
import requests

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_MONITORED_CONDITIONS, CONF_NAME, CONF_LATITUDE, CONF_LONGITUDE,
    CONF_API_KEY, CONF_SCAN_INTERVAL, TEMP_CELSIUS, DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_TEMPERATURE, DEVICE_CLASS_PRESSURE, PRESSURE_HPA, HTTP_OK,
    CONTENT_TYPE_JSON, ATTR_ATTRIBUTION
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'Airly'
DEFAULT_MONITORED_CONDITIONS = ['pm1', 'pm25', 'pm10']
DEFAULT_ATTRIBUTION = "Data provided by Airly"
DEFAULT_SCAN_INTERVAL = timedelta(minutes=10)

LABEL_TEMPERATURE = 'Temperature'
LABEL_HUMIDITY = 'Humidity'
LABEL_PRESSURE = 'Pressure'
LABEL_PM1 = 'PM1'
LABEL_PM25 = 'PM2.5'
LABEL_PM10 = 'PM10'
LABEL_CAQI = 'CAQI'
VOLUME_MICROGRAMS_PER_CUBIC_METER = 'µg/m³'
HUMI_PERCENT ='%'

ATTR_LIMIT = 'limit'
ATTR_PERCENT = 'percent'
ATTR_PM1 = 'pm1'
ATTR_PM25 = 'pm25'
ATTR_PM25_LIMIT = 'pm25_limit'
ATTR_PM25_PERCENT = 'pm25_percent'
ATTR_PM10 = 'pm10'
ATTR_PM10_LIMIT = 'pm10_limit'
ATTR_PM10_PERCENT = 'pm10_percent'
ATTR_TEMPERATURE = 'temperature'
ATTR_HUMIDITY = 'humidity'
ATTR_PRESSURE = 'pressure'
ATTR_CAQI = 'caqi'
ATTR_CAQI_LEVEL = 'level'

ATTR_NO_SENSOR_AVAILABLE = ("There are no Airly sensors in this area yet.")

SENSOR_TYPES = {
    ATTR_PM1: [LABEL_PM1, VOLUME_MICROGRAMS_PER_CUBIC_METER, 'mdi:blur'],
    ATTR_PM25: [LABEL_PM25, VOLUME_MICROGRAMS_PER_CUBIC_METER, 'mdi:blur'],
    ATTR_PM10: [LABEL_PM10, VOLUME_MICROGRAMS_PER_CUBIC_METER, 'mdi:blur'],
    ATTR_PRESSURE: [LABEL_PRESSURE, PRESSURE_HPA, 'mdi:gauge'],
    ATTR_HUMIDITY: [LABEL_HUMIDITY, HUMI_PERCENT, 'mdi:water-percent'],
    ATTR_TEMPERATURE: [LABEL_TEMPERATURE, TEMP_CELSIUS, 'mdi:thermometer'],
    ATTR_CAQI: [LABEL_CAQI, None, 'mdi:chart-line']
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY, None): cv.string,
    vol.Inclusive(
        CONF_LATITUDE,
        'coordinates',
        'Latitude and longitude must exist together'
    ): cv.latitude,
    vol.Inclusive(
        CONF_LONGITUDE,
        'coordinates',
        'Latitude and longitude must exist together'
    ): cv.longitude,
    vol.Optional(CONF_MONITORED_CONDITIONS,
                 default=DEFAULT_MONITORED_CONDITIONS):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL):
        cv.time_period
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Configure the platform and add the sensors."""

    name = config.get(CONF_NAME)
    token = config.get(CONF_API_KEY)
    latitude = config.get(CONF_LATITUDE, hass.config.latitude)
    longitude = config.get(CONF_LONGITUDE, hass.config.longitude)
    _LOGGER.debug("Using latitude and longitude: %s, %s", latitude, longitude)
    scan_interval = config[CONF_SCAN_INTERVAL]
    sensors = []
    for variable in config[CONF_MONITORED_CONDITIONS]:
        sensors.append(AirlySensor(name, variable, latitude, longitude, token))
    add_entities(sensors, True)


class AirlySensor(Entity):
    """Define an Airly sensor."""

    def __init__(self, name, type, latitude, longitude, token):
        """Initialize."""
        self._name = name
        self._latitude = latitude
        self._longitude = longitude
        self._type = type
        self._token = token
        self.data = None
        self._state = None
        self._attrs = {ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION}
        self._device_class = None
        self._icon = None
        self._unit_of_measurement = None

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        if self._type == ATTR_CAQI:
            self._attrs[ATTR_CAQI_LEVEL] = self.data[ATTR_CAQI_LEVEL]
        if self._type == ATTR_PM25:
            self._attrs[ATTR_LIMIT] = self.data[ATTR_PM25_LIMIT]
            self._attrs[ATTR_PERCENT] = round(self.data[ATTR_PM25_PERCENT])
        if self._type == ATTR_PM10:
            self._attrs[ATTR_LIMIT] = self.data[ATTR_PM10_LIMIT]
            self._attrs[ATTR_PERCENT] = round(self.data[ATTR_PM10_PERCENT])
        return self._attrs

    @property
    def name(self):
        """Return the name."""
        return '{} {}'.format(self._name, SENSOR_TYPES[self._type][0])

    @property
    def icon(self):
        """Return the icon."""
        if self._type == ATTR_CAQI:
            if self._state <= 25:
                return 'mdi:emoticon-excited'
            elif self._state <= 50:
                return 'mdi:emoticon-happy'
            elif self._state <= 75:
                return 'mdi:emoticon-neutral'
            elif self._state <= 100:
                return 'mdi:emoticon-sad'
            elif self._state > 100:
                return 'mdi:emoticon-dead'
        return SENSOR_TYPES[self._type][2]

    @property
    def device_class(self):
        """Return the device_class."""
        if self._type == ATTR_TEMPERATURE:
            return DEVICE_CLASS_TEMPERATURE
        elif self._type == ATTR_HUMIDITY:
            return DEVICE_CLASS_HUMIDITY
        elif self._type == ATTR_PRESSURE:
            return DEVICE_CLASS_PRESSURE
        else:
            return self._device_class

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return '{}-{}-{}'.format(self._latitude, self._longitude, self._type)

    @property
    def state(self):
        """Return the state."""
        if self.data is not None:
            self._state = self.data[self._type]
        if self._type in [ATTR_PM1, ATTR_PM25, ATTR_PM10, ATTR_PRESSURE,
                          ATTR_CAQI]:
            self._state = round(self._state)
        if self._type in [ATTR_TEMPERATURE, ATTR_HUMIDITY]:
            self._state = round(self._state, 1)
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return SENSOR_TYPES[self._type][1]

    def update(self):
        """Get the data from Airly."""
        url = 'https://airapi.airly.eu/v2/measurements/point' \
              '?lat={}&lng={}&maxDistanceKM=2'.format(self._latitude,
                                                      self._longitude)
        headers = {'Accept': CONTENT_TYPE_JSON, 'apikey': self._token}
        request = requests.get(url, headers=headers)
        _LOGGER.debug("New data retrieved: %s", request.status_code)
        if request.status_code == HTTP_OK and request.content.__len__() > 0:
            if (request.json()['current']['indexes'][0]['description'] ==
                    ATTR_NO_SENSOR_AVAILABLE):
                _LOGGER.error(ATTR_NO_SENSOR_AVAILABLE)
            else:
                self.get_data(request.json())

    def get_data(self, data):
        """
        Return a new state based on the type.
        """
        self.data = {}
        self.data[ATTR_PM1] = data['current']['values'][0]['value']
        self.data[ATTR_PM25] = data['current']['values'][1]['value']
        self.data[ATTR_PM25_LIMIT] = data['current']['standards'][0]['limit']
        self.data[ATTR_PM25_PERCENT] = (data['current']['standards'][0]
                                        ['percent'])
        self.data[ATTR_PM10] = data['current']['values'][2]['value']
        self.data[ATTR_PM10_LIMIT] = data['current']['standards'][1]['limit']
        self.data[ATTR_PM10_PERCENT] = (data['current']['standards'][1]
                                        ['percent'])
        self.data[ATTR_PRESSURE] = data['current']['values'][3]['value']
        self.data[ATTR_HUMIDITY] = data['current']['values'][4]['value']
        self.data[ATTR_TEMPERATURE] = data['current']['values'][5]['value']
        self.data[ATTR_CAQI] = data['current']['indexes'][0]['value']
        self.data[ATTR_CAQI_LEVEL] = (data['current']['indexes'][0]
                                      ['level'].lower().replace('_', ' '))





