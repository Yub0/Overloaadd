# Standard Library
import os
import shutil

# Third Party
from tinydb import Query
from tinydb.table import Table

# First Party
from overloaadd import configuration, db, transmission
from overloaadd.dataclasses import Torrent
from overloaadd.helpers import (
    clean_medias,
    download_file,
    encode_file,
    is_already_encoded,
    mount_juicefs,
    setup_handbrake,
)
from overloaadd.logger import logger


def process(logger: logger, torrents: Table, torrent: dict) -> None:
    """Process torrent."""
    TorrentQuery = Query()

    transmission_torrent = transmission.get_torrent(torrent["torrent_id"])

    title = torrent.get("title")
    year = torrent.get("year")
    tmdb_id = torrent.get("tmdb_id")

    if transmission_torrent.progress == 100:
        logger.info(f"Processing {title}.")
        # Set torrent status to encoding.
        torrents.update(
            {"status": Torrent.TorrentStatus.ENCODING.value},
            TorrentQuery.torrent_id == torrent["torrent_id"],
        )

        clean_medias(logger)

        # Download torrent.
        logger.info(f"Downloading {title}.")
        files = transmission_torrent.get_files()

        # Get the biggest file.
        file = max(files, key=lambda file: file.size)

        downloaded_file = download_file(
            f"{file.name}",
            os.path.join(os.getcwd(), "medias"),
        )

        if not is_already_encoded(logger, downloaded_file):
            # Encode torrent.
            logger.info(f"Encoding {title}.")
            output_file_name = (
                f"{title} ({year}) {{tmdb-{tmdb_id}}} [IRILIS].mkv"
            )
            encode_file(
                logger,
                os.path.join(os.getcwd(), "medias", downloaded_file),
                os.path.join(os.getcwd(), "medias", output_file_name),
                "movie",
            )

        # Move to JUICEFS.
        logger.info(f"Moving {title} to JuiceFS Bucket.")
        shutil.move(
            os.path.join(os.getcwd(), "medias", output_file_name),
            os.path.join(
                os.getcwd(),
                "juicefs",
                configuration.juicefs_movie.bucket,
                output_file_name,
            ),
        )

        # Set torrent status to done.
        torrents.update(
            {"status": Torrent.TorrentStatus.DONE.value},
            TorrentQuery.torrent_id == torrent["torrent_id"],
        )


def entrypoint() -> None:
    """Encoder."""
    logger.info("Encoder started.")

    setup_handbrake(logger)

    # Mount movies bucket.
    mount_juicefs(
        logger,
        configuration.juicefs_movie.database,
        os.path.join(
            os.getcwd(), "juicefs", configuration.juicefs_movie.bucket
        ),
        configuration.juicefs_movie.bucket,
    )

    torrents = db.table("torrents")

    for torrent in torrents.search(
        Query().status == Torrent.TorrentStatus.ENCODING.value
    ):
        logger.warning(
            f"Torrent {torrent['title']} has not correctly "
            "finished the encoding process. "
            "Restarting."
        )
        process(logger, torrents, torrent)

    for torrent in torrents.search(
        Query().status == Torrent.TorrentStatus.DOWNLOADING.value
    ):
        process(logger, torrents, torrent)
