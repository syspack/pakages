__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2023, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import os
import shlex
import shutil
import subprocess

from pakages.logger import logger


def which(software, strip_newline=True):
    """get_install will return the path to where Singularity (or another
    executable) is installed.
    """
    return shutil.which(software)


def check_install(software, quiet=True, command="--version"):
    """check_install will attempt to run the singularity command, and
    return True if installed. The command line utils will not run
    without this check.

    Parameters
    ==========
    software: the software to check if installed
    quiet: should we be quiet? (default True)
    command: the command to use to check (defaults to --version)
    """
    cmd = [software, command]
    try:
        version = run_command(cmd, software)
    except Exception:  # FileNotFoundError
        return False
    if version:
        if not quiet and version["return_code"] == 0:
            version = version["message"]
            logger.info("Found %s version %s" % (software.upper(), version))
        return True
    return False


def get_installdir():
    """get_installdir returns the installation directory of the application"""
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def get_userhome():
    """get the user home based on the effective uid. If import of pwd fails
    (not supported for Windows) then fall back to environment variable.
    """
    try:
        import pwd

        return pwd.getpwuid(os.getuid())[5]
    except Exception:
        return os.environ.get("HOME") or os.environ.get("HOMEPATH")


def get_user():
    """Get the name of the user. We first try to import pwd, but fallback to
    extraction from the environment.
    """
    try:
        import pwd

        return pwd.getpwuid(os.getuid())[0]
    except Exception:
        return os.environ.get("USER") or os.environ.get("USERNAME")


def stream_command(cmd):
    """stream a command (yield) back to the user, as each line is available.

    # Example usage:
    results = []
    for line in stream_command(cmd):
        print(line, end="")
        results.append(line)

    Parameters
    ==========
    cmd: the command to send, should be a list for subprocess
    """
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )

    # Allow the runner to choose streaming output or error
    stream = process.stdout.readline

    # Stream lines back to the caller
    for line in iter(stream, ""):
        yield line

    # If there is an error, raise.
    process.stdout.close()
    return_code = process.wait()
    if return_code != 0:
        error = process.stderr.read().strip("\n")
        logger.error(error)
        raise subprocess.CalledProcessError(return_code, cmd, error)


def run_command(cmd):
    """run_command uses subprocess to send a command to the terminal.

    Parameters
    ==========
    cmd: the command to send, should be a list for subprocess
    error_message: the error message to give to user if fails,
    if none specified, will alert that command failed.

    """
    if not isinstance(cmd, list):
        cmd = shlex.split(cmd)

    output = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    t = output.communicate()[0], output.returncode
    output = {"message": t[0], "return_code": t[1]}

    if isinstance(output["message"], bytes):
        output["message"] = output["message"].decode("utf-8")
    return output


def confirm_action(question, force=False):
    """confirm if the user wants to perform a certain action

    Parameters
    ==========
    question: the question that will be asked
    force: if the user wants to skip the prompt
    """
    if force is True:
        return True

    response = input(question)
    while len(response) < 1 or response[0].lower().strip() not in "ynyesno":
        response = input("Please answer yes or no: ")

    if response[0].lower().strip() in "no":
        return False

    return True
