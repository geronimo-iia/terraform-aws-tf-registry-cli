from logging import getLogger

from boto3 import client

from ..config import ApplicationConfig
from .model import TerraformModuleIdentifier

logger = getLogger()

__all__ = ["publish_module"]

# mypy: disable-error-code="arg-type"
def publish_module(
    config: ApplicationConfig, terraform_module: TerraformModuleIdentifier, version: str, source: str
) -> str:
    config.validate()
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
