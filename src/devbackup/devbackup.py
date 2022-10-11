"""
This is the entry point for dbu command.
"""

import argparse
import logging
import shlex
import subprocess as sp
import sys
from pathlib import Path
from shutil import copyfile, copytree, ignore_patterns, rmtree

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
    """Make a directory if it doesn't exist, overwrite if it does

    Args:
      path (str): directory path
    """
    if not path.exists():
        path.mkdir(parents=True)
    else:
        rmtree(path)
        path.mkdir(parents=True)


def copy_file(src: Path, dst: Path, exclude: list = []):
    """Copy a file to destination

    Args:
      src (str): source file path
      dst (str): destination file path
      exclude (list): exclude list
    """
    make_dir(dst.parent)
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
        copytree(src, dst, ignore=ignore_patterns(*exclude))


def backup(path: Path, config: dict):
    """Backup files and directories to a destination"""
    try:
        for item in config["dotfiles"]:
            src = Path.home() / ("." + item)
            dst = path / item
            make_dir(dst.parent)
            copy_file(src, dst, config["exclude"])
        for item in config["dotfolders"]:
            src = Path.home() / ("." + item)
            dst = path / item
            make_dir(dst)
            copy_dir(src, dst, config["exclude"])
    except KeyError:
        pass


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
        "-o", "--output", default="backup", help="output directory"
    )

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
    _logger.debug(f"config: {config}")
    make_dir(Path(args.output))
    _logger.debug(f"output: {args.output}")

    # backup dotfiles here
    for path in config["dotfiles"]:
        print(Path.home() / ("." + path))
        copy_file(
            Path.home() / ("." + path),
            Path(args.output) / path,
            config["exclude"],
        )
        _logger.debug("Copied %s", path)

    # backup dotfolders here
    for path in config["dotfolders"]:
        copy_dir(
            Path.home() / ("." + path),
            Path(args.output) / path,
            config["exclude"],
        )
        _logger.debug("Copied %s", path)

    # backup homebrew list
    output = sp.run(["brew", "list", "--formula"], stdout=sp.PIPE)
    with open(Path(args.output) / "brew.txt", "w") as f:
        f.write(output.stdout.decode("utf-8"))

    # backup cask list
    output = sp.run(["brew", "list", "--cask"], stdout=sp.PIPE)
    with open(Path(args.output) / "cask.txt", "w") as f:
        f.write(output.stdout.decode("utf-8"))

    # backup all conda envs
    output = sp.run(["conda", "env", "list"], stdout=sp.PIPE)
    envs = output.stdout.decode("utf-8").split("\n")[2:-2]
    envs = [e.split("  ")[0] for e in envs]
    make_dir(Path(args.output) / "conda_backups")
    for env in envs:
        output = sp.run(["conda", "env", "export", "-n", env], stdout=sp.PIPE)
        with open(Path(args.output) / f"conda_backups/{env}.yml", "w") as f:
            # Split command will remove prefix from the file
            f.write("\n".join(output.stdout.decode("utf-8").split("\n")[:-2]))


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
