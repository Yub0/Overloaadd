# Third Party
from tinydb import TinyDB

# First Party
from overloaadd.handlers import Overseerr, Transmission, Xthor
from overloaadd.helpers import load_configuration
from overloaadd.logger import logger

db = TinyDB("db.json")

configuration = load_configuration(logger)
transmission = Transmission(
    logger=logger,
    host=configuration.transmission.host,
    port=configuration.transmission.port,
    username=configuration.transmission.username,
    password=configuration.transmission.password,
)
overseerr = Overseerr(
    logger=logger,
    host=configuration.overseerr.host,
    api_key=configuration.overseerr.api_key,
)
xthor = Xthor(
    logger=logger,
    api_key=configuration.xthor.api_key,
)
