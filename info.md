![Screenshot](https://github.com/bieniu/ha-airly/blob/master/images/airly-ha.png?raw=true)

You can add this integration to Home Assistant via `Configuration -> Integrations -> Add -> Airly` or `configuration.yaml` file. You can add this integration several times for different locations, e.g. home and work.

## API Key
To generate `api_key` go to [Airly for developers](https://developer.airly.eu/register) page.

## Breaking change
Home Assistant 0.98+ allows disabling unnecessary entities in the entity registry. For this reason, the `monitored_conditions` argument has been removed.

## Minimal configuration
```yaml
sensor:
  - platform: airly
    api_key: !secret airly_api_key
```

{% if version_installed.replace(".","") | int < 56  %}
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
{% endif %}
{% if version_installed.replace(".","") | int > 55  %}
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
{% endif %}

## Arguments
{% if version_installed.replace(".","") | int < 56  %}
key | optional | type | default | description
-- | -- | -- | -- | --
`name` | True | string | `Airly` | name of the sensors
`api_key` | False | string | | Airly API key
`latitude` | True | string | latitude from HA config | latitude of the location to monitor
`longitude` | True | string | longitude from HA config | longitude of the location to monitor
`language` | True | string | `en` | language, available `en` and `pl`
`scan_interval` | True | integer | 600 | rate in seconds at which Airly should be polled for new data
`monitored_conditions` | True | list | all available | list of monitored conditions, available: `pm1`, `pm25`, `pm10`, `caqi`, `temperature`, `humidity`, `pressure`, `description`
{% endif %}
{% if version_installed.replace(".","") | int > 55  %}
key | optional | type | default | description
-- | -- | -- | -- | --
`name` | True | string | `Airly` | name of the sensors
`api_key` | False | string | | Airly API key
`latitude` | True | string | latitude from HA config | latitude of the location to monitor
`longitude` | True | string | longitude from HA config | longitude of the location to monitor
`language` | True | string | `en` | language, available `en` and `pl`
`scan_interval` | True | integer | 600 | rate in seconds at which Airly should be polled for new data
{% endif %}
