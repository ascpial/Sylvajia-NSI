from __future__ import annotations
from typing import TYPE_CHECKING

from pathlib import Path
import json

from src.configuration import Configuration
from src import configuration

def get_configuration(tmpdir, dict_test) -> Configuration:
    tmpdir = Path(tmpdir)
    config = tmpdir / "configuration.json"
    config.write_text(
        json.dumps(
            dict_test
        ),

    )
    configuration.CONFIGURATION_FILE = str(config)

    config = Configuration()

    return config

class TestConfiguration:
    def test_application_id(self, tmpdir):
        config = get_configuration(
            tmpdir,
            dict_test = {
                "application_id": 794563716710957096,
                "version": "v0.0.1-alpha"
            }
        )
        assert config.application_id == 794563716710957096
    
    def test_version(self, tmpdir):
        config = get_configuration(
            tmpdir,
            dict_test = {
                "application_id": 794563716710957096,
                "version": "v0.0.1-alpha"
            }
        )
        assert config.version=="v0.0.1-alpha"