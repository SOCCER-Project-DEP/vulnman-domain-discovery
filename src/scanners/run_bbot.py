import json
import logging
import subprocess
import sys
from datetime import datetime
import time

from lib.db import get_database
from lib.models import Domain


def execute_bbot(skip_scan: bool, event_file_path: str, target: str):
    """
    Bbot yaml configuration does not support all options from the command line
    Bbot python library is buggy and did not work
    Thus, to be consistent, we are setting bbot only here
    """
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    #  portscan.rate: packets per second, default: 300
    command = f"""bbot \
         --target {target} \
         --force \
         --ignore-failed-deps \
         --yes \
         --name {target}_{timestamp} \
         --preset subdomain-enum \
         --require-flag safe \
         --config "modules.portscan.rate=50" \
         --config "home=/var/log/domain_discovery/"
        """

    logging.info(f"Executing command: {command}")
    if not skip_scan:
        output = subprocess.run(
            command,  # command to execute
            capture_output=True,  # To get output of stdout and stderr
            shell=True,  # So command argument can be string and not list
            text=True,  # To get output as utf-8 string
            errors="replace",  # Don't throw UnicodeDecodeError on bad characters
        )
        if output.returncode != 0:
            logging.error(f"Error while executing bbot: {output}")
            sys.exit(1)
    else:
        output = "Skipping scan..."

    logging.info(f"Output: {output}")
    # sleep 3 seconds to let bbot finish writing to file

    logging.info("Sleeping for 3 seconds to let bbot finish writing to file")
    time.sleep(3)

    if event_file_path is None or event_file_path.strip() == "":
        event_file_path = f"/var/log/domain_discovery/scans/{target}_{timestamp}/output.json"
    with open(event_file_path) as f:
        for line in f:
            yield json.loads(line)


def orchestrate_scan(skip_scan: bool = False, event_file_path: str = None, target: str = "muni.cz"):
    db = get_database()
    domains = []
    logging.info("Starting scan")
    for event in execute_bbot(skip_scan, event_file_path, target):
        try:
            if event["type"] not in [
                "DNS_NAME",
                "URL",
                "IP_ADDRESS",
                "OPEN_TCP_PORT",
            ]:
                continue

            if event.get("port", None) is not None:
                port = event["port"]
            else:
                port = 443

            if (name := event.get("data", None)) is None:
                continue

            # handle edge case where after : is port then we need to split it
            # http://example.com:80 has two semicolons
            # so we need to check if after semi colon is number
            if ":" in name:
                name, *port = name.split(":")
                if port and port[0].isnumeric():
                    port = int(port[0])
                else:
                    port = 443
            else:
                port = 443

            discovered_time = datetime.now()
            if (time := db.get_discovered_time_domain(name, port)) is not None:
                discovered_time = time

            domains.append(
                d := Domain(
                    name=name,
                    port=port,
                    discovered_tool=f"bbot_{target}",
                    discovered_time=discovered_time,
                    last_seen=datetime.now(),
                    blacklisted=False,
                    info=str(event),
                )
            )
            db.update_last_seen(d)
        except KeyError as e:
            logging.warning(f"error parsing event from bbot {event}, {e}")
    logging.info(f"Scan finished, found {len(domains)} domains")
    return domains
