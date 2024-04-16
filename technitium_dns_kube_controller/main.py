import kopf
from loguru import logger
import asyncio
from cerberus import Validator
import os
import requests

# Technitium API Docs: https://github.com/TechnitiumSoftware/DnsServer/blob/master/APIDOCS.md

DEFAULT_USERNAME = os.getenv('USERNAME', 'admin')
DEFAULT_PASSWORD = os.getenv('USERNAME', 'admin')
TOKEN = ""
DEFAULT_ANNOTATION_KEY = "technitium-dns-entry/v1"

schema = {"record_name": {"type": "string"},
          "record_value": {"type": "string"},
          "zone": {"type": "string"}}

DNS_ENDPOINT = os.getenv("DNS_ENDPOINT", "http://127.0.0.1:5380")  # e.g. http://localhost:56196


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


def create_record_fn(**kwargs):
    dns_endpoint = kwargs['dns_endpoint']
    token = kwargs['token']
    zone = kwargs['zone']
    url = f"{dns_endpoint}/api/zones/records/add?token={token}&domain={kwargs['record_name']}.{zone}&zone={zone}&type=A&ipAddress={kwargs['record_value']}"
    logger.info(f"Creating DNS entry at {url}")
    if not zone_already_exists(dns_endpoint, token, zone):
        requests.get(f"{DNS_ENDPOINT}/api/zones/create?token={token}&zone={zone}")
    requests.get(url)


def update_record_fn(**kwargs):
    old_record_value = kwargs['old']['data']['record_value']
    url = f"{kwargs['dns_endpoint']}/api/zones/records/update?token={kwargs['token']}&domain={kwargs['record_name']}.{kwargs['zone']}&zone={kwargs['zone']}&type=A&value={old_record_value}&newValue={kwargs['record_value']}&ptr=false"
    logger.info(f"Updating DNS entry at {url}")
    requests.get(url)


def delete_record_fn(**kwargs):
    url = f"{kwargs['dns_endpoint']}/api/zones/records/delete?token={kwargs['token']}&domain={kwargs['record_name']}.{kwargs['zone']}&zone={kwargs['zone']}&type=A&ipAddress={kwargs['record_value']}"
    logger.debug(f"Deleting record at {url}")
    requests.get(url)


def base_resource_fn(resource_fn, **kwargs):
    body = kwargs.get("body")
    old = kwargs.get("old", None)
    if body['metadata']['annotations'].get(DEFAULT_ANNOTATION_KEY, None):
        # validate schema
        if is_valid_dns_entry_config_map(body['metadata']['name'], body['data']):
            entry = body['data']
            return resource_fn(dns_endpoint=DNS_ENDPOINT, token=TOKEN, zone=entry['zone'],
                               record_name=entry['record_name'], record_value=entry['record_value'], old=old)
        else:
            logger.info(f"no action taken for resource {body['metadata']['name']}")


@kopf.on.create('', 'v1', 'ConfigMap')
def create_fn(body, **_):
    base_resource_fn(create_record_fn, body=body)


@kopf.on.update('', 'v1', 'ConfigMap')
def update_fn(body, old, **_):
    base_resource_fn(update_record_fn, body=body, old=old)


@kopf.on.delete('', 'v1', 'ConfigMap')
def delete_fn(body, **_):
    base_resource_fn(delete_record_fn, body=body)


def generate_token(dns_endpoint, username, password, token_name) -> str:
    return \
        requests.get(
            f"{dns_endpoint}/api/user/createToken?user={username}&pass={password}&tokenName={token_name}").json()[
            "token"]


def endpoint_is_accessible(dns_endpoint) -> bool:
    try:
        requests.get(dns_endpoint)
        return True
    except ConnectionError:
        return False


def ensure_no_previous_record(zone_name, dns_endpoint, record_name, generated_token):
    """ensure that the record name does not currently exist in Technitium DNS server
       will cause issues where multiple IPs will be returned if duplicate entries for a record name present
       Only nice way to do this is deleting and recreating zone
    """
    response = requests.get(f"{dns_endpoint}/api/zones/delete?token={generated_token}&zone={zone_name}")
    print("evaluated : " + f"{dns_endpoint}/api/zones/delete?token={generated_token}&zone={zone_name}")
    print(response.content)


def main():
    dns_endpoint = os.getenv("DNS_ENDPOINT")  # e.g. http://localhost:56196

    if endpoint_is_accessible(dns_endpoint):
        token_name = os.getenv("TOKEN_NAME")  # secret token name
        username = os.getenv("USERNAME")  # username to technitium dns
        password = os.getenv("PASSWORD")  # password to technitium dns
        zone_name = os.getenv("ZONE")  # zone to create e.g. example.com
        record_name = os.getenv("RECORD_NAME")  # record to add to zone e.g. "*" note record will always be A record
        record_value = os.getenv("RECORD_VALUE")  # dns entry to add for record e.g. 192.168.1.10

        generated_token = generate_token(dns_endpoint, username, password, token_name)

        ensure_no_previous_record(zone_name, dns_endpoint, record_name, generated_token)

        if not zone_already_exists(dns_endpoint, generated_token, zone_name):
            requests.get(f"{dns_endpoint}/api/zones/create?token={generated_token}&zone={zone_name}")

        requests.get(
            f"{dns_endpoint}/api/zones/records/add?token={generated_token}&domain={record_name}.{zone_name}&zone={zone_name}&type=A&ipAddress={record_value}&priority=1")
        print(f"Created record {record_name} in zone {zone_name}! Enjoy :D")
    else:
        raise SystemExit


if __name__ == '__main__':
    main()

@kopf.on.startup()
def configure(settings: kopf.OperatorSettings, **_):
    global TOKEN
    logger.info("Started Technitium DNS Kube Controller")
    logger.info(f"the settings {settings}")
    TOKEN = generate_token(DNS_ENDPOINT, DEFAULT_USERNAME, DEFAULT_PASSWORD,
                           "technitium-dns-kube-controller")
