from logging import getLogger

from boto3 import client

from ..config import ApplicationConfig
from .model import TerraformModuleIdentifier

logger = getLogger()

__all__ = ["publish_module", "exists"]


# mypy: disable-error-code="arg-type"
def publish_module(
    config: ApplicationConfig, terraform_module: TerraformModuleIdentifier, version: str, source: str
) -> str:
    """Publish terraform module.

    Args:

        config (ApplicationConfig): application configuration
        terraform_module (TerraformModuleIdentifier): module identifier
        version (str): version to publish
        source (str): module source

    Returns:
        str: source

    Raises:
        (RuntimeError): if specified version and module is ever published.
    """
    config.validate()

    if exists(config=config, terraform_module=terraform_module, version=version):
        msg = f"Version {version} for module {terraform_module.module_id} ever exist"
        logger.error(msg)
        raise RuntimeError(msg)

    client('dynamodb').put_item(
        TableName=config.dynamodb_table_name,
        Item={
            "Id": {"S": terraform_module.module_id},
            "Version": {"S": version},
            "Source": {"S": source},
        },
    )
    logger.info(f"Published module {terraform_module.module_id}, Version {version}, Source {source}")
    return source


# mypy: disable-error-code="arg-type"
def unpublish_module(config: ApplicationConfig, terraform_module: TerraformModuleIdentifier, version: str):
    """UnPublish terraform module.

    Args:

        config (ApplicationConfig): application configuration
        terraform_module (TerraformModuleIdentifier): module identifier
        version (str): version to publish


    Raises:
        (RuntimeError): if specified version and module did not exists.
    """
    config.validate()

    if not exists(config=config, terraform_module=terraform_module, version=version):
        msg = f"Version {version} for module {terraform_module.module_id} did not exist"
        logger.error(msg)
        raise RuntimeError(msg)

    client('dynamodb').delete_item(
        TableName=config.dynamodb_table_name,
        Key={
            "Id": {"S": terraform_module.module_id},
            "Version": {"S": version},
        },
    )
    logger.info(f"Unpublished module {terraform_module.module_id}, Version {version}")


def exists(config: ApplicationConfig, terraform_module: TerraformModuleIdentifier, version: str) -> bool:
    dynamodb_client = client("dynamodb")
    response = dynamodb_client.get_item(
        TableName=config.dynamodb_table_name, Key={'Id': {'S': terraform_module.module_id}, 'Version': {'S': version}}
    )
    return 'Item' in response
