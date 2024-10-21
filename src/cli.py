import argparse
import asyncio
import json
import logging
import ssl

import aiohttp
import certifi

from perry_cdom_api_community.api import PerryCdomCrm4API

logging.basicConfig(level=logging.DEBUG)

async def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    login_parser = subparsers.add_parser("login")
    required_argument = login_parser.add_argument_group("required arguments")
    required_argument.add_argument(
        "-c", dest="cdom_serial_number", help="Serial number of the thermostat", required=True
    )
    required_argument.add_argument(
        "-p", dest="pin", help="Pin of the thermostat", required=True
    )

    _list_parser = subparsers.add_parser("list")

    command_parser = subparsers.add_parser("command")
    command_parser.add_argument(
        "-c",
        dest="command",
        help="Command that should be sent to the device",
        required=True,
    )
    command_parser.add_argument(
        "-s",
        dest="cdom_serial_number",
        help="Serial number of the thermostat",
        required=True,
    )
    command_parser.add_argument(
        "-p",
        dest="pin",
        help="Pin of the thermostat",
        required=True,
    )

    args = parser.parse_args()

    ssl_context = ssl.create_default_context()
    conn = aiohttp.TCPConnector(ssl=ssl_context)



    async with aiohttp.ClientSession(connector=conn) as session:
        hub = PerryCdomCrm4API(session, 1820188, 1234)
        thermostat = await hub.async_get_thermostat()
        await thermostat.async_update()

        print(f"Thermostat ID: {thermostat.cdom_serial_number}")

        print(thermostat.cdom_serial_number)

        if args.cmd == "command":
            try:
               await thermostat.send_command(json.loads(args.command))
            except StopIteration:
                print(f"Thermostat with ID {args.cdom_serial_number} was not found")


if __name__ == "__main__":
    asyncio.run(main())