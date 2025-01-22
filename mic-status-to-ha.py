import json
import logging
import os
from argparse import ArgumentParser
from http.client import HTTPException
from time import sleep
from typing import Optional
from urllib.request import Request, urlopen

# Constants
HA_URL = os.environ["HA_URL"]
BEARER_TOKEN = os.environ["HA_BEARER_TOKEN"]
HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json",
}
ENTITY_ID = os.environ["HA_ENTITY_ID"]
MIC_STATUS_FILE_PATH = "/proc/asound/card0/pcm0p/sub0/status"


def get_entity_data(entity_id: str) -> Optional[dict]:
    """Fetches the current state of the provided entity."""
    request = Request(f"{HA_URL}/api/states/{entity_id}", headers=HEADERS, method="GET")
    try:
        with urlopen(request) as response:
            response_data_str = response.read().decode("utf-8")
    except HTTPException as e:
        logging.error(f"Failed to fetch entity state: {e}")
        return None
    return json.loads(response_data_str)


def change_entity_data(entity_id: str, updated_state: dict) -> Optional[dict]:
    """Updates the state of the given entity."""
    request = Request(
        f"{HA_URL}/api/states/{entity_id}",
        headers=HEADERS,
        method="POST",
        data=json.dumps(updated_state).encode("utf-8"),
    )
    try:
        with urlopen(request) as response:
            response_data_str = response.read().decode("utf-8")
    except HTTPException as e:
        logging.error(f"Failed to update entity state: {e}")
        return None
    return json.loads(response_data_str)


def get_mic_status() -> bool:
    """Returns True if the mic is active, and False otherwise."""
    with open(MIC_STATUS_FILE_PATH, "r") as mic_status_file:
        return "closed" not in mic_status_file.read()


def main():
    """Monitors mic status and updates the Home Assistant entity."""
    entity_data = None

    while True:
        if entity_data is None:
            entity_data = get_entity_data(ENTITY_ID)
            if entity_data is None:
                sleep(5)
                continue
            else:
                logging.info(f"Initial entity state: {entity_data}")

        ha_mic_state_is_on = entity_data.get("state") == "on"
        mic_is_on = get_mic_status()

        if mic_is_on != ha_mic_state_is_on:
            new_state = {
                "attributes": entity_data["attributes"],
                "entity_id": entity_data["attributes"],
                "state": "on" if mic_is_on else "off"
            }
            entity_data = change_entity_data(ENTITY_ID, new_state)
            logging.info(f"Changed entity state to: {entity_data}")
        else:
            logging.debug("No change in mic status")

        sleep(3)


def get_and_parse_args():
    args = ArgumentParser()
    args.add_argument("--log-level", default="INFO", help="Logging level", choices=["DEBUG", "INFO"])
    return args.parse_args()


if __name__ == "__main__":
    parsed_args = get_and_parse_args()
    logging.basicConfig(level=parsed_args.log_level)
    main()
