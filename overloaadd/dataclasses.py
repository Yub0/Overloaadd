# Standard Library
from enum import Enum

# Third Party
from pydantic import BaseModel, HttpUrl


class TransmissionConfiguration(BaseModel):
    """Transmission configuration dataclass."""

    host: str
    port: int
    username: str
    password: str


class NginxConfiguration(BaseModel):
    """Nginx configuration dataclass."""

    host: str


class OverseerrConfiguration(BaseModel):
    """Overseerr configuration dataclass."""

    host: HttpUrl
    api_key: str


class XthorConfiguration(BaseModel):
    """Xthor configuration dataclass."""

    api_key: str


class JuiceFSConfiguration(BaseModel):
    """JuiceFS configuration dataclass."""

    database: str
    bucket: str


class IrilisConfiguration(BaseModel):
    """Irilis configuration dataclass."""

    transmission: TransmissionConfiguration
    nginx: NginxConfiguration
    overseerr: OverseerrConfiguration
    xthor: XthorConfiguration
    juicefs_movie: JuiceFSConfiguration


class Torrent(BaseModel):
    """Torrent dataclass."""

    class TorrentStatus(str, Enum):
        """Torrent status enum."""

        DOWNLOADING = "downloading"
        ENCODING = "encoding"
        DONE = "done"

    torrent_id: int
    tmdb_id: int
    title: str
    year: int | None
    status: TorrentStatus = TorrentStatus.DOWNLOADING
