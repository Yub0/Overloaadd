# Standard Library
from datetime import datetime, timedelta
from time import sleep

# Third Party
from tinydb import Query

# First Party
from overloaadd import db, overseerr, transmission, xthor
from overloaadd.dataclasses import Torrent
from overloaadd.logger import logger


def entrypoint() -> None:
    """Watcher entrypoint."""
    requests = overseerr.get_movie_requests()

    for request in requests:
        # Get movie details.
        tmdb_id = request.get("media", {}).get("tmdbId")
        movie = overseerr.get_movie_details(tmdb_id)
        title = movie.get("originalTitle") or movie.get("title")
        try:
            release_date = datetime.strptime(
                movie.get("releaseDate"), "%Y-%m-%d"
            )
        except (ValueError, TypeError):
            release_date = None
        current_date_with_delta = datetime.now() + timedelta(days=7)

        # Check if movie is released.
        if release_date is None or release_date > current_date_with_delta:
            logger.debug(f"Movie {title} is not released yet.")
            continue

        TorrentQuery = Query()
        # Check if request is already in database.
        if db.table("torrents").search(TorrentQuery.tmdb_id == tmdb_id):
            logger.debug(f"Request already in database: {title}.")
            continue

        # Search for torrent.
        sleep(2.5)
        if (torrent_link := xthor.search_movie(tmdb_id, title)) is None:
            logger.warning(f"No torrent found for {title}.")
            continue

        # Add torrent to Transmission.
        if torrent := transmission.add_torrent(torrent_link):
            logger.info(f"Torrent added: {torrent}")

            torrent = Torrent(
                torrent_id=torrent,
                tmdb_id=tmdb_id,
                title=title,
                year=release_date.year,
            )

            db.table("torrents").insert(torrent.model_dump())

            logger.info(f"Torrent added to database: {torrent}")
        else:
            logger.error(f"Failed to add torrent: {torrent_link}")

    logger.info("Watcher finished.")
