import logging
from datetime import datetime
from functools import lru_cache

from lib.models import Domain, Domains
from lib.prepare import prepare_db
from lib.utils import clean_domain_name, process_old_and_new_domains
from sqlalchemy import func
from sqlalchemy.orm import Session

# This class can be used as lib for database operations
# Use with combination of prepare_db() function


class Database:
    def __init__(self, engine):
        self.engine = engine
        self.session = Session(bind=engine)
        logging.info("Database session created")

    def __del__(self):
        self.session.close()
        logging.info("Database session closed")

    def domain_in_db(self, domain_name: str, port):
        return self.session.query(Domains).filter(Domains.name == domain_name, Domains.port == port).first()

    def get_current_domains(self):
        return self.session.query(Domains).all()

    def insert_new_domains(self, new_domains: list[Domain], target: str):
        for domain in new_domains:
            if self.domain_in_db(domain.name, domain.port) is not None:
                continue
            if domain.name is None:
                continue
            if domain.name.endswith("."):
                domain.name = domain.name[:-1]
            if not domain.name.endswith(f".{target}") and not domain.name.replace(".", "").isnumeric():
                logging.warning(f"Domain {domain.name} not in target {target}")
                continue

            new_domain = Domains(**domain.__dict__)
            self.session.add(new_domain)
        self.session.commit()

    def update_last_seen(self, domain: Domain):
        # Has to be called before old and new domains are merged
        try:
            domain.name = clean_domain_name(domain.name)
            if (d := self.domain_in_db(domain.name, domain.port)) is None:
                return

            # Update last seen
            d.last_seen = domain.last_seen
            self.session.add(d)

            self.session.commit()
        except Exception as e:
            logging.warning(f"Error while updating domain {domain.name}: {e}")

    def process_found_domains(self, found_domains: list[Domain], target: str):
        new_domains = process_old_and_new_domains(self.get_current_domains(), found_domains)
        self.insert_new_domains(new_domains, target)

    def get_discovered_time_domain(self, domain_name: str, port: int):
        d = self.domain_in_db(domain_name, port)
        if d is not None:
            return d.discovered_time
        return None

    def get_stats(self):
        stats = {
            "old_domains": 0,
            "new_domains": 0,
        }

        current_date = datetime.now().date()

        # Query for new domains; new domains were discovered today and last seen is current date
        stats["new_domains"] = (
            self.session.query(Domains)
            .filter(
                func.date(Domains.discovered_time) >= current_date,
            )
            .count()
        )

        # Query for old domains that were not discovered today and last seen is current date
        stats["old_domains"] = (
            self.session.query(Domains)
            .filter(
                func.date(Domains.discovered_time) < current_date,
            )
            .count()
        )

        return stats


@lru_cache(maxsize=1)
def get_database():
    return Database(prepare_db())