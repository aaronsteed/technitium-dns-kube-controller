import os
import time

import requests


def zone_already_exists(dns_endpoint, generated_token, zone_name) -> bool:
    get_zones_response = requests.get(
        f"{dns_endpoint}/api/zones/list?token={generated_token}&pageNumber=1&zonesPerPage=10")
    zones = get_zones_response.json()["response"]["zones"]

    for zone in zones:
        if zone["name"] == zone_name:
            return True

    return False


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
