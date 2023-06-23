import os
import sys
from dataclasses import asdict, dataclass
from logging import getLogger
from pathlib import Path
from typing import Optional, Union

import yaml
from envclasses import envclass, load_env

logger = getLogger()

__ALL__ = ["ApplicationConfig"]

_CONFIG_NAME = "terraform_registry.yaml"


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

    secret_key_name: Optional[str] = None
    repository_url: Optional[str] = None
    dynamodb_table_name: Optional[str] = None
    bucket_name: Optional[str] = None
    default_namespace: str = "devops"

    def __post_init__(self):
        """Finalize configuration.

        Feed attributs from TFR_xxxx env variable if exists.
        """
        # Feed from env var
        load_env(self, prefix='tfr')

    def validate(self):
        """Validate each attributs.

        Raise:
            (RuntimeError): if an attribut is empty

        """
        for name in ['secret_key_name', 'repository_url', 'dynamodb_table_name', 'bucket_name', 'default_namespace']:
            if not getattr(self, name):
                logger.error(f"Configuration ERROR: '{name}' parameter is missing")
                raise RuntimeError(f"Configuration ERROR: '{name}' parameter is missing")

    def show(self):
        yaml.safe_dump(asdict(self), sys.stdout)

    @classmethod
    def lookup(clazz, config_file_name: Optional[str] = None) -> 'ApplicationConfig':
        # define config file name
        config_file_name = config_file_name if config_file_name else os.environ.get('TFR_CONFIG_FILE', _CONFIG_NAME)

        # lookup
        for path in [Path.home(), Path.cwd(), Path('/etc/tfr')]:
            config_path = path / config_file_name
            if config_path.exists():
                return ApplicationConfig.load_from(filename=config_path)

        return ApplicationConfig()

    @classmethod
    def load_from(clazz, filename: Union[Path, str]) -> 'ApplicationConfig':
        """Load ApplicationConfig from a yaml file."""
        with open(filename) as f:
            return clazz(**yaml.safe_load(f.read()))
