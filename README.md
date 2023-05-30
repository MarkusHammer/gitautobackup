# Git Auto Backup Tool

A basic CLI program and python module that allows for quickly making and comming changes to a git repository, along with a few other tools. Use it from the command line or import it as a module, it works both ways!

## Setup

If not installed via pip, than the requirements for this script must be installed in the python environment. This script requires the ``git`` python module be available in you python environment in order to run. This can also use the ``argparse`` module optionally to help greatly increase the usability on the command line (and is highly suggested). These can be installed using:

``pip install git argparse[cli]``

or if you just want the module without the extra cli overhead:

``pip install git argparse``

If you prefer to have this a s a standalone file and are **sure** that you have all dependences satisfied in some way you can also simply clone this repo into your project and import the ``gitautobackup.py`` file locally.

## Command Line Interface

depending on how you set up this file on you system you can run this module using ``python -m gitautobackup`` if you set it up using pip or ``python ./gitautobackup.py`` or ``py ./gitautobackup.py`` if you have the gitautobackup file locally.

While this module does not explicitly require the ``argparse`` module, it is **highly** suggested as it help greatly improve the usability and allows acess to more options.

If in doubt just install ``argparse``.

### With ``argparse``

This module does not have any required arguments, as everything does have a default behaviour. The most importnant thing to note is that when not supplied with the path of the git repository, it attempts to deduce the location of a git repository (by testing if the directory is able to be loaded as a git repository) from (in this specific order):

1. The console's current working direcory
2. The directory given in the 0th arg of the command line (aka ``sys.argv[0]``'s lowest directory)
3. The location of this file itself
   For those wanting to acess this logic when using this a  a module the ``get_default_git_location()`` function will return this value.

- ``-p`` or ``--path`` specifies the repository path
- ``-m`` or ``--message`` (or others) specifies the commit's message.
- ``-f``, ``--force``, or ``--forcecommit`` makes a commit be made even if nothing was changed
- ``--fc``, ``--forcecompress`` forces the repository's database to always be compressed, even if it not really necessary. This cannot be combined with ``--fnc``
- ``--fnc``, ``--forcenocompress`` forces the repository's database to never be compressed, even if it might be beneficial. This cannot be combined with ``--fc``
- ``-v``, ``--verbose`` makes the output of the program more noisy. This cannot be combined with ``-q``
- ``-q``, ``--quiet`` greatly reduces the output of the program. This cannot be combined with ``-v``

There are also the traditional arguments that report various information about this software then exit:

- ``--ver`` or ``--version`` prints the program version and then exits. You don't need a input file if you run this command.
- ``-h`` or ``--help`` prints some details about the programs arguments and then exits. You don't need a input file if you run this command.
- ``--git`` or ``--github`` prints a like to the github repository and then exits. You don't need a input file if you run this command.

### Without ``argparse``

While using this on the command line without argparse is not suggested, you may still access a diminished selection of features:

- The ``-m`` or ``--message`` flag still works
- The path of the git repository does not require a flag and can simply have it path stated. If multiple paths are given, the first one thats a valid repository will be chosen. The program will explicitly fail if none where given.
- The ``--help`` and ``-h`` args also work as expected.

### Command Line Interface Example

If argparse is available:

```cmd:
python -m gitautobackup -p "./repo" -m "automatic backup after big change" -f -fc -v
```

If argparse is not available:

```cmd:
python -m gitautobackup "./repo" -m "automatic backup after big change"
```

## Module Interface

This module can also be interfaced with as a normal module. The points of intreast include the ``main`` function for interfacing with this just like it was the command line (this means **parsing the arguments**, meaning that the features outlined in the Command Line Interface section above), and the ``auto_git_backup`` command for a more direct ussage of the command.
While both can manage to acheave the same result its suggested to use ``auto_git_backup`` unless there is a specific reason to use ``main``.

More information about this module can be found in the main file as all functions have been documented in there.

### Module Example

```python:
from gitautobackup import auto_git_backup

myrepopath = "./project/repo/" #this assumes the folder "./project/repo/" has a already initialised non bare git repository already.

if auto_git_backup(myrepopath, commit_message = "Automatic Backup No. 1", force_commit = True):
  print("Backup successful")
else:
  print("Backup failure")
```

## Licence

This is licenced under the Mozilla Public License 2.0 (MPL 2.0) Licence. See the ``Licence`` file in this repository for more information.

## Credits

This project uses the ``pathlib``, ``git`` and optionally ``argparse`` modules, all very usefull python modules. Check them out if you want to make a simple CLI script like this, or for whatever else you might be up to in python. Also thank you to the developers of these modules for making these as they helped keep my sanity in check.

While not required, feel free to credit "*Markus Hammer*" (or just "*Markus*") if you find this code or script usefull for whatever you may be doing with it.

**Thanks!**
