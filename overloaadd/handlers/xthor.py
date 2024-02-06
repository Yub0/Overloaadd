# Standard Library
from time import sleep
from typing import Optional

# Third Party
import jellyfish
import requests
from loguru import logger


class Xthor:
    """Xthor service class."""

    def __init__(self, logger: logger, api_key: str):
        """Initialize Xthor service.

        Args:
            logger: Instance of logger.
            host: Overseerr host.
            api_key: Overseerr API key.
        """
        self.logger = logger
        self.host = "https://api.xthor.tk"
        self.api_key = api_key
        self.client = requests.Session()

    def search_movie(self, tmdb_id: int, title: str) -> Optional[str]:
        link = f"{self.host}?passkey={self.api_key}&tmdbid={tmdb_id}"
        logger.info(f"Searching for {title} on Xthor.")
        logger.debug(f"Requesting {link}.")
        response = self.client.get(link)

        if response.status_code != 200:
            self.logger.error(f"Failed to search for {title}.")
            return None

        data = response.json().get("torrents", [])
        data = [
            x
            for x in data
            if jellyfish.jaro_winkler_similarity(x["name"], title) >= 0.7
        ]

        # Sort torrents by weight.
        # TODO: Implement a better sorting algorithm.

        # Remove all files not containing "MULTi", you can lower the name to compare with.
        data = [
            x
            for x in data
            if "MULTi" in x["name"]
            or "MULTI" in x["name"]
            or "multi" in x["name"]
        ]

        if data:
            self.logger.info(f"Found a torrent for {title}.")
            return max(data, key=lambda x: int(x["times_completed"])).get(
                "download_link"
            )
        else:
            self.logger.warning(f"No torrents found for {title}.")
            return None
