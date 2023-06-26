from aws_terraform_registry.cli import build_parser, main
from aws_terraform_registry.config import ApplicationConfig


def test_build_parser():
    assert main
    assert build_parser
    parser = build_parser(config=ApplicationConfig.lookup())
    assert parser


def test_cli_config():
    parser = build_parser(config=ApplicationConfig.lookup())
    assert "func" in parser.parse_args(["config"])


def test_cli_terraformrc():
    parser = build_parser(config=ApplicationConfig.lookup())
    assert "func" in parser.parse_args(["generate-terraformrc", "--output-directory", "myhome"])

    assert "func" in parser.parse_args(["generate-terraformrc", "--output-directory", "myhome", "--weeks", "1"])


def test_cli_token():
    parser = build_parser(config=ApplicationConfig.lookup())
    assert "func" in parser.parse_args(["generate-token"])

    assert "func" in parser.parse_args(["generate-token", "--weeks", "1"])


def test_cli_publish():
    parser = build_parser(config=ApplicationConfig.lookup())
    assert "func" in parser.parse_args(
        [
            "publish",
            "--namespace",
            "devops",
            "--name",
            "kms",
            "--system",
            "aws",
            "--version",
            "1.0.0",
            "--source",
            "https:://oneuponatime.inaland.com",
        ]
    )


def test_cli_unpublish():
    parser = build_parser(config=ApplicationConfig.lookup())
    assert "func" in parser.parse_args(
        [
            "unpublish",
            "--namespace",
            "devops",
            "--name",
            "kms",
            "--system",
            "aws",
            "--version",
            "1.0.0",
        ]
    )


def test_cli_release():
    parser = build_parser(config=ApplicationConfig.lookup())
    assert "func" in parser.parse_args(
        [
            "release",
            "--namespace",
            "devops",
            "--name",
            "kms",
            "--system",
            "aws",
            "--version",
            "1.0.0",
            "--source",
            "https:://oneuponatime.inaland.com",
        ]
    )
