__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import locale
import os
import platform
import shlex
import shutil
import subprocess
import tempfile
import uuid
from datetime import datetime

from pakages.logger import logger

from .fileio import read_file
from .terminal import get_user, run_command


class Capturing:
    """capture output from stdout and stderr into capture object.
    This is based off of github.com/vsoch/gridtest but modified
    to write files. The stderr and stdout are set to temporary files at
    the init of the capture, and then they are closed when we exit. This
    means expected usage looks like:

    with Capturing() as capture:
        process = subprocess.Popen(...)

    And then the output and error are retrieved from reading the files:
    and exposed as properties to the client:

        capture.out
        capture.err

    And cleanup means deleting these files, if they exist.
    """

    def __enter__(self):
        self.set_stdout()
        self.set_stderr()
        self.output = []
        self.error = []
        return self

    def set_stdout(self):
        self.stdout = open(tempfile.mkstemp()[1], "w")

    def set_stderr(self):
        self.stderr = open(tempfile.mkstemp()[1], "w")

    def __exit__(self, *args):
        self.stderr.close()
        self.stdout.close()

    @property
    def out(self):
        """
        Return output stream. Returns empty string if empty or doesn't exist.
        Returns (str) : output stream written to file
        """
        if os.path.exists(self.stdout.name):
            return read_file(self.stdout.name)
        return ""

    @property
    def err(self):
        """
        Return error stream. Returns empty string if empty or doesn't exist.
        Returns (str) : error stream written to file
        """
        if os.path.exists(self.stderr.name):
            return read_file(self.stderr.name)
        return ""

    def cleanup(self):
        for filename in [self.stdout.name, self.stderr.name]:
            if os.path.exists(filename):
                os.remove(filename)


class Command:
    def __init__(self, cmd=None):
        """
        set a unique id that includes executor name (type) and random uuid)
        """
        self.cmd = cmd
        self.taskid = str(uuid.uuid4())
        self.pwd = os.getcwd()
        self.message = None
        if not hasattr(self, "data"):
            self.data = {}

    def __str__(self):
        if self.cmd:
            return "[pakages.utils.Command:%s]" % self.cmd
        return "[pakages.utils.Command]"

    def _export_host(self):
        """
        Export host information from archspec.
        """
        host = {
            "architecture": platform.machine(),
            "python-compiler": platform.python_compiler(),
            "python-version": platform.python_version(),
            "cpu-count": platform.os.cpu_count(),
            "system": platform.os.uname().sysname,
        }
        libc = "@".join(platform.libc_ver())
        if libc != "@":
            host["libc"] = libc
        return {"host": host}

    def decode(self, line):
        """Given a line of output (error or regular) decode using the
        system default, if appropriate
        """
        loc = locale.getdefaultlocale()[1]

        try:
            line = line.decode(loc)
        except:
            pass
        return line

    def _export_common(self):
        """export common task variables such as present working directory, user,
        and timestamp for when it was run. This might include envars at some
        point, but we'd need to be careful.
        """
        common = {
            "pwd": self.pwd,
            "user": get_user(),
            "timestamp": str(datetime.now()),
        }
        if self.message:
            common["message"] = self.message

        # Try to get the version of the command
        cmd = self.data.get("cmd", [])
        if cmd:
            binary = shutil.which(cmd[0])
            if not binary:
                logger.exit(
                    "Error parsing command %s - did you forget the executable?"
                    % " ".join(cmd)
                )
            res = run_command([binary, "--version"])
            if res["return_code"] != 0:
                res = run_command([binary, "version"])
            if res["return_code"] == 0:
                common["version"] = res["message"].strip()

        return common

    def export(self):
        """
        Return data as json.
        """
        # Get common context (e.g., pwd)
        common = self._export_common()
        common.update(self._export_host())
        common.update(self.data)
        return common

    def get_command(self, cmd=None):
        cmd = cmd or self.cmd
        if not cmd:
            logger.exit("A command (cmd) is required.")
        if not isinstance(cmd, list):
            cmd = shlex.split(cmd)
        return cmd

    def run(self, cmd=None):
        """Run and capture a shell command.
        We use Capturing and then save attributes like the pid, output, error
        to it, and return to the calling function.
        """
        cmd = self.get_command(cmd)

        # Capturing provides temporary output and error files
        with Capturing() as capture:
            process = subprocess.Popen(
                cmd,
                stdout=capture.stdout,
                stderr=capture.stderr,
                universal_newlines=True,
            )
            capture.pid = process.pid
            returncode = process.poll()

            # Iterate through the output
            while returncode is None:
                returncode = process.poll()

        # Get the remainder of lines, add return code
        capture.output = self.decode(capture.out)
        capture.error = self.decode(capture.err)

        # Cleanup capture files and save final return code
        capture.cleanup()
        capture.returncode = returncode
        return capture

    def summary(self):
        return "[%s]" % self.name
