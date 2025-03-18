"""
This is example of module that will be loaded by domain_discovery.py
"""
from lib.models import Domain
from datetime import datetime

def main() -> list[Domain]:
    domain = Domain(
        name="example.com",
        port=443,
        discovered_tool="example",
        discovered_time=datetime.now(),
        last_seen=datetime.now(),
        blacklisted=False,
        info="Example domain"
    )
    return [domain]
