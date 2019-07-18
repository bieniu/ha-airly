# Airly
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub Release](https://img.shields.io/github/release/bieniu/ha-airly.svg?style=popout)][releases]

![Screenshot](https://github.com/bieniu/ha-airly/blob/master/images/airly-ha.png?raw=true)

The component collects data about air quality from [Airly](https://airly.eu) and present as sensors in Home Assitant.

To generate `api_key` go to [Airly for developers](https://developer.airly.eu/register) page.
)
## Minimal configuration
```yaml
sensor:
  - platform: airly
    api_key: !secret airly_api_key
```

## Custom configuration example
```yaml
sensor:
  - platform: airly
    api_key: !secret airly_api_key
    latitude: !secret latitude
    longitude: !secret longitude
    language: 'pl'
    scan_interval: 300
    monitored_conditions:
      - pm1
      - pm25
      - pm10
      - caqi
      - temperature
      - pressure
      - humidity
      - description
```

## Arguments

key | optional | type | default | description
-- | -- | -- | -- | --
`api_key` | False | string | | Airly API key
`latitude` | True | string | latitude from HA config | latitude of the location to monitor
`longitude` | True | string | longitude from HA config | longitude of the location to monitor
`language` | True | string | `en` | language, available `en` and `pl`
`scan_interval` | True | integer | 600 | rate in seconds at which Airly should be polled for new data
`monitored_conditions` | True | list | `pm1, pm25, pm10` | list of monitored conditions, available: `pm1`, `pm25`, `pm10`, `caqi`, `temperature`, `humidity`, `pressure`, `description`

[releases]: https://github.com/bieniu/ha-airly/releases
