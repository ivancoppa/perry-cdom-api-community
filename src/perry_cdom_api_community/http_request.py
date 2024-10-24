import logging

from aiohttp import ClientResponse, ClientSession

from perry_cdom_api_community.const import PERRY_CDOM_BASE_URL

_LOGGER = logging.getLogger(__name__)


class PerryHTTPRequest:
    def __init__(self, session: ClientSession, serial_number, pin):
        self.session = session
        self._cdom_serial_number = serial_number
        self._pin = pin
        self.host = PERRY_CDOM_BASE_URL

    async def request(self, method: str, path: str, **kwargs) -> ClientResponse:
        """Make a request."""
        json = kwargs.get("json", {})
        json["Pin"] = self._pin
        json["CdomSerialNumber"] = self._cdom_serial_number
        headers = kwargs.get("headers")

        if headers is None:
            headers = {}
        else:
            headers = dict(headers)

        headers["Content-type"] = "application/json"

        return await self.session.request(
            method, f"{self.host}/{path}", headers=headers, json=json
        )
