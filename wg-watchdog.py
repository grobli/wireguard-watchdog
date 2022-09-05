#! /usr/bin/env python3

import logging
import re
import subprocess
from multiprocessing.pool import ThreadPool
from time import sleep
from typing import Union

import requests
from requests.exceptions import RequestException

API_URLS = ["https://ifconfig.me", "https://api.ipify.org", "https://ident.me"]
IP_CHECK_INTERVAL = 1  # seconds
REQUEST_TIMEOUT = 2  # seconds
WIREGUARD_INTERFACES = ["wg0", "wg1"]
LOGGING_LEVEL = logging.INFO

logging.basicConfig(level=LOGGING_LEVEL,
                    format='%(asctime)s %(levelname)s: %(message)s')


def get_public_ip() -> tuple[Union[str, None], list[RequestException]]:
    def fetch_ip(url: str) -> tuple[Union[str, None], Union[RequestException, None]]:
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            ip = response.text
            logging.debug(f"Fetching public IP from: {url} | Response: {ip}")
            return ip, None
        except requests.exceptions.RequestException as e:
            logging.error(e)
            return None, e

    errors: list[RequestException] = []
    with ThreadPool(processes=len(API_URLS)) as pool:
        results = pool.map(fetch_ip, API_URLS)
    errors = [r[1] for r in results if r[1]]
    ips = [r[0] for r in results if r[0] and re.match(
        r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", r[0])]
    if ips:
        return ips[0], errors
    return None, errors


def reset_wireguard(interface: str):
    logging.warning(f"Resetting Wireguard interface - {interface}")
    subprocess.run(
        ["systemctl", "restart", f"wg-quick@{interface}"], check=True)


def main():
    previous_ip = None

    while True:
        if not previous_ip:
            previous_ip, _ = get_public_ip()
            logging.info(f"Current public IP: {previous_ip}")
            continue

        current_ip, _ = get_public_ip()
        if not current_ip:
            continue

        if current_ip != previous_ip:
            logging.warning(
                f"Public IP changed to: {current_ip} from: {previous_ip}")
            for interface in WIREGUARD_INTERFACES:
                reset_wireguard(interface)
            previous_ip = current_ip
            logging.info(f"Current public IP: {current_ip}")
        else:
            logging.debug(f"Public IP not changed: {current_ip}")

        sleep(IP_CHECK_INTERVAL)


if __name__ == '__main__':
    main()
