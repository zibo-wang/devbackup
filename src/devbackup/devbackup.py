"""
This is the entry point for dbu command.
"""

import argparse
import logging
import subprocess as sp
import sys
from pathlib import Path
from shutil import copyfile, copytree

import yaml

from devbackup import __version__

__author__ = "Zibo Wang"
__copyright__ = "Zibo Wang"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


# ---- Python API ----
# The functions defined in this section can be imported by users in their
# Python scripts/interactive interpreter, e.g. via
# `from devbackup.devbackup import load_config``,
# when using this Python module as a library.


def load_config(config_path: Path) -> dict:
    """Load config from config file

    Args:
      config_path (str): config file path

    Returns:
      :obj:`dict`: config dict
    """

    with open(config_path, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config


def make_dir(path: Path):
    """Make a directory if it doesn't exist

    Args:
      path (str): directory path
    """
    if not path.exists():
        path.mkdir(parents=True)


def copy_file(src: Path, dst: Path, exclude: list = []):
    """Copy a file to destination

    Args:
      src (str): source file path
      dst (str): destination file path
      exclude (list): exclude list
    """
    if src.name not in exclude:
        copyfile(src, dst)


def copy_dir(src: Path, dst: Path, exclude: list = []):
    """Copy a directory to destination

    Args:
      src (str): source directory path
      dst (str): destination directory path
      exclude (list): exclude list
    """
    if src.name not in exclude:
        copytree(src, dst)


# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.


def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="A backup tool for developers.")
    parser.add_argument(
        "--version",
        action="version",
        version="devbackup {ver}".format(ver=__version__),
    )
    parser.add_argument("-c", "--config", help="config file path")
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel,
        stream=sys.stdout,
        format=logformat,
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main(args):
    """Wrapper allowing :func:`fib` to be called with string arguments in a CLI fashion

    Instead of returning the value from :func:`fib`, it prints the result to the
    ``stdout`` in a nicely formatted message.

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--verbose", "42"]``).
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("Starting Tools")
    config = load_config(Path(args.config))
    print(config)
    _logger.info("Script ends here.")


def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html

    # After installing your project with pip, users can also run your Python
    # modules as scripts via the ``-m`` flag, as defined in PEP 338::
    #
    #     python -m devbackup.skeleton 42
    #
    run()
