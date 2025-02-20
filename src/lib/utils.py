import ipaddress as ip
from typing import List

import polars as pl
from lib.models import Domain


class BlackList:
    def __init__(self) -> None:
        self._blacklisted_file = "blacklist.txt"
        self._blacklisted_ip_subnets: List[str] = []
        self._blacklisted_domains: List[str] = []
        self.process_blacklist()

    def process_blacklist(self) -> None:
        with open(self._blacklisted_file) as blacklist_file:
            for line in blacklist_file:
                blacklisted_item = line.rstrip()
                try:
                    # is ip address
                    ip.ip_network(blacklisted_item)
                    self._blacklisted_ip_subnets.append(blacklisted_item)
                except ValueError:
                    # isn't ip address -> domain
                    self._blacklisted_domains.append(blacklisted_item)

    def check_blacklist(self, domain: str) -> bool:
        try:  # is ip address
            return any(
                map(
                    lambda subnet: ip.ip_address(domain) in ip.ip_network(subnet),
                    self._blacklisted_ip_subnets,
                )
            )
        except ValueError:  # isn't ip address -> domain
            return any(
                map(lambda b_domain: b_domain in domain, self._blacklisted_domains)
            )
        # return True if domain is blacklisted
        # "any" returns True if any of the elements is True

    def negated_check_blacklist(self, domain: str) -> bool:
        return not self.check_blacklist(domain)
        # return True if domain is not blacklisted


def clean_domain_name(x: str) -> str:
    return x.lower().replace("https://", "").replace("http://", "").split("/")[0]


def clean_domain_name_pl(xs: pl.DataFrame) -> pl.DataFrame:
    return xs.with_columns(
        pl.col("name")
        .str.to_lowercase()
        .str.replace("https://", "")
        .str.replace("http://", "")
        .str.replace("/.*", "")
    )


def strip_unncessary_columns(domains: list[Domain]) -> list[Domain]:
    # SQLalchemy adds unnecessary columns to the query
    return [
        Domain(
            name=domain.name,
            port=domain.port,
            discovered_tool=domain.discovered_tool,
            discovered_time=domain.discovered_time,
            last_seen=domain.last_seen,
            blacklisted=domain.blacklisted,
            info=domain.info,
        )
        for domain in domains
    ]


def process_old_and_new_domains(
    old_domains: list[Domain], found_domains: list[Domain]
) -> List[Domain]:
    """
    Merges two sets of domains, ensuring no duplicates, and checks for blacklisted domains.

    This function merges old and newly found domains into a single list, ensuring that there are no duplicate domains.
    A domain is considered duplicate if it has the same name and port.
    IP addresses are also treated as domains in this context.
    The function also checks and updates if a domain is blacklisted but does not update the time.
    It is recommended to call this function only once per run.

    Args:
        old_domains (list[Domain]): List of previously known domains.
        found_domains (list[Domain]): List of newly discovered domains.

    Returns:
        List[Domain]: A list of merged domains without duplicates, with updated blacklist status.
    """
    pl_model = {
        "name": pl.String,
        "port": pl.Int64,
        "discovered_tool": pl.String,
        "discovered_time": pl.Datetime,
        "last_seen": pl.Datetime,
        "blacklisted": pl.Boolean,
        "info": pl.String,
    }

    old_domains = pl.DataFrame(strip_unncessary_columns(old_domains), schema=pl_model)
    found_domains = pl.DataFrame(
        found_domains,
        schema=pl_model,
    )

    if old_domains.is_empty():
        domains = found_domains
    elif found_domains.is_empty():
        domains = old_domains
    else:
        try:
            domains = clean_domain_name_pl(
                pl.concat([old_domains, found_domains], how="align")
            )
        except pl.exceptions.InvalidOperationError:
            domains = clean_domain_name_pl(pl.concat([old_domains, found_domains]))

    domains = domains.unique(subset=["name", "port"])

    bl = BlackList()
    domains = domains.with_columns(
        blacklisted=pl.col("name").map_elements(bl.check_blacklist, return_dtype=bool)
    )
    domains_list: List[Domain] = []
    for i in range(len(domains)):
        domains_list.append(
            Domain(
                name=domains["name"][i],
                port=domains["port"][i],
                discovered_tool=domains["discovered_tool"][i],
                discovered_time=domains["discovered_time"][i],
                last_seen=domains["last_seen"][i],
                blacklisted=domains["blacklisted"][i],
                info=domains["info"][i],
            )
        )

    return domains_list
