import json
import logging
from datetime import datetime

# from typing import Dict, List, Union
from typing import Dict, Union

from aiohttp.client_exceptions import ClientResponseError

from perry_cdom_api_community.const import (
    PERRY_CDOM_GET_INFO_URL,
    PERRY_CDOM_SET_WORKING_MODE,
)
from perry_cdom_api_community.http_request import PerryHTTPRequest

_LOGGER = logging.getLogger(__name__)


class PerryZone:
    def __init__(self, zone_id: int, name: str, initial_data: Dict):

        self._zone_id = zone_id
        self._name = name.strip()  # Normalize name to avoid trailing spaces
        self._initial_data = initial_data

    @staticmethod
    def _parse_date(date_str: Union[str, datetime]) -> datetime:
        """Parse date string into datetime object."""
        if isinstance(date_str, datetime):
            return date_str
        try:
            return datetime.strptime(date_str, "%d/%m/%Y %H:%M:%S")
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}")

    # Getters and Setters

    @property
    def zone_id(self) -> int:
        return self._zone_id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value.strip()  # Avoid leading/trailing spaces

    @property
    def last_temperature(self) -> float:
        return self._last_temperature

    @last_temperature.setter
    def last_temperature(self, value: float):
        if not (0 <= value <= 100):  # Assuming temperature range
            raise ValueError("Temperature must be between 0 and 100")
        self._last_temperature = value

    # @property
    # def last_temperature_date(self) -> datetime:
    #    return self._last_temperature_date

    @property
    def current_mode(self) -> int:
        return self._current_mode

    @current_mode.setter
    def current_mode(self, mode: int):
        if mode not in [0, 1, 2]:  # Example: Assume 0 = off, 1 = heating, 2 = cooling
            raise ValueError("Invalid mode. Must be 0, 1, or 2.")
        self._current_mode = mode

    @property
    def custom_temperature_for_manual_mode(self) -> float:
        return self._custom_temperature_for_manual_mode

    @custom_temperature_for_manual_mode.setter
    def custom_temperature_for_manual_mode(self, value: float):
        if not (5 <= value <= 35):  # Example: Assuming safe temperature range
            raise ValueError("Temperature must be between 5 and 35 degrees.")
        self._custom_temperature_for_manual_mode = value

    @property
    def humidity(self) -> float:
        return self._humidity

    @humidity.setter
    def humidity(self, value: float):
        if not (0 <= value <= 100):
            raise ValueError("Humidity must be between 0 and 100%.")
        self._humidity = value

    @property
    def hysteresis(self) -> float:
        return self._hysteresis

    @hysteresis.setter
    def hysteresis(self, value: float):
        if value < 0:
            raise ValueError("Hysteresis must be non-negative.")
        self._hysteresis = value

    @property
    def heater_bit(self) -> bool:
        return self._heater_bit

    @heater_bit.setter
    def heater_bit(self, value: bool):
        self._heater_bit = value

    @property
    def functions_params(self) -> dict:
        return self._functions_params

    @functions_params.setter
    def functions_params(self, value: dict):
        if not isinstance(value, dict):
            raise ValueError("functions_params must be a dictionary.")
        self._functions_params = value

    def __repr__(self):
        return f"Zone(name={self._name}, last_temperature={self._last_temperature}, mode={self._current_mode})"


class PerryThermostat:
    def __init__(
        self, cdom_serial_number: int, api: PerryHTTPRequest, initial_data: Dict
    ):
        #                 creation_date: Union[str, datetime],
        # anti_freeze_enabled: bool = True,
        # anti_heat_enabled: bool = True,
        # zones: Optional[List[PerryZone]] = None):
        self._cdom_serial_number = cdom_serial_number
        self.api = api
        self.initial_data = initial_data
        self.thermo_zones_container_data = self.initial_data["ThermoZonesContainer"]
        # self.thermo_zones_container_data: dict[str, str] = {}
        # self.capabilities_data: dict[str, Any] = {}

        self._zones = {}
        for zone in self.initial_data["ThermoZonesContainer"]["zones"]:
            PerryZone(zone["zoneId"], zone["name"], zone)
            self._zones[zone["zoneId"]] = zone

    @staticmethod
    def _parse_date(date_str: Union[str, datetime]) -> datetime:
        """Parse date string into datetime object."""
        if isinstance(date_str, datetime):
            return date_str
        try:
            return datetime.strptime(date_str, "%d/%m/%Y %H:%M:%S")
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}")

    # Getters and Setters

    @property
    def cdom_serial_number(self) -> int:
        return self._cdom_serial_number

    # @property
    # def creation_date(self) -> datetime:
    #     return self._creation_date

    @property
    def anti_freeze_enabled(self) -> bool:
        return self._anti_freeze_enabled

    @anti_freeze_enabled.setter
    def anti_freeze_enabled(self, value: bool):
        self._anti_freeze_enabled = value

    @property
    def anti_heat_enabled(self) -> bool:
        return self._anti_heat_enabled

    @anti_heat_enabled.setter
    def anti_heat_enabled(self, value: bool):
        self._anti_heat_enabled = value

    # @property
    # def zones(self) -> List[PerryZone]:
    #    return self._zones

    # @zones.setter
    # def zones(self, value: List[PerryZone]):
    #    if not all(isinstance(zone, PerryZone) for zone in value):
    #        raise ValueError("All elements of zones must be of type Zone.")
    #    self._zones = value

    # def add_zone(self, zone: PerryZone):
    #    if not isinstance(zone, PerryZone):
    #        raise ValueError("Only Zone objects can be added.")
    #    self._zones.append(zone)

    def get_data(self) -> Dict:
        return self.initial_data

    def get_thermo_zones_container_data(self) -> Dict:
        return self.initial_data

    async def set_zone_manual_temperature(self, zone_id, temperature) -> bool:
        payload = {}
        payload["zones"] = self.thermo_zones_container_data["zones"]
        for id in range(len(payload["zones"])):
            if payload["zones"][id]["zoneId"] == zone_id:
                payload["zones"][id]["customTemperatureForManualMode"] = temperature
                payload["zones"][id]["currentProfileLevel"] = 5
                payload["zones"][id]["currentMode"] = 2

        _LOGGER.info("PerryCoordinators set_manual_temperature " + json.dumps(payload))
        return await self.send_command(payload)

    async def send_command(self, changes: Dict):
        _LOGGER.info(
            f"Changes '{changes}' sent to thermostat {self._cdom_serial_number}"
        )

        data = self.thermo_zones_container_data | changes
        del data["CdomSerialNumber"]
        del data["CreationDate"]
        del data["easyModeCoolingActivationTime"]
        del data["easyModeCoolingSwitchOffTime"]
        del data["easyModeHeatingActivationTime"]
        del data["easyModeHeatingSwitchOffTime"]

        payload = {
            "ThermoZonesContainer": json.dumps(data)  # The modified zones container
        }

        resp = await self.api.request("post", PERRY_CDOM_SET_WORKING_MODE, json=payload)
        try:
            data = await resp.json()
            _LOGGER.info(f"Response from thermostat {self._cdom_serial_number}: {data}")
            resp.raise_for_status()
        except ClientResponseError as e:
            _LOGGER.error(
                f"Error sending command '{changes}' to thermostat {self._cdom_serial_number}"
            )
            raise e

    async def async_update(self):
        """Update the thermostat data."""
        if not self.thermo_zones_container_data:
            resp = await self.api.request("post", PERRY_CDOM_GET_INFO_URL)
            resp.raise_for_status()
            data = await resp.json()
            self.initial_data = data
            self.thermo_zones_container_data = data["ThermoZonesContainer"]
