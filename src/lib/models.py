from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.schema import ForeignKeyConstraint


@dataclass
class Domain:
    name: str
    port: int
    discovered_tool: str
    discovered_time: datetime
    last_seen: datetime
    blacklisted: bool
    # optional info
    info: str = ""


class Base(DeclarativeBase):
    # https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html#step-one-orm-declarative-base-is-superseded-by-orm-declarativebase
    pass


class Domains(Base):
    __tablename__ = "domains"
    name = Column(String, primary_key=True)
    port = Column(Integer, primary_key=True)
    discovered_tool = Column(String)
    discovered_time = Column(DateTime)
    last_seen = Column(DateTime)
    blacklisted = Column(Boolean)
    info = Column(String, nullable=True)


class Scanned(Base):
    # This table is used to store information about scans from different tools
    __tablename__ = "scan_info"
    name = Column(String, primary_key=True)
    port = Column(Integer, primary_key=True)
    scan_id = Column(String)
    timestamp = Column(DateTime, primary_key=True)
    info = Column(String, nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(["name", "port"], ["domains.name", "domains.port"]),
    )
