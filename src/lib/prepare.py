import logging
import os

from dotenv import load_dotenv
from lib.models import Domains, Scanned
from sqlalchemy import Engine, create_engine


def prepare_db_struct(engine: Engine) -> None:
    Domains.metadata.create_all(engine)
    Scanned.metadata.create_all(engine)
    logging.info("Tables created")


def get_env_var(name: str) -> str:
    x = os.getenv(name)
    if x is None:
        logging.error(f"Environment variable {name} is not set")
        raise Exception(f"Environment variable {name} is not set")
    return x


def init_engine() -> Engine:
    load_dotenv()

    if (conn_str := get_env_var("DB_CONN_STR")) != "":
        engine = create_engine(conn_str)
    else:
        engine = create_engine(
            "postgresql://"
            + get_env_var("DB-USER")
            + ":"
            + get_env_var("DB-PASSWORD")
            + "@"
            + get_env_var("DB-HOST")
            + "/"
            + get_env_var("DB-NAME")
        )

    logging.info("Engine created")
    return engine


def prepare_db():
    engine = init_engine()
    prepare_db_struct(engine)
    return engine
