"""A subprocess keeps its interpreter ABI without inheriting ambient credentials."""

import unittest
from unittest.mock import patch

from tests.python_runtime import isolated_python_env


class PythonRuntimeEnvironmentTests(unittest.TestCase):
    def test_loader_path_survives_but_credentials_and_network_config_do_not(self):
        with patch.dict(
            "os.environ",
            {
                "LD_LIBRARY_PATH": "/selected/python/lib",
                "AWS_SECRET_ACCESS_KEY": "fixture-only",
                "HTTPS_PROXY": "http://fixture.invalid",
            },
            clear=True,
        ):
            self.assertEqual(
                isolated_python_env({"PATH": "/offline/fixture", "PYTHONNOUSERSITE": "1"}),
                {"LD_LIBRARY_PATH": "/selected/python/lib", "PATH": "/offline/fixture", "PYTHONNOUSERSITE": "1"},
            )

    def test_no_loader_setting_is_invented_on_other_installations(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(isolated_python_env({"PATH": "/offline/fixture"}), {"PATH": "/offline/fixture"})
