import tarfile
import urllib.request
from logging import getLogger
from pathlib import Path

from boto3 import client

from ..config import ApplicationConfig
from .model import TerraformModuleIdentifier
from .publish import publish_module

logger = getLogger()


__all__ = ['release_module', 'send_s3_from_file', 'send_s3_from_dir', 'send_s3_from_url']

# mypy: disable-error-code="arg-type"
def release_module(
    config: ApplicationConfig, terraform_module: TerraformModuleIdentifier, version: str, source: str
) -> str:
    """Release a terraform module.

    Source could be:

    - a local folder (In this case local folder will be targzified).
    - an url which point to a targzified archive (like a git release)

    This source will be send to the default bucket and publish onto the registry.

    Args:

        config (ApplicationConfig): application configuration
        terraform_module (TerraformModuleIdentifier): module identifier
        version (str): version to publish
        source (str): module source

    Raise:
        (RuntimeError): if source did not exists
    """
    config.validate()
    # remove the v
    version = version if not version.lower().startswith("v") else version[1:]

    s3_key = terraform_module.get_bucket_key(version=version)
    logger.debug(f"Put module archive to {s3_key}")

    if source.lower().startswith("http"):
        send_s3_from_url(config=config, source_url=source, s3_key=s3_key)
    else:
        _source = Path(source)
        if not _source.exists():
            raise RuntimeError(f"Source {source} did not exists ")
        if _source.is_file():
            send_s3_from_file(config=config, archive_file=_source, s3_key=s3_key)

        send_s3_from_dir(config=config, archive_dir=_source, s3_key=s3_key)

    publish_url = terraform_module.get_publish_url(bucket_name=config.bucket_name, version=version)
    logger.debug(f"url: {publish_url}")
    publish_module(config=config, terraform_module=terraform_module, version=version, source=publish_url)

    return publish_url


def send_s3_from_file(config: ApplicationConfig, archive_file: str, s3_key: str):
    s3 = client('s3')
    with open(archive_file, "rb") as object_data:
        s3.put_object(Bucket=config.bucket_name, Key=s3_key, Body=object_data)


def send_s3_from_dir(config: ApplicationConfig, archive_dir: str, s3_key: str):
    archive_file = Path.cwd() / "archive.tar.gz"
    try:
        with tarfile.open(archive_file, "w:gz") as tar:
            tar.add(archive_dir, arcname=".", filter=lambda a: a if not a.name.startswith("./.") else None)
        send_s3_from_file(config=config, archive_file=archive_file, s3_key=s3_key)
    finally:
        archive_file.unlink()


def send_s3_from_url(config: ApplicationConfig, source_url: str, s3_key: str):
    opener = urllib.request.build_opener()
    archive_file = Path.cwd() / "archive.tar.gz"
    try:
        with open(archive_file, "wb") as archive:
            with opener.open(source_url) as object_data:
                archive.write(object_data.read())
        send_s3_from_file(config=config, archive_file=archive_file, s3_key=s3_key)
    finally:
        archive_file.unlink()
