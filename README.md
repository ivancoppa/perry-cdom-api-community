# perry-cdom-api-community
![Version](https://img.shields.io/github/v/release/ivancoppa/perry-cdom-api-community?include_prereleases)
![PyPi](https://img.shields.io/pypi/v/perry-cdom-api-community?label=latest%20pypi)
![Downloads PyPi](https://img.shields.io/pypi/dm/perry-cdom-api-community)

# Perry Electric CDOM/CRM4.0

**UNOFFICIAL** library for communicating with Perry Electric CDOM/CRM4.0 apis.

## Disclaimer :warning:

This project is unofficial and is not affiliated with, endorsed by, or supported by Perry Electric, Use this library and integration at your own risk. I am not responsible for any damages, malfunctions, or issues that may arise from using this software with your thermostat or any other device.

This project is unofficial and not affiliated with, endorsed by, or supported by Perry Electric. It is a personal initiative created to facilitate interaction with Perry Electric thermostats through a Python library and Home Assistant integration.
### Important Notice :warning:

Users assume all responsibility and legal liability for using this software. This library is intended to provide convenient access to thermostat controls for developers and hobbyists. It is not an official Perry Electric package, and excessive or commercial usage may lead to restrictions on your device or account.

Please note that using this software may involve risks, including possible malfunctions or compatibility issues with future updates by Perry Electric. Use at your own risk.

# Installation
Use poetry install --extras cli to install dependencies for CLI and the library itself.

# Listing devices
To get the thermostat, use the list command:

poetry run python3 src/cli.py list -s [cdom_serial_number] -p [pin]
