import datetime
import os
from base64 import b64decode

import jwt
from boto3 import client

from ..config import ApplicationConfig

__all__ = ["generate_token", "generate_terraformrc", "get_secret"]

# mypy: disable-error-code="arg-type"
def generate_token(config: ApplicationConfig, weeks: int = 1) -> str:
    """Generate a JWT tokecm.

    Args:
        config (ApplicationConfig): application configuration.
        weeks (int, optional): weeks of validity (1 per default).

    Returns:
        str: encoded jwt token
    """
    config.validate()
    token = get_secret(secret_key_name=config.secret_key_name)
    return jwt.encode(
        {"exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(weeks=weeks)},
        token,
        algorithm="HS256",
    )


# mypy: disable-error-code="arg-type"
def generate_terraformrc(config: ApplicationConfig, output_directory: str, weeks: int = 52):
    """Generate terraform_rc file.

    Args:
        config (ApplicationConfig): application configuration.
        output_directory (str): directory where to wrote the .terraform_rc.
        weeks (int, optional): weeks of validity (52 per default).

    """
    config.validate()
    repository_url = str(config.repository_url)  # avoid mypi error: this could not be null
    hostmane = repository_url[repository_url.index("://") + 3 : -1]
    with open(os.path.join(output_directory, ".terraformrc"), "w") as f:
        f.write(
            f"""
credentials "{hostmane}" {{
    token = "{generate_token(config=config, weeks=weeks)}"
}}
"""
        )


def get_secret(secret_key_name: str):
    secret_value_response = client('secretsmanager').get_secret_value(SecretId=secret_key_name)
    return (
        secret_value_response["SecretString"]
        if "SecretString" in secret_value_response
        else str(b64decode(secret_value_response["SecretBinary"]))
    )
