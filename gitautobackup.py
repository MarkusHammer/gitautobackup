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

__version__ = "2.0.1.0"

from git import Repo, InvalidGitRepositoryError, GitCommandNotFound, NoSuchPathError, RepositoryDirtyError, GitError

try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path

try:
    from datetime import datetime
    DATETIME_IMPORTED = True
except ImportError:
    DATETIME_IMPORTED = False

try:
    from argparse import ArgumentParser
    ARGPARSE_IMPORTED = True
except ImportError:
    ARGPARSE_IMPORTED = False

try:
    from sys import argv as cliargv
    CLIARGV_IMPORTED = True
except ImportError:
    CLIARGV_IMPORTED = False

try:
    from sys import exit as end
    END_IMPORTED = True
except ImportError:
    END_IMPORTED = False

try:
    from os import name as os_type
    OS_TYPE_IMPORTED = True
except ImportError:
    OS_TYPE_IMPORTED = False

try:
    from typing import Union
except ImportError:
    from typing_extensions import Union

try:
    from typing import List
except ImportError:
    from typing_extensions import List

try:
    from typing import Tuple
except ImportError:
    from typing_extensions import Tuple

try:
    from typing import Callable
except ImportError:
    from typing_extensions import Callable


class InvalidArchiveFormatError(GitError, Exception):
    """Raised when a format for git archive when that format is not a valid format for git archive"""    

    def __init__(self, given_format:str, possible_formats:Union[List[str], None] = None):
        """
        Args:
            format (str): The issue causing format.
            repo_reference (Union[Repo, None], optional): A optional list of possible valid formats, or None if this cant be given.
        """

        self.given_format:str = given_format
        self.possible_formats:List[str] = []

        if possible_formats is not None:
            self.possible_formats = possible_formats

    def __str__(self) -> str:
        return f"The format {self.given_format} is not a valid format for a archive in git. {('Valid formats are ' + ' '.join(self.possible_formats)) if len(self.possible_formats) > 0 else ''}"


class InsecureRepositoryError(GitError, Exception):
    """Raised when a repository may be consitered insecure due to relevant GitPython security issues"""    

    def __init__(self, reasoning:str = ""):
        """
        Args:
            reasoning (str): The reason why this repo is consitered insecure, worded like "This repository is conidered insecure because {INSERT REASON HERE}."
        """

        self.reasoning:str = reasoning.strip()

    def __str__(self) -> str:
        return f"This path to a repository cannot be used and is considered insecure because {self.reasoning}."


def path_hunt_dir(path: Union[Path, str, None]) -> Union['Path', None]:
    """Gets the parrent directory of a file if possible.
    
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


def assert_file(path: Union[Path, str, None]):
    """Asserts that a file exists and is a file

    Args:
        path (Union[Path, str, None]): The path to assert exists and is a file

    Raises:
        NoSuchPathError: The path does not exist on the system
        FileNotFoundError: The path is not a file
    """
    if path is None:
        raise NoSuchPathError()

    if not isinstance(path, Path):
        path = Path(path)
    path = path.expanduser()

    if not path.exists():
        raise NoSuchPathError()

    if not path.is_file():
        raise FileNotFoundError


def assert_repo(path: Union[Path, str, None], allow_bare: bool = False):
    """Raises various exceptions to test if a path is or is not a git repo. This function does not return a value, use is_repo instead if you want that.

    Args:
        path (Union[Path,str,None]): The path to assert is a repository. Always raises NoSuchPathError when set to None.
        allow_bare (bool, optional): Don't raise InvalidGitRepositoryError if the repository is bare. Defaults to False.

    Raises:
        NOTE: This may not be a comprehensive list of all possible exceptions raised, as pathlib or git may raise various other exceptions as well, however what is stated below is the behaviour explicitly defined in raise statements.
        InvalidGitRepositoryError: Raised when the folder could not be opened as a git repo, if the path couldn't possibly be a git repo (if its not a directory and does not end with ".git"), or if it can be opened but it is a bare repo and allow_bare is False.
        NoSuchPathError: Raised when the path is None or doesn't exist on the system.
    """

    if path is None:
        raise NoSuchPathError()

    if not isinstance(path, Path):
        path = Path(path)
    path = path.expanduser()

    if not path.exists():
        raise NoSuchPathError()

    if not path.is_dir():
        raise InvalidGitRepositoryError()

    if not OS_TYPE_IMPORTED or os_type == "nt": #protects against https://github.com/MarkusHammer/gitautobackup/security/dependabot/1
        dangerous_files = list(path.glob('git.exe')) + list(path.glob('git'))
        dangerous_files = [file for file in dangerous_files if not file.is_dir()]
        if len(dangerous_files) > 0:
            dangerous_files = [f"'{file.name}'" for file in dangerous_files]
            raise InsecureRepositoryError(f"it contains {'files' if len(dangerous_files) > 1 else 'a file'} named {' and '.join(dangerous_files)} which may allow for this file to be called instead of the git command on your system")

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
    except (InvalidGitRepositoryError, NoSuchPathError, PermissionError): #DO NOT CATCH ANY InsecureRepositoryErrors these errors must be passed on!
        retval = False
    return retval


def default_commit_name(nodatetime: bool = False) -> str:
    """Returns the default commit name, generated based on if the system has the datetime module accessable and if its allowed.

    Args:
        nodatetime (bool, optional): Don't allow use fo the datetime module. Defaults to False.

    Returns:
        str: The ideal default commit name.
    """

    if DATETIME_IMPORTED and not nodatetime:
        return f"Autosave on {datetime.now()}"
    return "Autosave"


def get_default_file_location() -> Union[Path, None]:
    """Returns the most relevant default file location based on how this script/module is run and what is accessable. Returns None if nothing could be determined.

    Returns:
        Union[Path,None]: The path that was found, it one was found. If not this will be None.
    """

    possiblepath = path_hunt_dir(Path.cwd())
    if possiblepath is not None and possiblepath.exists():
        return possiblepath

    if CLIARGV_IMPORTED:
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
        except (NameError, TypeError):
            pass
        else:
            possiblepath = path_hunt_dir(__file__)
            if possiblepath is not None and possiblepath.exists():
                return possiblepath

    return None


def resolve_repo(repo_path: Union[Path, str, None] = None,
                 further_guess_paths: bool = False
                 ) -> Repo:
    """Attempts to smartley resolve a path to find a gitrepo withing it and possibly the default path location (as given by ```get_default_file_location```) if enabled.

    Args:
        repo_path (Union[Path, str, None], optional): The path to look for a git repo in. Defaults to None.
        further_guess_paths (bool, optional): If the path is not defined, should the default path (as given by ```get_default_file_location```) be used instead. Defaults to False.

    Raises:
        InvalidGitRepositoryError: The path exists, but is not a git repo.
        NoSuchPathError: The path is not something that exists.

    Returns:
        Repo: The resolved git repo object.
    """
    
    if further_guess_paths and repo_path is None:
        repo_path = get_default_file_location()

    if repo_path is None:
        raise InvalidGitRepositoryError()

    repo_path = Path(repo_path)
    if not repo_path.exists():
        raise NoSuchPathError()
    while not is_repo(repo_path) and len(repo_path.parents) > 0:
        repo_path = repo_path.parent
    assert_repo(repo_path)

    return Repo(repo_path)


def print_output(msg:Union[str,None] = None, *, print_func:Callable = print):
    """Print out and lightly format a message, only if it would not appear empty.

    Args:
        msg (Union[str,None], optional): The message to print. Defaults to None.
        print_func (Callable, optional): Overide the print function possibly called. Defaults to the callable of ```print()```.
    """
    
    if msg is None:
        return

    msg = msg.strip()

    if msg != "":
        return

    print_func(msg)


def repo_get_archive_formats(repo:Repo) -> Tuple[str]:
    """Retrieves the possible archive formats (as git archive would accept) available to this specific repo on this specific system.

    Args:
        repo (Repo): A repository to use to query what archive formats are available.

    Returns:
        Tuple[str]: A tuple of all formats
    """
    return tuple(x.strip() for x in repo.git.archive("--list").split())


def archive_repo(repo:Repo,
                 archive_paths:Union[Path, str, List[Union[Path, str]], Tuple[Union[Path, str]]],
                 archive_format:Union[str, None] = None,
                 *,
                 verbose:bool = False
                ):
    """Archives a repository object to the given path (or paths), with the specified format, or the default format if not provided.
    
    Args:
        repo(Repo): The Repo object in question, the one to create an archive from.
        archive_paths(Union[Path, str, List[Union[Path, str]]): The (or a list or tuple of multiple) path (as a path object or string) to save the archive to.
        archive_format(Union[str, None], optional): The string of the archive format to use, as is returned by ```repo_get_archive_formats()```, not case sensitive. Defaults to None.
        verbose (bool, optional): Should the outputs of the functions be passed into the terminal. Defaults to False.
    """

    if archive_format is not None:
        archive_format = archive_format.strip()
        valid_archive_formats = repo_get_archive_formats(repo)

        if archive_format not in valid_archive_formats:
            if archive_format.lower() in valid_archive_formats:
                archive_format = archive_format.lower()
            elif archive_format.upper() in valid_archive_formats:
                archive_format = archive_format.upper()
            else:
                raise InvalidArchiveFormatError(archive_format, valid_archive_formats)

    if not isinstance(archive_paths, (list, tuple)):
        archive_paths = (archive_paths, )

    for archive_path in archive_paths:
        archive_path = path_hunt_dir(Path(archive_path))

        cmd_args = []
        cmd_kwargs = {"o": archive_path}
        if verbose:
            cmd_args.append("-v")
        if archive_format is not None:
            cmd_kwargs["format"] = archive_format
        cmd_args.append("HEAD")

        msg = repo.git.archive(cmd_args, **cmd_kwargs)
        if verbose:
            print_output(msg)


def cleanup_repo(repo:Repo,
                 force_cleanup: Union[bool, None] = None,
                 cleanup_aggressive:bool = False,
                 *,
                 verbose:bool = False
                ):
    """Attempts to garbage collect the given Repo if needed or forced. Can be done aggressively if specified.

    Args:
        repo (Repo):  The Repo object in question, the one to garbage collect.
        force_cleanup (Union[bool, None], optional): Weather or not to cleanup even if not really needed. Defaults to None.
        cleanup_aggressive (bool, optional): If cleaning up, should it be done aggressively? Defaults to False.
        verbose (bool, optional): Should the outputs of the functions be passed into the terminal. Defaults to False.
    """
    cmd_args = []
    if cleanup_aggressive:
        cmd_args.append("--aggressive")
    if force_cleanup is None:
        cmd_args.append("--auto")

    msg = repo.git.gc(cmd_args)
    if verbose:
        print_output(msg)


def commit_repo(repo:Repo,
                commit_message: Union[str, None] = None,
                force_commit: bool = False,
                tag:Union[str,None] = None,
                force_tag:bool = False,
                tag_message:Union[str, None] = None,
                *,
                verbose:bool = False
                ):
    """Makes a commit of all changes to the repository, with any specified message, tag, and tag message.

    Args:
        repo (Repo): The Repo object in question, the one to commit all changes to.
        commit_message (Union[str, None], optional): The message to add to a commit. If None or not printable (whitespace) this will be automatically generated using ```default_commit_name()``` Defaults to None.
        force_commit (bool, optional): Make a commit even if it would not contain any changes. Defaults to False.
        tag (Union[str,None], optional): The tag to add to the repository. No tag is added if set to None. Defaults to None.
        force_tag (bool, optional): Overwrite a tag if it already exists. Defaults to False.
        tag_message (Union[str, None], optional): A message to add to the tag. No message is added if set to None. Defaults to None.
        verbose (bool, optional): Should the outputs of the functions be passed into the terminal. Defaults to False.
    """

    msg = repo.git.add("--all", "--ignore-errors")
    if verbose:
        print_output(msg)

    if verbose:
        print_output(repo.git.status("-s"))

    cmd_args = []
    if force_commit:
        cmd_args.append("--allow-empty")
    if verbose:
        cmd_args.append("-v")
    if commit_message is None or commit_message.strip() == "":
        commit_message = default_commit_name()

    msg = repo.git.commit(cmd_args, m=commit_message)
    if verbose:
        print_output(msg)

    print("commit done")

    if tag is not None:
        cmd_args = []
        cmd_kwargs = {}
        if force_tag:
            cmd_args.append("-f")
        if tag_message is not None:
            cmd_args.append("-a")
            cmd_kwargs["m"] = tag_message
        cmd_args.append(tag)
        cmd_args.append('HEAD')

        msg = repo.git.tag(cmd_args, **cmd_kwargs)
        if verbose:
            print_output(msg)

    print("tag done")


def main_cli(repo_path: Union[Path, str, None] = None,
             further_guess_paths: bool = False,

             commit_message: Union[str, None] = None,
             force_commit: bool = False,
             tag:Union[str,None] = None,
             force_tag:bool = False,
             tag_message:Union[str, None] = None,

             force_cleanup: Union[bool, None] = None,
             cleanup_aggressive:bool = False,

             archive_paths:Union[Path, str, None, List[Union[Path, str]], Tuple[Union[Path, str]]] = None,
             archive_format:Union[str, None] = None,

             *,

             verbose: bool = True,
            ) -> bool:
    """Run the main command line interface's actions. The main CLI calls this, but this may also be called as a function if using this as a module. While not suggested, if you wish to pass cli arguments instead, please use the ```main()```function instead if possible.

    Args:
        repo_path (Union[Path,None], optional): The path of the target git repository. If set to None and further_guess_paths is set there will be an attempts to determine this using ```get_default_file_location()```. Defaults to None.
        further_guess_paths (bool, optional): If the path is set to none, should there be attempt to automatically guess the relevant path using ```get_default_file_location()```. Defaults to False.

        commit_message (Union[str,None], optional): The message of the commit being made. If None this will be automatically generated using ```default_commit_name()```. Defaults to None.
        force_commit (bool, optional): Should a commit be made even if there is nothing to be committed? Defaults to False.
        tag (Union[str,None], optional): If a tag should be created, this should be the name of that tag. If no tag is to be made, this should be None, even if tag_force is True
        force_tag (bool, optional): Create the new tag even if an old one already exists. No effect if tag is None.
        tag_message (Union[str,None], optional): Add a message to the tag, or None if the tag should have no message. No effect if tag is None.

        force_cleanup (Union[bool, None], optional): Should (or shouldn't) the database be cleaned despite it possibly being beneficial. True forces the database to be cleaned, False forces the databest to not be cleaned, and None allows for this to be automatically determined by git instead. Defaults to None.
        cleanup_aggressive (bool, optional): If the repo is cleaned, should it be done aggressively?

        archive_path (Union[Path,None], optional): If set to None no archive will be made, otherwide a archive will be output to the given location.
        archive_format (Union[str, None], optional): If set this will override the format of the archive being outputted, if set to None it will be inferred form the path.

        verbose (bool, optional): Should this function print out non error related messages? Defaults to True.

    Raises:
        NOTE: This may not be a comprehensive list of all possible exceptions raised, as pathlib or git may raise various other exceptions as well, however what is stated below is the behaviour explicitly defined in raise statements.
        InvalidGitRepositoryError: Raised when the folder could not be opened as a git repo, if the path couldn't possibly be a git repo (if its not a directory and does not end with ".git"), or if it can be opened but it is a bare repo and allow_bare is False.
        InvalidArchiveFormatError: Raised when the given archive format is not a valid format for git archive.
        NoSuchPathError: Raised when the path doesn't exist on the system.

    Returns:
        bool: If commit was made to the repository.
    """

    made_a_backup: bool = False

    repo = resolve_repo(repo_path, further_guess_paths=further_guess_paths)

    if verbose:
        print(f"Opening path as repo: {Path(repo.common_dir).parent} {'and forcing a commit' if force_commit else ''}...")

    with repo:

        if force_commit or repo.is_dirty(untracked_files=True):
            print("Commit...")
            made_a_backup = True
            commit_repo(repo, commit_message, force_commit, tag, force_tag, tag_message, verbose=verbose)

        if force_cleanup is None or force_cleanup is True:
            print("Cleanup...")
            cleanup_repo(repo, force_cleanup, cleanup_aggressive, verbose=verbose)

        if archive_paths is not None:
            print("Archive...")
            archive_repo(repo, archive_paths, archive_format, verbose=verbose)

    return made_a_backup


def main(*args, prog_arg: Union[str, None] = None) -> bool:
    """A function that when used as a module acts as the main entry point of the program. This allows for you to use this as you would normally via the cli but still import this as a module.
    Please note however that argv is only intended for the cli arguments and not for the name of the script running this, thats what the optional prog_arg argument is intended for.
    Also note that this function does not handle exceptions unlike how the cli turns these into user friendly messages. This is intended as the user of a module will most likely find these exceptions usefull.

    Args:
        *args (Tuple[str]): The arguments form the command line, sans the one with the name of this program (what the sys module's argv puts in the [0]th spot), thats what prog_arg is for.
        prog_arg (Union[str, None], optional): This is used for what is traditionally used as the [0]th member if argv, the name of this program as it was called in the command line. THis is however, completely optional. Defaults to None.

    Returns:
        bool: weather or not a backup was made
    """

    path = None
    force_commit = False
    force_tag = False
    force_cleanup = None
    cleanup_aggressive = False
    commit_message = None
    tag = None
    tag_message = None
    verbose = True
    further_guess_paths = True
    archive_path = None
    archive_format = None

    # parse the cli args
    if ARGPARSE_IMPORTED:
        parser = ArgumentParser(prog=prog_arg,
                                description="""
                                A basic CLI program that allows for quick formatting of a .gitignore file
                                """)

        parser.add_argument('-p', '--path', '-d', '--dest', '-r', '--repo',
                            dest='repo_path', action='store', default=path, type=str,
                            help='The location of the git repo')
        parser.add_argument('-m', '--message', '-b', '--body', '-c', '--cm', '--commit_message', '-n', '--name', '--cn', '--commit_name',
                            dest='commit_message', action='store', default=commit_message, type=str,
                            help="The message of the commit. Note that this defaults to the message of the form 'Autosave at DATE TIME HERE' not to None as it might say")
        parser.add_argument('-t', '--tag', '--commit_tag', '--tn', '--tag_name',
                            dest='tag', action='store', default=tag, type=str,
                            help="Assign a tag of the specified name to the commit. If this flag is not used no tag will be made.")
        parser.add_argument('--tm', '--tag_message', '--tm', '--tag_message',
                            dest='tag_message', action='store', default=tag_message, type=str,
                            help="Set a message for the tag of this commit. Only effective if the tag flag is also used, otherwise there is no effect.")

        parser.add_argument('-a', '--archive', '--ap', '--archive_path',
                            dest='archive_path', action='store', default=archive_path, type=str,
                            help="A path to the location of the desired archive to be made. If not defined no archive will be made.")
        parser.add_argument('--af', '--archive_format',
                            dest='archive_format', action='store', default=archive_format, type=str,
                            help="Force the given type of format to be used for the file. If not defined it will be taken from the given path.")

        parser.add_argument('-f', '--force', '--force_commit',
                            dest='force_commit', action='store_true', default=force_commit,
                            help='Push a commit to the repo even if there are no changes')
        parser.add_argument('--ft', '--force_tag',
                            dest='force_tag', action='store_true', default=force_tag,
                            help='If a tag is to be made, force it to overwrite any existing tags that may be in it`s way')

        force_cleanup_group = parser.add_mutually_exclusive_group()
        force_cleanup_group.add_argument('--fnc', '--force_no_cleanup',
                                         dest='force_no_cleanup', action='store_true',
                                         help='Skip cleaning the database even if it might be usefull')
        force_cleanup_group.add_argument('--fc', '--force_cleanup',
                                         dest='force_cleanup', action='store_true',
                                         help='cleanup the database even if its not quite necessary')
        force_cleanup_group.add_argument('--fca', '--force_cleanup_aggressive',
                                         dest='force_cleanup_aggressive', action='store_true',
                                         help='cleanup the database aggressively, even if its not quite necessary')

        loudness_group = parser.add_mutually_exclusive_group()
        loudness_group.add_argument("-v", "--verbose",
                                    dest="verbose", action="store_true",
                                    help="Print a verbose output of the process")
        loudness_group.add_argument("-q", "--quiet",
                                    dest="quiet", action="store_true",
                                    help="Avoid printing anything to the terminal if possible")

        # don't forget to update it in the pyproject.toml to!
        parser.add_argument("--ver", "--version",
                            action='version', version=__version__)
        parser.add_argument("--git", "--github",
                            action='version', version="https://github.com/MarkusHammer/gitautobackup",
                            help="Give a link to the github repo page")

        args = parser.parse_args(*args)
        path = args.repo_path
        if path is not None:
            path = path.strip("'").strip('"')
        force_commit = args.force_commit
        force_tag = args.force_tag
        if args.force_cleanup:
            force_cleanup = True
        elif args.force_no_cleanup:
            force_cleanup = False
        elif args.force_cleanup_aggressive:
            force_cleanup = True
            cleanup_aggressive = True
        else:
            force_cleanup = None
        commit_message = args.commit_message
        if commit_message is not None:
            commit_message = commit_message.strip("'").strip('"')
        tag = args.tag
        if tag is not None:
            tag = tag.strip("'").strip('"')
        tag_message = args.tag_message
        if tag_message is not None:
            tag_message = tag_message.strip("'").strip('"')
        archive_path = args.archive_path
        if archive_path is not None:
            archive_path = archive_path.strip("'").strip('"')
        archive_format = args.archive_format
        if archive_format is not None:
            archive_format = archive_format.strip("'").strip('"')

        if args.verbose:
            verbose = True
        elif args.quiet:
            verbose = False
    else:
        print("Argparse could not be loaded/found, please note that this will mean that explicitly specifying the path form the cli is required and all other cli arguments are not available")
        further_guess_paths = False

        next_is_message = False
        next_is_path = False
        for arglet in args:
            arglet = arglet.strip().strip('"')

            if next_is_path:
                path = arglet.strip("'").strip('"')
                next_is_path = False

            elif next_is_message:
                commit_message = arglet
                next_is_message = False

            elif arglet.lower() == "-h" or arglet.lower() == "--help":
                print(f"You are running {prog_arg[0]}")
                print(
                    """
                    -h or --help shows this
                    -m or --message specifies a message for the commit
                    All other arguments given will be tested for being a valid repository. The first one found will be the one selected.
                    To receve a better command line experience please install 'argparse' to your python environment!""")
                return 0

            elif arglet.lower() == "-p" or arglet.lower() == "--path":
                next_is_path = True

            elif arglet.lower() == "-m" or arglet.lower() == "--message":
                next_is_message = True

        if path is None:
            print("No valid repository path was found")
            return False
        verbose = True

    if args.verbose:
        print("Making auto backup")

    return main_cli(path, commit_message=commit_message, further_guess_paths=further_guess_paths, force_commit=force_commit, tag = tag, tag_message = tag_message, force_tag = force_tag, force_cleanup=force_cleanup, cleanup_aggressive = cleanup_aggressive, archive_paths = archive_path, archive_format = archive_format, verbose=verbose)


if CLIARGV_IMPORTED and END_IMPORTED: #this is the only way the CLI could be run
    def __main__():
        """PRIVATE USED TO RUN DIRECTLY FORM THE COMMAND LINE DO NOT USE THIS IF USING THIS AS A MODULE"""
        scode = -1
        try:
            scode = 0 if main(cliargv[1:], prog_arg=cliargv[0]) else 1 #1 means not error but also no changes, 0 is no error and changes where made
        except GitCommandNotFound:
            print("Your system is not set up properly for use with the GitPython module. Please refer to it's documentation for setting it up before running this script.")
            scode = -2
        except (NoSuchPathError, FileNotFoundError, PermissionError):
            print("The given path does not exist on this system or could not be accessed by this user.")
            scode = -3
        except InvalidGitRepositoryError:
            print("The folder given is not a git repo, or is bare.")
            scode = -4
        except RepositoryDirtyError:
            print("The repository already has some changes that could end up being overwritten. Please Handle these first before running this.")
            scode = -5
        except InvalidArchiveFormatError as exc:
            print(str(exc))
            scode = -6
        end(scode)
    if __name__ == "__main__":
        __main__()
