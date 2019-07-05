# Airly
The component collects data from Airly API to present air quality data as sensors in Home Assitant.

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
