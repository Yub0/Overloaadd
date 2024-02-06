# Standard Library
import os
import shutil
import subprocess
from pydantic import ValidationError

# Third Party
import requests
from loguru import logger
from videoprops import get_video_properties

from overloaadd.dataclasses import IrilisConfiguration


def load_configuration(logger: logger) -> IrilisConfiguration:
    try:
        with open(os.path.join(os.getcwd(), "config.json"), "r") as file:
            config = file.read()
    except FileNotFoundError as exc:
        logger.error(f"The configuration file is missing: {exc}")
        exit(1)
    
    try:
        configuration = IrilisConfiguration.model_validate_json(config)
        logger.info("Configuration loaded successfully.")
        return configuration
    except ValidationError as exc:
        logger.error(f"The configuration file is invalid: {exc}")
        exit(1)


def download_file(url, output_path):
    local_filename = os.path.join(output_path, url.split("/")[-1])
    with requests.get(url, stream=True) as r:
        with open(local_filename, "wb") as f:
            shutil.copyfileobj(r.raw, f)

    return local_filename


def setup_handbrake(logger: logger) -> None:
    try:
        subprocess.run(
            ["HandBrakeCLI", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("HandbrakeCLI is not installed.")
        logger.error("Please install HandbrakeCLI. (brew install handbrake)")
        exit(1)
    else:
        logger.info("HandbrakeCLI is installed.")


def mount_juicefs(
    logger: logger, database_url: str, mount_point: str, bucket_name: str
) -> None:
    command = [
        "sudo",
        "juicefs",
        "mount",
        "-d",
        database_url,
        mount_point,
        "--get-timeout",
        "120",
        "--put-timeout",
        "120",
        "--io-retries",
        "20",
    ]

    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logger.info(f"JuiceFS mounted for {bucket_name} at {mount_point}")
    except subprocess.CalledProcessError as e:
        logger.error(f"JuiceFS mount failed: {e.stderr}")
        exit(1)


def encode_file(
    logger: logger, input_file: str, output_file: str, preset_name: str
) -> None:
    command = [
        "HandBrakeCLI",
        "-i",
        input_file,
        "-o",
        output_file,
        "--preset-import-file",
        os.path.join(os.getcwd(), "presets", f"{preset_name}.json"),
        "--preset",
        preset_name,
    ]

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        logger.info("File transcoded successfully")
    except subprocess.CalledProcessError as error:
        logger.error("Transcoding failed: {}".format(error.stderr))
        exit(1)


def clean_medias(logger: logger) -> None:
    logger.info("Cleaning medias directory.")
    shutil.rmtree(os.path.join(os.getcwd(), "medias"))
    os.makedirs(os.path.join(os.getcwd(), "medias"))
    logger.info("Medias directory cleaned.")


def is_already_encoded(logger: logger, file_path: str) -> bool:
    try:
        logger.debug(f"Getting video properties for {file_path}")
        video_properties = get_video_properties(file_path)
    except Exception as e:
        logger.error(f"Could not get video properties: {e}")
        return False

    if video_properties.get("codec_name") == "hevc":
        logger.info(f"{file_path} is already encoded.")
        return True
    else:
        return False
