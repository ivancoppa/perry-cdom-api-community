import pytest
from aiohttp import ClientSession
from aioresponses import aioresponses

from perry_cdom_api_community.api import PerryCdomCrm4API
from perry_cdom_api_community.entity import PerryThermostat


@pytest.mark.asyncio
async def test_get_thermoreg():
    # Mock the token manager

    async with ClientSession() as session:
        cdom_serial_number = 12345678
        cdom_pin = 0000

        # Create an instance of PerryCdomCrm4API
        hub = PerryCdomCrm4API(session, cdom_serial_number, cdom_pin)
        thermostat = PerryThermostat(cdom_serial_number, hub)

        with aioresponses() as mocked:
            # Mock the response for the appliances endpoint
            appliances_url = (
                "https://cdom.perryhome.it/CDomWS.svc/rests/ThermoregGetInfo"
            )

            mocked.post(
                appliances_url,
                headers={"Content-type": "application/json"},
                payload={
                    "Message": None,
                    "communicationStatus": 100,
                    "connectionStatus": 10,
                    "HasHistory": True,
                    "HistoryDate": "24\/10\/2024 14:51:22",
                    "InfoDate": "\/Date(1729774282059+0200)\/",
                    "ThermoZonesContainer": {
                        "CdomSerialNumber": cdom_serial_number,
                        "zones": [],
                    },
                },
            )

            # Call the method
            thermostatdata = await thermostat.get_thermostat()

            # Assertions
            assert len(thermostatdata) == 7
