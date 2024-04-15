import kopf
from loguru import logger
import asyncio
from cerberus import Validator
import os
import requests

DEFAULT_USERNAME = os.getenv('USERNAME', 'admin')
DEFAULT_PASSWORD = os.getenv('USERNAME', 'admin')
TOKEN = ""

schema = {"record_name": {"type": "string"},
          "record_value": {"type": "string"},
          "zone": {"type": "string"}}

DNS_ENDPOINT = os.getenv("DNS_ENDPOINT", "127.0.0.1:56196")  # e.g. http://localhost:56196


def zone_already_exists(dns_endpoint, generated_token, zone_name) -> bool:
    get_zones_response = requests.get(
        f"{dns_endpoint}/api/zones/list?token={generated_token}&pageNumber=1&zonesPerPage=10")
    zones = get_zones_response.json()["response"]["zones"]

    for zone in zones:
        if zone["name"] == zone_name:
            return True

    return False


def is_valid_dns_entry_config_map(name, config_map):
    validator = Validator(schema)
    if not validator.validate(config_map):
        logger.error(f"Error validating DNS entry config map {name} with schema errors {validator.errors}")
        logger.error("Schema validation error for ")
        return False
    return True


@kopf.on.create('ConfigMap')
def create_fn(body, **_):
    logger.info(body['metadata']['annotations'])
    if body['metadata']['annotations'].get('technitium-dns-entry/v1', None):
        # validate schema
        if is_valid_dns_entry_config_map(body['metadata']['name'], body['data']):
            # create entry in technitium dns
            logger.info(f"valid")
        else:
            # do nothing
            logger.info(f"invalid")


@kopf.on.delete('ConfigMap')
def create_fn(body, **_):
    logger.info(body['metadata']['annotations'])
    if body['metadata']['annotations'].get('technitium-dns-entry/v1', None):
        # validate schema
        if is_valid_dns_entry_config_map(body['metadata']['name'], body['data']):
            # create entry in technitium dns
            logger.info(f"valid")
        else:
            # do nothing
            logger.info(f"invalid")


LOCK: asyncio.Lock


def generate_token(dns_endpoint, username, password, token_name) -> str:
    return \
        requests.get(
            f"{dns_endpoint}/api/user/createToken?user={username}&pass={password}&tokenName={token_name}").json()[
            "token"]


@kopf.on.startup()
async def startup_fn(logger, **kwargs):
    # TODO Generate technitium dns token
    generate_token(DNS_ENDPOINT, DEFAULT_USERNAME, DEFAULT_PASSWORD, "technitium-dns-kube-controller")
    global LOCK
    LOCK = asyncio.Lock()