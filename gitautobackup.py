'''
    autoback: A simple python script and module to make a automatic backup of a git repository.
    Includes both a CLI interface as well as a module interface for individual functions as well as
        a function that accepts arguments like the CLI interface.
    
    By Markus Hammer 2023

    Licenced under the Mozilla Public License 2.0 (MPL 2.0)
    Read the included 'LICENCE' file for more information.

    See the github repo for more info!
    
    This project is on github here:
    https://github.com/MarkusHammer/gitautobackup
'''

# I mean I know its good pratice but I do not care for reformating all
#  my docstrings and making the file less readable just so it fits on smaller screens.
# No its not a run on sentince problem I can stop anytime I want damn it!
# pylint: disable=C0301

#Disable the warnings for importing out of the top level,
# as this is used to import modules only when needed by certian functions
# pylint: disable=C0415



from pathlib import Path
from git import Repo, InvalidGitRepositoryError

try:
    from typing import Union
except ImportError:
    from typing_extensions import Union

__version__ = "1.0.1.3"

def path_hunt_dir(path: Union[Path, str, None]) -> Union['Path', None]:
    """_summary_

    Args:
        path (Union[Path,str,None]): The path to search for the parent directory of. If this is set to None the return value will always also be None

    Returns:
        Union[Path,None]: Returns a Path of the directory if a directory was found, or None if one couldn't be found
    """

    if path is None:
        return None

    if not isinstance(path, Path):
        path = Path(path)

    if not path.exists():
        return None

    path = path.expanduser()

    while (not path.is_dir()) and len(path.parents) > 0:
        path = path.parent

    if not path.is_dir():
        return None
    else:
        return path


def assert_repo(path: Union[Path, str, None], allow_bare: bool = False):
    """Raises various exceptions to test if a path is or is not a git repo. This function does not return a value, use is_repo instead if you want that.

    Args:
        path (Union[Path,str,None]): The path to assert is a repository. Always raises FileNotFoundError when set to None.
        allow_bare (bool, optional): Don't raise InvalidGitRepositoryError if the repository is bare. Defaults to False.

    Raises:
        NOTE: This may not be a comprehensive list of all possible exceptions raised, as pathlib or git may raise various other exceptions as well, however what is stated below is the behaviour explicitly defined in raise statements.
        InvalidGitRepositoryError: Raised when the folder could not be opened as a git repo, if the path couldn't possibly be a git repo (if its not a directory and does not end with ".git"), or if it can be opened but it is a bare repo and allow_bare is False.
        FileNotFoundError: Raised when the path is None or doesn't exist on the system.
    """

    if path is None:
        raise FileNotFoundError()

    if not isinstance(path, Path):
        path = Path(path)

    if not path.exists():
        raise FileNotFoundError()

    if not (path.is_dir() or str(path).endswith(".git")):
        raise InvalidGitRepositoryError()

    with Repo(path) as repo:
        if (not allow_bare) and repo.bare:
            raise InvalidGitRepositoryError()


def is_repo(path: Union[Path, str, None], allow_bare: bool = False) -> bool:
    """Returns bool if a path is a git repo. This returns a value and doesn't raise an exception, use assert_repo instead if you want that.

    Args:
        path (Union[Path,str,None]): The path to assert is a repository. Returns False when set to None.
        allow_bare (bool, optional): Don't raise InvalidGitRepositoryError if the repository is bare. Defaults to False.

    Returns:
        bool: Weather or not the path given is a git repository.
    """

    retval = True
    try:
        assert_repo(path, allow_bare)
    except (InvalidGitRepositoryError, FileNotFoundError, PermissionError):
        retval = False
    return retval


def default_commit_name(nodatetime: bool = False) -> str:
    """Returns the default commit name, generated based on if the system has the datetime module accessable and if its allowed.

    Args:
        nodatetime (bool, optional): Don't allow use fo the datetime module. Defaults to False.

    Returns:
        str: The ideal default commit name.
    """

    if not nodatetime:
        try:
            from datetime import datetime
            return f"Autosave on {datetime.now()}"
        except ImportError:
            pass
    return "Autosave"


def get_default_file_location() -> Union[Path, None]:
    """Returns the most relevant default file location based on how this script/module is run and what is accessable. Returns None if nothing could be determined.

    Returns:
        Union[Path,None]: The path that was found, it one was found. If not this will be None.
    """

    possiblepath = path_hunt_dir(Path.cwd())
    if possiblepath is not None and possiblepath.exists():
        return possiblepath

    try:
        from sys import (argv as cliargv)
    except ImportError:
        pass
    else:
        if len(cliargv) > 0 and isinstance(cliargv[0], str):
            possiblepath = path_hunt_dir(cliargv[0])
            if possiblepath is not None and possiblepath.exists():
                return possiblepath

    # this only really helps if this file is run as the main script.
    # Unlikely that it will be needed however because argv is almost always guaranteed
    #   to work on any system that is able to suport the mandatory requirements of this script anyway.
    # Still good for a plan c however ...
    if __name__ == "__main__":
        try:
            _ = __file__
        except NameError:
            pass
        else:
            possiblepath = path_hunt_dir(__file__)
            if possiblepath is not None and possiblepath.exists():
                return possiblepath

    return None


def auto_git_backup(repo_path: Union[Path, None] = None, commit_message: Union[str, None] = None, further_guess_paths: bool = False, verbose: bool = True, force_commit: bool = False, force_compress: Union[bool, None] = None) -> bool:
    """_summary_

    Args:
        repo_path (Union[Path,None], optional): The path of the target git repository. If set to None and further_guess_paths is set there will be an attempts to determine this using ```get_default_file_location()```. Defaults to None.
        commit_message (Union[str,None], optional): The message of the commit being made. If None this will be automatically generated using ```default_commit_name()```. Defaults to None.
        further_guess_paths (bool, optional): If the path is set to none, should there be attempt to automatically guess the relevant path using ```get_default_file_location()```. Defaults to False.
        verbose (bool, optional): SHould this function print out non error related messages? Defaults to True.
        force_commit (bool, optional): Should a commit be made even if there is nothing to be committed? Defaults to False.
        force_compress (Union[bool, None], optional): Should (or shouldn't) the database be compressed despite it possibly being beneficial. True forces the database to be compressed, False forces the databest to not be compressed, and None allows for this to be automatically determined by git instead. Defaults to None.

    Raises:
        NOTE: This may not be a comprehensive list of all possible exceptions raised, as pathlib or git may raise various other exceptions as well, however what is stated below is the behaviour explicitly defined in raise statements.
        InvalidGitRepositoryError: Raised when the folder could not be opened as a git repo, if the path couldn't possibly be a git repo (if its not a directory and does not end with ".git"), or if it can be opened but it is a bare repo and allow_bare is False.
        FileNotFoundError: Raised when the path doesn't exist on the system.

    Returns:
        bool: Weather or not a commit was made.
    """

    made_a_backup: bool = False

    if commit_message is None or commit_message.strip() == "":
        commit_message = default_commit_name()

    if verbose:
        try:
            from pprint import pprint
        except ImportError:
            pprint = print

    if further_guess_paths and repo_path is None:
        repo_path = get_default_file_location()

    if repo_path is None:
        raise InvalidGitRepositoryError()

    repo_path = Path(repo_path)
    if not repo_path.exists():
        raise FileNotFoundError()
    while not is_repo(repo_path) and len(repo_path.parents) > 0:
        repo_path = repo_path.parent
    assert_repo(repo_path)

    if verbose:
        print(f"Opening path as repo: {repo_path} {'and forcing a commit' if force_commit else ''}...")
    with Repo(repo_path) as repo:

        if force_commit or repo.is_dirty(untracked_files=True):
            made_a_backup = True

            msg = repo.git.add("--all", "--ignore-errors")
            if verbose and msg != "":
                pprint(msg)

            if verbose:
                pprint(repo.git.status("-s"))

            cmd_args = []
            if force_commit:
                cmd_args.append("--allow-empty")
            msg = repo.git.commit(cmd_args, m=commit_message)
            if verbose and msg != "":
                pprint(msg)

        if force_compress is None or force_compress is True:
            cmd_args = []
            if force_compress is None:
                cmd_args.append("--auto")
            msg = repo.git.gc(cmd_args)
            if verbose and msg != "":
                pprint(msg)

    # TODO LONGTERM git reflog expire can it also be a feature?

    return made_a_backup


def main(*args, prog_arg: Union[str, None] = None) -> bool:
    """A function that run the main entry point for the cli interface of the program. This allows for you to use this as you would normally via the cli but still import this as a module. Please not however that argv is only intended for the cli arguments and not for the name of the script running this, thats what the optional prog_arg argument is intended for.

    Args:
        *args (Tuple[None]): The arguments form the command line, sans the one with the name of this program (what the sys module's argv puts in the [0]th spot), thats what prog_arg is for.
        prog_arg (Union[str, None], optional): This is used for what is traditionally used as the [0]th member if argv, the name of this program as it was called in the command line. THis is however, completely optional. Defaults to None.

    Returns:
        bool: weather or not a backup was made by ```auto_git_backup```
    """

    path = None
    force_commit = False
    force_compress = None
    message = None
    verbose = True
    further_guess_paths = True

    # parse the cli args
    try:
        from argparse import ArgumentParser
        parser = ArgumentParser(
            prog=prog_arg, description='A basic CLI program that allows for quick formatting of a .gitignore file')

        parser.add_argument('-p', '--path', '-d', '--dest', '-r', '--repo',
                            dest='repo_path', action='store', default=None, type=str,
                            help='The location of the git repo')
        parser.add_argument('-m', '--message', '-b', '--body', '-c', '--cm', '--commit_message', '-n', '--name', '--cn', '--commit_name',
                            dest='message', action='store', default=message, type=str,
                            help="The message of the commit. Note that this defaults to the message of the form 'Autosave at DATE TIME HERE' not to None as it might say")

        parser.add_argument('-f', '--force', '--forcecommit', dest='force_commit', action='store_true', default=force_commit,
                            help='Push a commit to the repo even if there are no changes')
        force_compress_group = parser.add_mutually_exclusive_group()
        force_compress_group.add_argument('--fc', '--forcecompress', dest='force_compress', action='store_true',
                                          help='Compress the database even if its not quite necessary')
        force_compress_group.add_argument('--fnc', '--forcenocompress', dest='force_no_compress', action='store_true',
                                          help='Skip compressing the database even if it might be usefull')

        loudness_group = parser.add_mutually_exclusive_group()
        loudness_group.add_argument("-v", "--verbose", dest="verbose",
                                    action="store_true", help="Print a verbose output of the process")
        loudness_group.add_argument("-q", "--quiet", dest="quiet", action="store_true",
                                    help="Avoid printing anything to the terminal if possible")

        # don't forget to update it in the pyproject.toml to!
        parser.add_argument("--ver", "--version",
                            action='version', version=__version__)
        parser.add_argument("--git", "--github", action='version',
                            help="Give a link to the github repo page", version="https://github.com/MarkusHammer/gitautobackup")

        args = parser.parse_args(*args)
        path = args.repo_path
        if path is not None:
            path = path.strip("'").strip('"')
        force_commit = args.force_commit
        if args.force_compress:
            force_compress = True
        elif args.force_no_compress:
            force_compress = False
        else:
            force_compress = None
        message = args.message
        if message is not None:
            message = message.strip("'").strip('"')

        if args.verbose:
            verbose = True
        elif args.quiet:
            verbose = False
    except ImportError:
        print("Argparse could not be loaded/found, please note that this will mean that explicitly specifying the path form the cli is required and all other cli arguments are not available")
        further_guess_paths = False

        next_is_message = False
        for arglet in args:
            arglet = arglet.strip().strip('"')

            if next_is_message:
                message = arglet

            if arglet.lower() == "-p" or arglet.lower() == "--path":
                continue

            if arglet.lower() == "-h" or arglet.lower() == "--help":
                print(f"You are running {prog_arg[0]}")
                print(
                    """
                    -h or --help shows this
                    -m or --message specifies a message for the commit
                    All other arguments given will be tested for being a valid repository. The first one found will be the one selected.
                    To receve a better command line experience please install 'argparse' to your python environment!""")
                return 0

            if arglet.lower() == "-m" or arglet.lower() == "--message":
                next_is_message = True

            if path is not None and is_repo(arglet):
                path = arglet.strip("'").strip('"')

        if path is None:
            print("No valid repository path was found")
            return False
        verbose = True

    if args.verbose:
        print("Making auto backup")

    return auto_git_backup(path, commit_message=message, further_guess_paths=further_guess_paths, verbose=verbose, force_commit=force_commit, force_compress=force_compress)


def __main__():
    from sys import (exit as end, argv)
    end(main(argv[1:], prog_arg=argv[0]))

if __name__ == "__main__":
    __main__()
