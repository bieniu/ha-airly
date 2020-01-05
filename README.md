# Airly
[![GitHub Release][releases-shield]][releases]
[![GitHub All Releases][downloads-total-shield]][releases]
[![hacs_badge][hacs-shield]][hacs]
[![Community Forum][forum-shield]][forum]
[![Buy me a coffee][buy-me-a-coffee-shield]][buy-me-a-coffee]

## This integration is deprecated
Home Assistant 0.101 and newer includes official Airly integration.
Differences between the official and custom version:
- no configurable `scan_interval`
- no API messages in Polish language
- some sensors are represented in `air_quality` entity

These differences result from the requirements for official integrations. You can still use the custom version of component. If you want to use the official version, remove integration from Configuration -> Integrations and component files from the `/config/custom_components` folder and restart Home Assistant.

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
```

## Arguments

key | optional | type | default | description
-- | -- | -- | -- | --
`name` | True | string | `Airly` | name of the sensors
`api_key` | False | string | | Airly API key
`latitude` | True | string | latitude from HA config | latitude of the location to monitor
`longitude` | True | string | longitude from HA config | longitude of the location to monitor
`language` | True | string | `en` | language, available `en` and `pl`

[releases]: https://github.com/bieniu/ha-airly/releases
[releases-shield]: https://img.shields.io/github/release/bieniu/ha-airly.svg?style=popout
[downloads-total-shield]: https://img.shields.io/github/downloads/bieniu/ha-airly/total
[forum]: https://community.home-assistant.io/t/airly-integration-air-quality-data/124996
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=popout
[buy-me-a-coffee-shield]: https://img.shields.io/static/v1.svg?label=%20&message=Buy%20me%20a%20coffee&color=6f4e37&logo=buy%20me%20a%20coffee&logoColor=white
[buy-me-a-coffee]: https://www.buymeacoffee.com/QnLdxeaqO
[hacs-shield]: https://img.shields.io/badge/HACS-Default-orange.svg
[hacs]: https://github.com/custom-components/hacs
