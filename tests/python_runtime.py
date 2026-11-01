"""Keep isolated CLI fixtures on the selected Python interpreter's shared library."""

import os


def isolated_python_env(variables):
    # setup-python exports this path for relocatable Linux interpreters. Dropping
    # it can load the host's older libpython even through an absolute executable.
    # No credentials, proxy settings or other ambient configuration are inherited.
    loader = os.environ.get("LD_LIBRARY_PATH")
    environment = {"LD_LIBRARY_PATH": loader} if loader else {}
    return {**environment, **variables}
