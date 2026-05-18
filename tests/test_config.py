import pytest
import yaml

from aws_terraform_registry.config import ApplicationConfig


def _valid_config(**overrides) -> ApplicationConfig:
    defaults = {
        "secret_key_name": "my-secret",
        "repository_url": "https://registry.example.com",
        "dynamodb_table_name": "tf-modules",
        "bucket_name": "tf-bucket",
        "default_namespace": "devops",
    }
    defaults.update(overrides)
    return ApplicationConfig(**defaults)


class TestValidate:
    def test_valid_config(self):
        _valid_config().validate()

    @pytest.mark.parametrize("field", ["secret_key_name", "repository_url", "dynamodb_table_name", "bucket_name"])
    def test_missing_field_raises(self, field):
        config = _valid_config(**{field: None})
        with pytest.raises(RuntimeError, match=field):
            config.validate()


class TestPostInit:
    def test_strips_trailing_slash(self):
        config = _valid_config(repository_url="https://registry.example.com/")
        assert config.repository_url == "https://registry.example.com"

    def test_no_trailing_slash_unchanged(self):
        config = _valid_config(repository_url="https://registry.example.com")
        assert config.repository_url == "https://registry.example.com"


class TestLoadFrom:
    def test_loads_yaml(self, tmp_path):
        data = {
            "secret_key_name": "secret",
            "repository_url": "https://reg.test",
            "dynamodb_table_name": "table",
            "bucket_name": "bucket",
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.safe_dump(data))

        config = ApplicationConfig.load_from(config_file)
        assert config.secret_key_name == "secret"
        assert config.repository_url == "https://reg.test"
        assert config.dynamodb_table_name == "table"
        assert config.bucket_name == "bucket"


class TestLookup:
    def test_returns_default_when_no_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path / "nope")
        monkeypatch.chdir(tmp_path)
        config = ApplicationConfig.lookup()
        assert config.secret_key_name is None

    def test_loads_from_cwd(self, tmp_path, monkeypatch):
        data = {
            "secret_key_name": "found",
            "repository_url": "https://r.test",
            "dynamodb_table_name": "t",
            "bucket_name": "b",
        }
        (tmp_path / "terraform_registry.yaml").write_text(yaml.safe_dump(data))
        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path / "nope")
        monkeypatch.chdir(tmp_path)
        config = ApplicationConfig.lookup()
        assert config.secret_key_name == "found"
