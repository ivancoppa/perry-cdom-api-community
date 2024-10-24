import json
import logging

from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientResponseError

from perry_cdom_api_community.const import (
    PERRY_CDOM_BASE_URL,
    PERRY_CDOM_GET_INFO_URL,
    PERRY_CDOM_SET_WORKING_MODE,
)

# from .entity import PerryThermostat
from perry_cdom_api_community.http_request import PerryHTTPRequest

# from typing import Optional

_LOGGER = logging.getLogger(__name__)


class PerryCdomCrm4API:
    """Class to communicate with the Perry CDOM CRM 4.0 API."""

    def __init__(self, session: ClientSession, serial_number, pin):
        """Initialize the API and store the auth so we can make requests."""
        self.api_root = "https://cdom.perryhome.it/CDomWS.svc/rests"
        self.session = session
        self.cdom_serial_number = serial_number
        self.pin = pin
        self.host = PERRY_CDOM_BASE_URL
        self.api = PerryHTTPRequest(self.session, self.cdom_serial_number, self.pin)
        self.perry_thermostat = None

    async def set_thermostat(self, thermo_zone_container, changes) -> bool:
        """Change the appliances."""

        data = thermo_zone_container | changes

        if "CdomSerialNumber" in data:
            del data["CdomSerialNumber"]
        if "CreationDate" in data:
            del data["CreationDate"]
        if "easyModeCoolingActivationTime" in data:
            del data["easyModeCoolingActivationTime"]
        if "easyModeCoolingSwitchOffTime" in data:
            del data["easyModeCoolingSwitchOffTime"]
        if "easyModeHeatingActivationTime" in data:
            del data["easyModeHeatingActivationTime"]
        if "easyModeHeatingSwitchOffTime" in data:
            del data["easyModeHeatingSwitchOffTime"]

        payload = {
            "ThermoZonesContainer": json.dumps(data)  # The modified zones container
        }

        resp = await self.api.request("post", PERRY_CDOM_SET_WORKING_MODE, json=payload)
        try:
            resp.raise_for_status()
            data = await resp.json()
            _LOGGER.info(
                f"Response from thermostat {self.cdom_serial_number}: {data}\n"
            )
            return True
        except ClientResponseError as e:
            _LOGGER.error(
                f"Error sending command '{thermo_zone_container}' to thermostat {self.cdom_serial_number} : {e}"
            )
            # raise e
            return False

        return False

    async def get_thermoreg(self):
        """Update the thermostat data."""
        _LOGGER.debug("PerryCdomCrm4API: loading data from server")
        resp = await self.api.request("post", PERRY_CDOM_GET_INFO_URL)
        try:
            resp.raise_for_status()
            data = await resp.json()

            if data["communicationStatus"] == -3:
                raise Exception("Error authenticating: " + data["Message"])
            return data

        except ClientResponseError as e:
            _LOGGER.error(
                f"Error getting data from thermostat {self._cdom_serial_number} : {e}"
            )
            raise e
