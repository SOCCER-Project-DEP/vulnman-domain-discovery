import json
import logging
from datetime import datetime

import click
from lib.db import get_database
from lib.models import Domain
from logger import setup_logger
from scanners.run_bbot import orchestrate_scan


def dd_lubos(skip_scan: bool) -> list[Domain]:
    # placeholder for any other domain discovery scanner
    return []


def dd_bbot(skip_scan: bool, event_file_path: str, target: str) -> list[Domain]:
    return orchestrate_scan(skip_scan, event_file_path, target)


@click.command()
@click.option("--skip-scan", is_flag=True, help="Skip scanning")
@click.option("--event-file-path", help="Path to the event file")
@click.option("--skip-lubos", is_flag=True, default=False, help="Don't run Lubos scanner")
@click.option("--skip-bbot", is_flag=True, default=False, help="Don't run Bbot scanner")
@click.option("-t", "--target", help="Target domain")
def main(skip_scan: bool, event_file_path: str, skip_lubos: bool, skip_bbot: bool, target: str):
    log_file = f"/var/log/domain_discovery/domain_discovery_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    setup_logger(log_file)

    db = get_database()

    logging.info("Database prepared")

    domains = []

    if not skip_lubos:
        logging.info("Running Lubos scanner")
        domains += dd_lubos(skip_scan)
        logging.info("Lubos scanner finished")

    if not skip_bbot:
        logging.info("Running Bbot scanner")
        domains += dd_bbot(skip_scan, event_file_path, target)
        logging.info("Bbot scanner finished")

    db.process_found_domains(domains, target)
    stat_file = "stats.json"
    with open(stat_file, "w") as f:
        f.write(json.dumps(db.get_stats(), indent=4))

    logging.info("Domains processed, exiting")


if __name__ == "__main__":
    main()
