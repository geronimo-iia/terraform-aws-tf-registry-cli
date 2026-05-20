"""Unit tests configuration file."""

import logging
import os

import pytest


def pytest_configure(config):
    """Disable verbose output when running tests."""
    _logger = logging.getLogger()
    _logger.setLevel(logging.DEBUG)

    terminal = config.pluginmanager.getplugin("terminal")
    terminal.TerminalReporter.showfspath = False


@pytest.fixture(autouse=True)
def _clean_tfr_env(monkeypatch):
    """Remove TFR_* environment variables so they don't interfere with tests."""
    for key in list(os.environ):
        if key.startswith("TFR_"):
            monkeypatch.delenv(key)
