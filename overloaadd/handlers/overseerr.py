# Standard Library
from typing import Optional

# Third Party
import requests
from loguru import logger


class Overseerr:
    """Overseerr service class."""

    def __init__(self, logger: logger, host: str, api_key: str):
        """Initialize Overseerr service.

        Args:
            logger: Instance of logger.
            host: Overseerr host.
            api_key: Overseerr API key.
        """
        self.logger = logger
        self.host = host
        self.api_key = api_key
        self.client = requests.Session()
        self.client.headers.update(
            {
                "X-Api-Key": self.api_key,
            }
        )
        self.prefix = "api/v1"

    def _connection(self) -> bool:
        """Check connection to Overseerr.

        Returns:
            True if connection is successful.
        """
        url = f"{self.host}/{self.prefix}/auth/me"
        response = self.client.get(url)
        response.raise_for_status()
        self.logger.debug("Overseerr connection successful.")
        return True

    def get_movie_requests(self) -> Optional[list]:
        """Get movie requests from Overseerr.

        Returns:
            List of movie requests.
        """
        url = f"{self.host}/{self.prefix}/request?take=1000&filter=unavailable&sort=added"
        logger.debug(f"Retrieving movie requests: {url}")
        response = self.client.get(url)
        response.raise_for_status()
        self.logger.debug("Movie requests retrieved.")
        results = response.json().get("results", [])

        return [result for result in results if result["type"] == "movie"]

    def get_movie_details(self, tmdb_id: int) -> Optional[dict]:
        """Get movie details from Overseerr.

        Args:
            tmdb_id: TheMovieDB ID.

        Returns:
            Movie details.
        """
        url = f"{self.host}/{self.prefix}/movie/{tmdb_id}"
        logger.debug(f"Retrieving movie details: {url}")
        response = self.client.get(url)
        response.raise_for_status()
        self.logger.debug("Movie details retrieved.")
        return response.json()
