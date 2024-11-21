# Git Auto Backup

A basic CLI program and python module that allows for quickly making and committing changes to a git repository, along with a few other tools. Use it from the command line or import it as a module, it works both ways!

[![CodeQL](https://github.com/MarkusHammer/gitautobackup/actions/workflows/codeql.yml/badge.svg)](https://github.com/MarkusHammer/gitautobackup/actions/workflows/codeql.yml) [![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/markushammer)

## Setup

First off, this script uses the ``GitPython`` module, so ensure that you have a compatible version of git installed on your system so that ``GitPython`` can interface with it properly. For more info look [here](https://github.com/gitpython-developers/GitPython).

If not installed via pip, then the requirements for this script must be installed in the python environment. This script requires the ``git`` python module to be available in your python environment in order to run. This can also use the ``argparse`` module optionally to help greatly increase the usability on the command line (and is highly suggested). These can be installed using:

``pip install gitautobackup[cli]``

or if you just want the module without the extra cli overhead (not suggested):

``pip install gitautobackup``

If you prefer to have this as a standalone file and are **sure** that you have all dependences satisfied in some way you can also simply clone this repo into your project and import the ``gitautobackup.py`` file locally.

> Please note that if this is the method you use, please ensure that the path is always specified, as if not it will default to the current terminal working directory, which if set to the location of your clone of this repository will result in making a commit to this project's clone. I only mention this as this is a mistake I have made myself quite a few times.

## Command Line Interface

Depending on how you set up this file on your system, you can run this module using ``python -m gitautobackup`` if you set it up using pip, or ``python ./gitautobackup.py`` or ``py ./gitautobackup.py`` if you have the gitautobackup file locally.

While this module does not explicitly require the ``argparse`` module, it is **highly** suggested as it help greatly improve the usability and allows access to more options. If in doubt just install ``argparse`` if you can.

### With ``argparse``

This module does not have any required arguments, as everything does have a default behavior. The most important thing to note is that when not supplied with the path of the git repository, it attempts to deduce the location of a git repository (by testing if the directory is able to be loaded as a git repository) from (in this specific order):

1. The console's current working directory
2. The directory given in the 0th arg of the command line (aka ``sys.argv[0]``'s lowest directory)
3. The location of this file itself
   For those wanting to access this logic when using this as a module the ``get_default_git_location()`` function will return this value.

Here are a few of the possible arguments to use:

- ``-p`` / ``--path`` specifies the repository path
- ``-m`` / ``--message`` specifies the commit's message.
- ``-t`` / ``--tag`` sets a tag for the commit
- ``-a`` / ``--archive`` / ``--archive_path`` sets a path for an archive file to be made. If this isn't used an archive file will not be made.
- ``-f`` / ``--force`` / ``--force_commit`` makes a commit be made even if nothing was changed
- ``--fc`` / ``--force_cleanup`` forces the repository's database to always be cleaned, even if it's not really necessary. This cannot be combined with ``--fnc`` or ``--fca``
- ``--fnc`` / ``--force_no_cleanup`` forces the repository's database to never be cleaned, even if it might be beneficial. This cannot be combined with ``--fc`` or ``--fca``
- ``--fca`` / ``--force_cleanup_aggressive`` forces the repository's database cleaned aggressively (taking a much longer time), even if it's not necessary. This cannot be combined with ``--fc`` or ``--fnc``
- ``-v`` / ``--verbose`` makes the output of the program more noisy. This cannot be combined with ``-q``
- ``-q`` / ``--quiet`` greatly reduces the output of the program. This cannot be combined with ``-v``

There are also the traditional arguments that report various information about this software and then exit:

- ``--ver`` / ``--version`` prints the program version and then exits. You don't need an input file if you run this command.
- ``-h`` / ``--help`` prints some details about the programs arguments and then exits. You don't need a input file if you run this command.
- ``--git`` / ``--github`` prints a link to the github repository and then exits. You don't need an input file if you run this command.

### Without ``argparse``

While using this on the command line without ``argparse`` is not suggested, you may still access a diminished selection of features: only the ``-m``, ``--message``, ``-p``, ``--path``, ``--help`` and ``-h`` flags work.

### Command Line Interface Example

If ``argparse`` is available:

```bash:
python -m gitautobackup -p "./repo" -m "automatic backup after big change" -f -fc -v
```

If ``argparse`` is not available:

```bash:
python -m gitautobackup -p "./repo" -m "automatic backup after big change"
```

## Module Interface

This module can also be interfaced with as a normal module. The points of interest include the ``main`` function for interfacing with this just like it was the command line (this means **parsing the arguments**, meaning that the features outlined in the Command Line Interface section above), and the ``main_cli`` command for a more direct usage of the command.
While both can manage to achieve the same result it's suggested to use ``main_cli`` unless there is a specific reason to use ``main``.

More information about this module can be found in the main file as all functions have been documented within.

### Module Example

```python:
from gitautobackup import main_cli

myrepopath = "./project/repo/" #this assumes the folder "./project/repo/" has a already initialised non bare git repository already.

if main_cli(myrepopath, commit_message = "Automatic Backup No. 1", force_commit = True):
  print("Backup successful")
else:
  print("Backup failure")
```

## Licence

This is licensed under the Mozilla Public License 2.0 (MPL 2.0) Licence. See the ``Licence`` file in this repository for more information.

## Credits

This project uses the ``pathlib`` (or alternatively ``pathlib2`` if ``pathlib2`` is available to import and ``pathlib`` is not), ``GitPython`` and optionally ``argparse`` modules, all very useful python modules. Check them out if you want to make a simple CLI script like this, or for whatever else you might be up to in python. Also thank you to the developers of these modules for making these as they helped keep my sanity in check.

While not required, feel free to credit "*Markus Hammer*" (or just "*Markus*") if you find this code or script useful for whatever you may be doing with it.

**Thanks!**
