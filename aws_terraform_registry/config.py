import os
import sys
from dataclasses import asdict, dataclass
from functools import lru_cache
from logging import getLogger
from pathlib import Path

import yaml
from boto3 import client
from envclasses import envclass, load_env

logger = getLogger()

__ALL__ = ["ApplicationConfig", "dynamodb", "secretsmanager", "s3"]

_CONFIG_NAME = "terraform_registry.yaml"


@lru_cache
def dynamodb():
    """Return a cached DynamoDB client."""
    region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
    return client("dynamodb", region_name=region)


@lru_cache
def s3():
    """Return a cached S3 client."""
    region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
    return client("s3", region_name=region)


@lru_cache
def secretsmanager():
    """Return a cached Secrets Manager client."""
    region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
    return client("secretsmanager", region_name=region)


@envclass
@dataclass
class ApplicationConfig:
    """Define aws terraform private registry parameters.


    Attributes:

        secret_key_name (str): AWS Secret manager name where JWT Secret is stored
        repository_url (str): HTTPS endpoint of the registry
        dynamodb_table_name (str): dynamodb table name
        bucket_name (str): bucket name
        default_namespace: default namespace to publish terrafor module ("devops" per default)
    """

    secret_key_name: str | None = None
    repository_url: str | None = None
    dynamodb_table_name: str | None = None
    bucket_name: str | None = None
    default_namespace: str = "devops"

    def __post_init__(self):
        """Finalize configuration.

        Feed attributs from TFR_xxxx env variable if exists.
        """
        # Feed from env var
        load_env(self, prefix="tfr")

        # remove ending '/'
        if self.repository_url and self.repository_url.endswith("/"):
            self.repository_url = self.repository_url[0:-1]

    def validate(self):
        """Validate each attributs.

        Raise:
            (RuntimeError): if an attribut is empty

        """
        for name in ["secret_key_name", "repository_url", "dynamodb_table_name", "bucket_name", "default_namespace"]:
            if not getattr(self, name):
                logger.error(f"Configuration ERROR: '{name}' parameter is missing")
                raise RuntimeError(f"Configuration ERROR: '{name}' parameter is missing")

    def show(self):
        yaml.safe_dump(asdict(self), sys.stdout)

    @classmethod
    def lookup(cls, config_file_name: str | None = None) -> "ApplicationConfig":
        # define config file name
        config_file_name = config_file_name if config_file_name else os.environ.get("TFR_CONFIG_FILE", _CONFIG_NAME)

        # lookup
        for path in [Path.home(), Path.cwd(), Path("/etc/tfr")]:
            config_path = path / config_file_name
            if config_path.exists():
                return ApplicationConfig.load_from(filename=config_path)

        return ApplicationConfig()

    @classmethod
    def load_from(cls, filename: Path | str) -> "ApplicationConfig":
        """Load ApplicationConfig from a yaml file."""
        with open(filename) as f:
            return cls(**yaml.safe_load(f.read()))
