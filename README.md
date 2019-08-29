# Airly
[![GitHub Release][releases-shield]][releases]
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
[![Community Forum][forum-shield]][forum]

![Screenshot](https://github.com/bieniu/ha-airly/blob/master/images/airly-ha.png?raw=true)

The integration collects data about air quality from [Airly](https://airly.eu) and present as sensors in Home Assitant.
You can add this to Home Assistant via `Configuration -> Integrations -> Add -> Airly` or `configuration.yaml` file. You can add this integration several times for different locations, e.g. home and work.

To generate `api_key` go to [Airly for developers](https://developer.airly.eu/register) page.

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
    name: 'Air Quality'
    api_key: !secret airly_api_key
    latitude: !secret latitude
    longitude: !secret longitude
    language: 'pl'
    scan_interval: 300
```

## Arguments

key | optional | type | default | description
-- | -- | -- | -- | --
`name` | True | string | `Airly` | name of the sensors
`api_key` | False | string | | Airly API key
`latitude` | True | string | latitude from HA config | latitude of the location to monitor
`longitude` | True | string | longitude from HA config | longitude of the location to monitor
`language` | True | string | `en` | language, available `en` and `pl`
`scan_interval` | True | integer | 600 | rate in seconds at which Airly should be polled for new data


[releases]: https://github.com/bieniu/ha-airly/releases
[releases-shield]: https://img.shields.io/github/release/bieniu/ha-airly.svg?style=popout
[forum]: https://community.home-assistant.io/t/airly-integration-air-quality-data/124996
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=popout
