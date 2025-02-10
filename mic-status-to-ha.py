#!/usr/bin/env python3

import json
import logging
import os
import re
from argparse import ArgumentParser
from dataclasses import dataclass, field
from http.client import HTTPException
from subprocess import check_output
from time import sleep
from typing import Optional
from urllib.request import Request, urlopen


@dataclass
class Config:
    ha_url: str
    ha_bearer_token: str
    ha_entity_id: str
    monitored_device_name: str
    log_level: str = "INFO"
    ha_headers: dict = field(init=False)

    def __post_init__(self):
        if not self.ha_url:
            raise ValueError("Home Assistant URL is required")
        if not self.ha_bearer_token:
            raise ValueError("Bearer token is required")
        if not self.ha_entity_id:
            raise ValueError("Entity ID is required")
        if not self.monitored_device_name:
            raise ValueError("Monitored device name is required")
        self.ha_headers = {
            "Authorization": f"Bearer {self.ha_bearer_token}",
            "Content-Type": "application/json",
        }


def get_entity_data(config: Config) -> Optional[dict]:
    """Fetches the current state of the provided entity."""
    request = Request(f"{config.ha_url}/api/states/{config.ha_entity_id}", headers=config.ha_headers, method="GET")
    try:
        with urlopen(request) as response:
            response_data_str = response.read().decode("utf-8")
    except HTTPException as e:
        logging.error(f"Failed to fetch entity state: {e}")
        return None
    return json.loads(response_data_str)


def change_entity_data(config: Config, updated_state: dict) -> Optional[dict]:
    """Updates the state of the given entity."""
    try:
        request = Request(
            f"{config.ha_url}/api/states/{config.ha_entity_id}",
            headers=config.ha_headers,
            method="POST",
            data=json.dumps(updated_state).encode("utf-8"),
        )
        with urlopen(request) as response:
            response_data_str = response.read().decode("utf-8")
    except HTTPException as e:
        logging.error(f"Failed to update entity state: {e}")
        return None
    return json.loads(response_data_str)


def get_names_with_states_from_pa_ctl_stdout(cmd_output: str):
    devices = []
    device_pattern = r"Source #\d+\n\tState: (\w+)\n\tName: (.+?)\n"

    matches = re.finditer(device_pattern, cmd_output)
    for match in matches:
        state = match.group(1)
        name = match.group(2)
        devices.append({"name": name, "state": state})

    return devices


def get_mic_status(device_name: str) -> bool:
    """Returns True if the mic is active, and False otherwise."""
    try:
        res = check_output(["/bin/pactl", "list", "sources"]).decode("utf-8")
    except Exception as e:
        logging.error(f"Failed to get mic status: {e}")
        return False
    devices = get_names_with_states_from_pa_ctl_stdout(res)
    logging.debug(f"Found devices: {devices}")

    monitored_device = next((d for d in devices if d["name"] == device_name), None)
    logging.debug(f"Monitored device: {monitored_device}")

    if not monitored_device:
        logging.error(f"Device {device_name} not found in devices: {devices}")
        return False

    logging.debug(f"Monitored device state: {monitored_device['state']}")
    return monitored_device["state"] == "RUNNING"


def main(config: Config):
    """Monitors mic status and updates the Home Assistant entity."""
    logging.basicConfig(level=config.log_level)

    entity_data = None

    while True:
        if entity_data is None:
            entity_data = get_entity_data(config)
            if entity_data is None:
                sleep(5)
                continue
            else:
                logging.info(f"Initial entity state: {entity_data}")

        ha_mic_state_is_on = entity_data.get("state") == "on"
        mic_is_on = get_mic_status(config.monitored_device_name)

        if mic_is_on != ha_mic_state_is_on:
            new_state = {
                "attributes": entity_data["attributes"],
                "entity_id": entity_data["attributes"],
                "state": "on" if mic_is_on else "off"
            }
            entity_data = change_entity_data(config, new_state)
            logging.info(f"Changed entity state to: {entity_data}")
        else:
            logging.debug("No change in mic status")

        sleep(3)


def parse_config() -> Config:
    parser = ArgumentParser()
    parser.add_argument("--log-level", default="INFO", help="Logging level", choices=["DEBUG", "INFO"])
    args = parser.parse_args()

    return Config(
        ha_url=os.environ.get("HA_URL"),
        ha_bearer_token=os.environ.get("HA_BEARER_TOKEN"),
        ha_entity_id=os.environ.get("HA_ENTITY_ID"),
        monitored_device_name=os.environ.get("MONITORED_DEVICE"),
        log_level=args.log_level)


if __name__ == "__main__":
    parsed_config = parse_config()
    main(parsed_config)
