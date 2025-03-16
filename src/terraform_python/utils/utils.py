import sys

sys.path.append("..")

import os
import shlex
import subprocess
from time import time
from typing import Any, Callable, List, Optional, Union

from ..classes import CommandError
from .logger import log


def split_array_by_value(array: List[str], split_value: str) -> List[List[str]]:
    """
    Split an array into subarrays based on a delimiter value.

    Args:
        array: The input array to split
        split_value: The value to use as a delimiter

    Returns:
        A list of subarrays, split at each occurrence of the split_value
    """
    if not split_value in array:
        return array
    result = []
    current_sub_array = []
    for element in array:
        if element == split_value:
            if current_sub_array:
                result.append(current_sub_array)
            current_sub_array = []
        else:
            current_sub_array.append(element)
    if current_sub_array:
        result.append(current_sub_array)

    return result


def clean_command(cmd: List[str]) -> List[str]:
    """
    Clean a command list by removing None values and empty strings.

    Args:
        cmd: List of command arguments

    Returns:
        Filtered list with only valid command arguments
    """
    res = list(filter(lambda x: x is not None and len(x) > 0, cmd))
    # res =[shlex.quote(item) for item in res]
    # print(res)
    return res


def cmd_to_array(cmd: str) -> List[List[str]]:
    """
    Convert a command string with pipes into a list of command arrays.

    Args:
        cmd: Command string potentially containing pipe characters

    Returns:
        A list of command arrays, each representing a command in the pipeline
    """
    try:
        return split_array_by_value(shlex.split(cmd), "|")
    except ValueError as e:
        log.error(f"Error parsing command: {e}")
        return [[]]


class CommandResult:
    """
    Container for the results of a command execution.
    """

    def __init__(
        self,
        success: bool,
        code: int,
        command: str,
        stdout: str,
        stderr: str,
        callback_output: Any,
        line_callback_output: List[Any],
        start_time: float = time(),
        result: Optional[Any] = None,
    ):
        self.success = success
        self.code = code
        self.command = command
        self.stdout = stdout
        self.stderr = stderr
        self.callback_output = callback_output
        self.line_callback_output = line_callback_output
        self.duration = round(time() - start_time, 4)
        self.result = result

    def __str__(self) -> str:
        """String representation of the command result."""
        return f"CommandResult(success={self.success}, code={self.code}, command={' '.join(self.command)}, stdout_len={len(self.stdout)}, stderr_len={len(self.stderr)}, duration={self.duration}s)"

    def raise_for_status(self) -> None:
        """Raise an exception if the command failed."""
        if not self.success:
            raise CommandError("Command failed", self.code, self.stdout, self.stderr)


def run_command(
    cmd: Union[List[str], List[List[str]]],
    line_callback: Optional[Callable[[str, str], Any]] = None,
    callback: Optional[Callable[[str, str], Any]] = None,
    show_output: bool = True,
    cwd: str = ".",
    title: str = "",
    env: Optional[dict] = None,
    timeout: Optional[int] = None,
) -> CommandResult:
    """
    Execute a command with optional callbacks for line-by-line processing.

    Args:
        cmd: Command to execute, either a single list or a list of lists for piping
        line_callback: Optional callback function called for each line of output
        callback: Optional callback function called with complete stdout and stderr
        show_output: Whether to display output in the logs
        cwd: Working directory for the command
        title: Optional title to display in logs
        env: Optional environment variables to pass to the subprocess
        timeout: Optional timeout in seconds

    Returns:
        CommandResult object containing execution results
    """
    start_time = time()
    print(cmd)
    cmd = split_array_by_value(cmd, "|")
    # Prepare environment variables
    process_env = os.environ.copy()
    if env:
        process_env.update(env)

    if show_output:
        if len(title) > 0:
            log.info(f"Running: {title}", start_sub=True)
            log.debug(f"Command: {cmd}")
        if cwd != ".":
            log.info(f"Working directory: {cwd}")

    try:
        if isinstance(cmd[0], list):
            print(cmd)
            cmd[0] = clean_command(cmd[0])
            proc = subprocess.Popen(
                cmd[0],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
                env=process_env,
                # universal_newlines=True,
            )
            for _cmd in cmd[1:]:
                _cmd = clean_command(_cmd)
                proc = subprocess.Popen(
                    _cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=proc.stdout,
                    cwd=cwd,
                    env=process_env,
                    # universal_newlines=True,
                )
        else:
            cmd = clean_command(cmd)
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
                env=process_env,
                # universal_newlines=True,
            )
    except FileNotFoundError as e:
        raise CommandError(e.strerror, 127, "", f"Command not found: {e}")
    except Exception as e:
        raise CommandError(e.with_traceback(), proc.returncode, "", proc.stderr.read())

    stdout = ""
    stderr = ""
    line_callback_result = []

    try:
        # Use a timeout if specified
        if timeout:
            # Set up a timer to terminate the process if it exceeds the timeout
            proc_timeout = timeout
        else:
            proc_timeout = None

        while True:
            line = proc.stdout.readline().decode("utf-8", errors="ignore")
            error_line = proc.stderr.readline().decode("utf-8", errors="ignore")

            if not line and not error_line:
                break

            # try:

            if error_line:
                # No need to decode since we're using text mode
                stderr += error_line
                if show_output:
                    log.error(error_line.rstrip())

            if line:
                # No need to decode since we're using text mode
                stdout += line
                if show_output:
                    log.info(line.rstrip())

            if line_callback:
                try:
                    result = line_callback(line, error_line)
                    if result is not None:
                        line_callback_result.append(result)
                except Exception as e:
                    log.error(e)

        proc.wait(timeout=proc_timeout)
        res_callback = None
        if callback:
            try:
                res_callback = callback(stdout, stderr)
            except Exception as e:
                log.error(e)

        return CommandResult(
            proc.returncode == 0,
            proc.returncode,
            " ".join(clean_command(cmd)),
            stdout,
            stderr,
            res_callback,
            line_callback_result,
            start_time,
        )
    except subprocess.TimeoutExpired as e:
        proc.kill()
        log.error(f"Command timed out after {timeout} seconds")
        raise CommandError(
            e.cmd,
            -1,
            stdout,
            stderr + f"\nCommand timed out after {timeout} seconds",
        )
    except Exception as e:
        proc.kill()
        log.error(f"Exception during command execution: {str(e)}")
        import json

        raise CommandError(
            json.dumps(e.args),
            -1,
            stdout,
            stderr + f"\nException during execution: {str(e)}",
        )
