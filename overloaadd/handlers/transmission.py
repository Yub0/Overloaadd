# Standard Library
from typing import Optional

# Third Party
from loguru import logger
from transmission_rpc import Client, Torrent
from transmission_rpc.error import (
    TransmissionAuthError,
    TransmissionConnectError,
)


class Transmission:
    """Transmission service class."""

    def __init__(
        self,
        logger: logger,
        host: str,
        port: int,
        username: str,
        password: str,
    ):
        """Initialize Transmission service.

        Args:
            logger: Instance of logger.
            host: Transmission host.
            port: Transmission port.
            username: Transmission username.
            password: Transmission password.
        """
        self.logger = logger
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client = Optional[Client]
        self.logger.info("Transmission service initialized.")

    def _create_client(self) -> Client:
        """Create Transmission client.

        Returns:
            Transmission client.
        """
        try:
            self.client = Client(
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
            )
            self.logger.debug("Transmission client created.")
            return self.client
        except TransmissionAuthError as exc:
            msg = (
                "Transmission authentication error. Please check credentials."
                f"{str(exc)}"
            )
        except TransmissionConnectError as exc:
            msg = (
                f"Transmission connection error. Please check host and port."
                f"{str(exc)}"
            )

        raise Exception(msg)

    def _connection(self) -> Client:
        """Connect to Transmission service.

        Returns:
            Transmission client.
        """
        try:
            self.client.get_session()
            self.logger.debug(
                "Transmission client already connected. "
                "Re-using the active connection."
            )
            return self.client
        except (AttributeError, TransmissionConnectError):
            # No client or active connection.
            self.logger.debug("No active connection to Transmission.")
            pass

        return self._create_client()

    def add_torrent(self, torrent: str) -> int:
        """Add torrent to Transmission service.

        Args:
            torrent: Magnet link, torrent url or torrent file path.

        Returns:
            Torrent id.
        """
        self.logger.debug(f"Adding torrent: {torrent}")
        if added_torrent := self._connection().add_torrent(torrent):
            self.logger.info(f"Torrent added: {torrent}")
            return added_torrent.id

    def get_torrent(self, torrent_id: int) -> Torrent:
        """Get torrent from Transmission service.

        Args:
            torrent_id: Torrent id.
        """
        self.logger.debug(f"Getting torrent: {torrent_id}")
        if torrent := self._connection().get_torrent(torrent_id):
            self.logger.info(f"Torrent found: {torrent_id}")
            return torrent

    def get_completed_torrents(self) -> list[Torrent]:
        """Get completed torrents from Transmission service.

        Returns:
            List of completed torrents.
        """
        self.logger.debug("Getting completed torrent(s).")
        if completed_torrents := self._connection().get_torrents():
            self.logger.debug("Torrent(s) found, filtering the results.")
            torrents = [
                torrent
                for torrent in completed_torrents
                if torrent.progress == 100
            ]
            self.logger.info(f"{len(torrents)} torrent(s) found.")
            return torrents
