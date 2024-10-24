import json
import logging
from datetime import datetime

# from typing import Dict, List, Union
from typing import Dict, Union

from perry_cdom_api_community.api import PerryCdomCrm4API

_LOGGER = logging.getLogger(__name__)


class PerryThermostat:
    def __init__(self, cdom_serial_number: int, api: PerryCdomCrm4API):
        self.cdom_serial_number = cdom_serial_number
        self.api = api
        self.initial_data: Dict = {}
        self.thermo_zones_container_data: Dict = {}

        self._zones: dict[int, Dict] = {}

    @staticmethod
    def _parse_date(date_str: Union[str, datetime]) -> datetime:
        """Parse date string into datetime object."""
        if isinstance(date_str, datetime):
            return date_str
        try:
            return datetime.strptime(date_str, "%d/%m/%Y %H:%M:%S")
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}")

    @property
    def get_zones(self) -> Dict:
        return self._zones

    async def get_thermostat(self):
        # calling HTTP API PerryCdomCrm4API
        self.initial_data = await self.api.get_thermoreg()
        self.thermo_zones_container_data = self.initial_data["ThermoZonesContainer"]
        for zone in self.initial_data["ThermoZonesContainer"]["zones"]:
            self._zones[zone["zoneId"]] = zone
        return self.initial_data

    def get_data(self) -> Dict:
        return self.initial_data

    async def set_thermostat(self, changes: Dict):
        # calling HTTP API PerryCdomCrm4API
        if await self.api.set_thermostat(self.thermo_zones_container_data, changes):
            _LOGGER.debug(
                f"Changes '{changes}' sent to thermostat {self.cdom_serial_number}"
            )
            # refresh data
            _LOGGER.debug("Refreshing data")
            await self.get_thermostat()

    def get_thermoregulation_status(self):
        return self.thermo_zones_container_data["currentSharedThermoMode"]

    async def set_thermoregulation_off(self) -> bool:
        _LOGGER.info("PerryThermostat set_thermoregulation_off")
        changes = {}
        changes["currentSharedThermoMode"] = 5
        _LOGGER.debug("PerryThermostat set_thermoregulation_off " + json.dumps(changes))
        return await self.set_thermostat(changes)

    async def set_thermoregulation_on(self) -> bool:
        _LOGGER.info("PerryThermostat set_thermoregulation_off")
        changes = {}
        changes["currentSharedThermoMode"] = 0
        _LOGGER.debug("PerryThermostat set_thermoregulation_off " + json.dumps(changes))
        return await self.set_thermostat(changes)

    async def set_zone_temperature_manual(self, zone_id, temperature) -> bool:
        _LOGGER.info("PerryThermostat set_zone_temperature_manual " + str(zone_id))
        payload = {}
        payload["zones"] = self.thermo_zones_container_data["zones"]
        for id in range(len(payload["zones"])):
            if payload["zones"][id]["zoneId"] == zone_id:
                payload["zones"][id]["customTemperatureForManualMode"] = temperature
                payload["zones"][id]["currentProfileLevel"] = 5
                payload["zones"][id]["currentMode"] = 2

        _LOGGER.debug(
            "PerryThermostat set_zone_temperature_manual " + json.dumps(payload)
        )
        return await self.set_thermostat(payload)

    async def set_zone_temperature_auto(self, zone_id) -> bool:
        _LOGGER.info("PerryThermostat set_zone_temperature_auto " + str(zone_id))
        payload = {}
        payload["zones"] = self.thermo_zones_container_data["zones"]
        for id in range(len(payload["zones"])):
            if payload["zones"][id]["zoneId"] == zone_id:
                payload["zones"][id]["currentProfileLevel"] = 0
                payload["zones"][id]["currentMode"] = 0

        _LOGGER.debug(
            "PerryThermostat set_zone_temperature_auto " + json.dumps(payload)
        )
        return await self.set_thermostat(payload)

    async def set_temperature_manual(self, temperature) -> bool:
        _LOGGER.info("PerryThermostat set_zone_temperature_manual")
        payload = {}
        payload["zones"] = self.thermo_zones_container_data["zones"]
        for id in range(len(payload["zones"])):
            payload["zones"][id]["customTemperatureForManualMode"] = temperature
            payload["zones"][id]["currentProfileLevel"] = 5
            payload["zones"][id]["currentMode"] = 2

        _LOGGER.debug(
            "PerryThermostat set_zone_temperature_manual " + json.dumps(payload)
        )
        return await self.set_thermostat(payload)

    async def set_temperature_auto(self) -> bool:
        _LOGGER.info("PerryThermostat set_zone_temperature_auto")
        payload = {}
        payload["zones"] = self.thermo_zones_container_data["zones"]
        for id in range(len(payload["zones"])):
            payload["zones"][id]["currentProfileLevel"] = 0
            payload["zones"][id]["currentMode"] = 0

        _LOGGER.debug(
            "PerryThermostat set_zone_temperature_auto " + json.dumps(payload)
        )
        return await self.set_thermostat(payload)
