import logging
import sys


def setup_logger(log_file: str) -> bool:
    try:
        with open(log_file, "a") as f:
            f.write("Log file initialized\n")

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
        )
    except Exception as e:
        print(f"Error while setting up logger: {e}")
        logging.error(f"Error while setting up logger: {e}")
        exit(1)
