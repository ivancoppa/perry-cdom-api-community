import logging
from aiohttp import ClientSession

from perry_cdom_api_community.const import PERRY_CDOM_BASE_URL, PERRY_CDOM_GET_INFO_URL
from perry_cdom_api_community.entity import PerryThermostat
from perry_cdom_api_community.http_request import PerryHTTPRequest

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

    async def async_get_thermostat(self) -> PerryThermostat:
        """Return the appliances."""

        resp = await self.api.request("post", PERRY_CDOM_GET_INFO_URL)
        resp.raise_for_status()
        data = await resp.json()
        print(data)
        if data["communicationStatus"] == -3:
            raise Exception("Error authenticating: " + data["Message"])

        return PerryThermostat(self.cdom_serial_number, self.api, await resp.json())
