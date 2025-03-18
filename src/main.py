import importlib
import json
import logging
import os
from datetime import datetime
from pathlib import Path

import click

from lib.db import get_database
from lib.models import Domain
from logger import setup_logger
from scanners.run_bbot import orchestrate_scan

logger = logging.getLogger(__name__)


def dd_load_modules() -> list[Domain]:
    logger.info("Loading custom modules")
    py_files = [f for f in Path("src/modules").iterdir() if f.suffix == ".py" and f.name != "__init__.py"]
    domains = []
    for py_file in py_files:
        module_name = f"modules.{py_file.stem}"
        logger.info(f"Loading module {module_name}")
        module = importlib.import_module(module_name,package=__name__)
        try:
            domains += module.main()
        except (ImportError, AttributeError) as e:
            logger.error(f"Error in module {module_name}: {e}")
            continue
    return domains


def dd_bbot(skip_scan: bool, event_file_path: str, target: str) -> list[Domain]:
    return orchestrate_scan(skip_scan, event_file_path, target)


@click.command()
@click.option("--skip-scan", is_flag=True, help="Skip scanning")
@click.option("--event-file-path", help="Path to the event file")
@click.option("--skip-modules", is_flag=True, default=False, help="Don't run Lubos scanner, Not available currently")
@click.option("--skip-bbot", is_flag=True, default=False, help="Don't run Bbot scanner")
@click.option("-t", "--target", help="Target domain")
@click.option("--skip-db", is_flag=True, help="Skip database")
def main(skip_scan: bool, event_file_path: str, skip_modules: bool, skip_bbot: bool, target: str, skip_db: bool):
    log_file = f"/var/log/domain_discovery/domain_discovery_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    setup_logger(log_file)
    if not skip_db:
        db = get_database()
    else:
        db = None
        logger.info("Database skipped")

    logger.info("Database prepared")

    domains = []

    if not skip_modules:
        logger.info("Running custom modules")
        domains += dd_load_modules()
        logger.info("Custom modules finished")

    if not skip_bbot:
        logger.info("Running Bbot scanner")
        domains += dd_bbot(skip_scan, event_file_path, target)
        logger.info("Bbot scanner finished")

    if not skip_db:
        db.process_found_domains(domains, target)
        stat_file = "stats.json"
        with open(stat_file, "w") as f:
            f.write(json.dumps(db.get_stats(), indent=4))

    logger.info("Domains processed, exiting")


if __name__ == "__main__":
    main()
