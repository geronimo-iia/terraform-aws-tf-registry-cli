from unittest.mock import MagicMock

import pytest

from aws_terraform_registry.common.model import TerraformModuleIdentifier
from aws_terraform_registry.common.publish import exists, publish_module, unpublish_module
from aws_terraform_registry.config import ApplicationConfig


@pytest.fixture
def config():
    return ApplicationConfig(
        secret_key_name="secret",
        repository_url="https://registry.example.com",
        dynamodb_table_name="tf-modules",
        bucket_name="tf-bucket",
    )


@pytest.fixture
def tf_module():
    return TerraformModuleIdentifier(namespace="devops", name="kms", system="aws")


@pytest.fixture
def mock_dynamodb(mocker):
    mock = MagicMock()
    mocker.patch("aws_terraform_registry.common.publish.dynamodb", return_value=mock)
    return mock


class TestExists:
    def test_returns_true_when_item_present(self, config, tf_module, mock_dynamodb):
        mock_dynamodb.get_item.return_value = {"Item": {"Id": {"S": "devops/kms/aws"}, "Version": {"S": "1.0.0"}}}
        assert exists(config=config, terraform_module=tf_module, version="1.0.0") is True

    def test_returns_false_when_no_item(self, config, tf_module, mock_dynamodb):
        mock_dynamodb.get_item.return_value = {}
        assert exists(config=config, terraform_module=tf_module, version="1.0.0") is False


class TestPublishModule:
    def test_happy_path(self, config, tf_module, mock_dynamodb):
        mock_dynamodb.get_item.return_value = {}
        result = publish_module(config=config, terraform_module=tf_module, version="1.0.0", source="s3://my-source")

        assert result == "s3://my-source"
        mock_dynamodb.put_item.assert_called_once_with(
            TableName="tf-modules",
            Item={
                "Id": {"S": "devops/kms/aws"},
                "Version": {"S": "1.0.0"},
                "Source": {"S": "s3://my-source"},
            },
        )

    def test_raises_if_already_exists(self, config, tf_module, mock_dynamodb):
        mock_dynamodb.get_item.return_value = {"Item": {}}
        with pytest.raises(RuntimeError, match="ever exist"):
            publish_module(config=config, terraform_module=tf_module, version="1.0.0", source="s3://x")


class TestUnpublishModule:
    def test_happy_path(self, config, tf_module, mock_dynamodb):
        mock_dynamodb.get_item.return_value = {"Item": {}}
        unpublish_module(config=config, terraform_module=tf_module, version="1.0.0")

        mock_dynamodb.delete_item.assert_called_once_with(
            TableName="tf-modules",
            Key={"Id": {"S": "devops/kms/aws"}, "Version": {"S": "1.0.0"}},
        )

    def test_raises_if_not_exists(self, config, tf_module, mock_dynamodb):
        mock_dynamodb.get_item.return_value = {}
        with pytest.raises(RuntimeError, match="did not exist"):
            unpublish_module(config=config, terraform_module=tf_module, version="1.0.0")
