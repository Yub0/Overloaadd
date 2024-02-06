# Standard Library
from time import sleep

# First Party
from overloaadd.encoder import entrypoint as encoder_entrypoint
from overloaadd.logger import logger
from overloaadd.watcher import entrypoint as watcher_entrypoint


def encoder() -> None:
    """Encoder entrypoint."""
    try:
        while True:
            encoder_entrypoint()
            logger.info("Sleeping for 15 seconds.")
            sleep(15)
    except KeyboardInterrupt:
        logger.info("Watcher stopped by user.")
        exit(0)
    except Exception as exc:
        logger.error(f"Encoder crashed: {exc}")
        exit(1)


def watcher() -> None:
    """Watcher entrypoint."""
    try:
        while True:
            watcher_entrypoint()
            logger.info("Sleeping for 15 seconds.")
            sleep(15)
    except KeyboardInterrupt:
        logger.info("Watcher stopped by user.")
        exit(0)
    except Exception as exc:
        logger.error(f"Watcher crashed: {exc}")
        exit(1)
