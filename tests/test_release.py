from unittest.mock import MagicMock

import pytest

from aws_terraform_registry.common.model import TerraformModuleIdentifier
from aws_terraform_registry.common.release import release_module, send_s3_from_dir, send_s3_from_file
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
def mock_s3(mocker):
    mock = MagicMock()
    mocker.patch("aws_terraform_registry.common.release.s3", return_value=mock)
    return mock


@pytest.fixture
def mock_dynamodb(mocker):
    mock = MagicMock()
    mocker.patch("aws_terraform_registry.common.publish.dynamodb", return_value=mock)
    return mock


class TestReleaseModule:
    def test_strips_v_prefix(self, config, tf_module, mock_s3, mock_dynamodb, mocker):
        mock_dynamodb.get_item.return_value = {}
        mocker.patch("aws_terraform_registry.common.release.send_s3_from_url")
        mocker.patch("aws_terraform_registry.common.model._find_caller_region", return_value="eu-west-1")

        result = release_module(
            config=config, terraform_module=tf_module, version="v2.0.0", source="https://example.com/mod.tar.gz"
        )

        assert "2.0.0" in result
        assert "v2.0.0" not in result

    def test_raises_if_already_exists(self, config, tf_module, mock_s3, mock_dynamodb):
        mock_dynamodb.get_item.return_value = {"Item": {}}
        with pytest.raises(RuntimeError, match="ever exist"):
            release_module(config=config, terraform_module=tf_module, version="1.0.0", source="https://x.com/a.tar.gz")

    def test_raises_if_source_not_exists(self, config, tf_module, mock_s3, mock_dynamodb):
        mock_dynamodb.get_item.return_value = {}
        with pytest.raises(RuntimeError, match="did not exists"):
            release_module(config=config, terraform_module=tf_module, version="1.0.0", source="/nonexistent/path")

    def test_with_http_source(self, config, tf_module, mock_s3, mock_dynamodb, mocker):
        mock_dynamodb.get_item.return_value = {}
        mock_send_url = mocker.patch("aws_terraform_registry.common.release.send_s3_from_url")
        mocker.patch("aws_terraform_registry.common.model._find_caller_region", return_value="eu-west-1")

        release_module(
            config=config, terraform_module=tf_module, version="1.0.0", source="https://github.com/mod.tar.gz"
        )

        mock_send_url.assert_called_once()

    def test_with_local_file(self, config, tf_module, mock_s3, mock_dynamodb, mocker, tmp_path):
        mock_dynamodb.get_item.return_value = {}
        mocker.patch("aws_terraform_registry.common.model._find_caller_region", return_value="eu-west-1")

        archive = tmp_path / "module.tar.gz"
        archive.write_bytes(b"fake archive")

        result = release_module(config=config, terraform_module=tf_module, version="1.0.0", source=str(archive))

        mock_s3.put_object.assert_called_once()
        assert "s3::" in result

    def test_with_local_directory(self, config, tf_module, mock_s3, mock_dynamodb, mocker, tmp_path, monkeypatch):
        mock_dynamodb.get_item.return_value = {}
        mocker.patch("aws_terraform_registry.common.model._find_caller_region", return_value="eu-west-1")
        monkeypatch.chdir(tmp_path)

        source_dir = tmp_path / "mymodule"
        source_dir.mkdir()
        (source_dir / "main.tf").write_text("resource {}")

        result = release_module(config=config, terraform_module=tf_module, version="1.0.0", source=str(source_dir))

        mock_s3.put_object.assert_called_once()
        assert "s3::" in result


class TestSendS3FromFile:
    def test_uploads_file(self, config, mock_s3, tmp_path):
        archive = tmp_path / "test.tar.gz"
        archive.write_bytes(b"content")

        send_s3_from_file(config=config, archive_file=archive, s3_key="ns/mod/aws/1.0.0/archive.tar.gz")

        mock_s3.put_object.assert_called_once()
        call_kwargs = mock_s3.put_object.call_args[1]
        assert call_kwargs["Bucket"] == "tf-bucket"
        assert call_kwargs["Key"] == "ns/mod/aws/1.0.0/archive.tar.gz"


class TestSendS3FromDir:
    def test_creates_tar_and_uploads(self, config, mock_s3, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        source_dir = tmp_path / "src"
        source_dir.mkdir()
        (source_dir / "main.tf").write_text("resource {}")

        send_s3_from_dir(config=config, archive_dir=source_dir, s3_key="key/archive.tar.gz")

        mock_s3.put_object.assert_called_once()
        # temp file should be cleaned up
        assert not (tmp_path / "archive.tar.gz").exists()
