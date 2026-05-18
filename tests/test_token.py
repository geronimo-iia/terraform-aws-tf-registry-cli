import datetime
from base64 import b64encode
from unittest.mock import MagicMock

import jwt
import pytest

from aws_terraform_registry.common.token import generate_terraformrc, generate_token, get_secret
from aws_terraform_registry.config import ApplicationConfig


@pytest.fixture
def config():
    return ApplicationConfig(
        secret_key_name="my-secret-key",
        repository_url="https://registry.example.com",
        dynamodb_table_name="tf-modules",
        bucket_name="tf-bucket",
    )


@pytest.fixture
def mock_secretsmanager(mocker):
    mock = MagicMock()
    mocker.patch("aws_terraform_registry.common.token.secretsmanager", return_value=mock)
    return mock


class TestGetSecret:
    def test_returns_secret_string(self, mock_secretsmanager):
        mock_secretsmanager.get_secret_value.return_value = {"SecretString": "my-jwt-secret"}
        assert get_secret("key-name") == "my-jwt-secret"

    def test_returns_decoded_binary(self, mock_secretsmanager):
        binary_secret = b"binary-secret"
        mock_secretsmanager.get_secret_value.return_value = {"SecretBinary": b64encode(binary_secret)}
        result = get_secret("key-name")
        assert "binary-secret" in result


class TestGenerateToken:
    def test_returns_valid_jwt(self, config, mock_secretsmanager):
        mock_secretsmanager.get_secret_value.return_value = {"SecretString": "test-secret"}

        token = generate_token(config=config, weeks=2)

        decoded = jwt.decode(token, "test-secret", algorithms=["HS256"])
        assert "exp" in decoded
        exp = datetime.datetime.fromtimestamp(decoded["exp"], tz=datetime.UTC)
        assert exp > datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=13)

    def test_validates_config(self, mock_secretsmanager):
        config = ApplicationConfig()  # missing required fields
        with pytest.raises(RuntimeError):
            generate_token(config=config)


class TestGenerateTerraformrc:
    def test_writes_correct_file(self, config, mock_secretsmanager, tmp_path):
        mock_secretsmanager.get_secret_value.return_value = {"SecretString": "test-secret"}

        generate_terraformrc(config=config, output_directory=str(tmp_path), weeks=1)

        rc_file = tmp_path / ".terraformrc"
        assert rc_file.exists()
        content = rc_file.read_text()
        assert 'credentials "registry.example.com"' in content
        assert "token = " in content

    def test_extracts_hostname_without_protocol(self, config, mock_secretsmanager, tmp_path):
        mock_secretsmanager.get_secret_value.return_value = {"SecretString": "s"}

        generate_terraformrc(config=config, output_directory=str(tmp_path))

        content = (tmp_path / ".terraformrc").read_text()
        assert "https://" not in content.split("credentials")[1]
        assert "registry.example.com" in content
