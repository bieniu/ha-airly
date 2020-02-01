[![Community Forum][forum-shield]][forum]  [![Buy me a coffee][buy-me-a-coffee-shield]][buy-me-a-coffee]

## This integration is deprecated

Home Assistant 0.101 and newer includes official Airly integration.
Differences between the official and custom version:

- no configurable `scan interval`
- no API messages in Polish language
- some sensors are represented in `air_quality` entity

These differences result from the requirements for official integrations. You can still use the custom version of the integration. If you want to use the official version, remove integration from Configuration -> Integrations, remove component's files from the `/config/custom_components` folder and restart Home Assistant.

![Screenshot](https://github.com/bieniu/ha-airly/blob/master/images/airly-ha.png?raw=true)

You can add this integration to Home Assistant via `Configuration -> Integrations -> button with + sign -> Airly`. You can add this integration several times for different locations, e.g. home and work.

## API Key

To generate `API Key` go to [Airly for developers](https://developer.airly.eu/register) page.

**Airly allows 100 requests per day. Default scan interval of the integration is 15 minutes (96 requests per day). If you want use more than one instance of the integration you have to change scan interval via config flow options to not exceed allowed number of requests.**

[forum]: https://community.home-assistant.io/t/airly-integration-air-quality-data/124996
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=popout
[buy-me-a-coffee-shield]: https://img.shields.io/static/v1.svg?label=%20&message=Buy%20me%20a%20coffee&color=6f4e37&logo=buy%20me%20a%20coffee&logoColor=white
[buy-me-a-coffee]: https://www.buymeacoffee.com/QnLdxeaqO
