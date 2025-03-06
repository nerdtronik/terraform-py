import subprocess
import shlex
from .logger import log


def split_array_by_value(array, split_value):
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


def clean_command(cmd: list) -> list:
    return list(filter(lambda x: x is not None and len(x) > 0, cmd))
    # res =[shlex.quote(item) for item in res]
    print(res)
    return res


def cmd_to_array(cmd: str) -> list:
    return split_array_by_value(shlex.split(cmd), "|")


class CommandResult:
    success: str
    code: int
    stdout: str
    stderr: str
    callback_output: any
    line_callback_output: any

    def __init__(self, success: bool, code: int, stdout: str, stderr: str, callback_output: any, line_callback_output: any):
        self.success = success
        self.code = code
        self.stdout = stdout
        self.stderr = stderr
        self.callback_output = callback_output,
        self.line_callback_output = line_callback_output


def run_command(cmd: list, line_callback=None, callback=None, show_output=True, cwd: str = ".", title: str = "") -> CommandResult:
    if show_output and len(title) > 0:
        log.info(f"Running: {title}")

    if isinstance(cmd[0], list):
        cmd[0] = clean_command(cmd[0])
        proc = subprocess.Popen(cmd[0], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, cwd=cwd)
        for _cmd in cmd[1:]:
            _cmd = clean_command(_cmd)
            proc = subprocess.Popen(_cmd, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, stdin=proc.stdout, cwd=cwd)
    else:
        cmd = clean_command(cmd)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, cwd=cwd)
    stdout = ""
    stderr = ""
    line_callback_result = []

    while True:
        line = proc.stdout.readline()
        error_line = proc.stderr.readline()
        if not line and not error_line:
            break
        else:
            if error_line:
                error_line = error_line.decode("utf-8")
                stderr += error_line
                if show_output:
                    log.error(error_line.replace("\n", ""))

            if line:
                line = line.decode("utf-8")
                stdout += line
                if show_output:
                    log.info(line.replace("\n", ""))

            if line_callback:
                line_callback_result.append(line_callback(line, error_line))
    proc.wait()
    res_callback = None
    if callback:
        res_callback = callback(stdout, stderr)

    return CommandResult(proc.returncode == 0, proc.returncode, stdout, stderr, res_callback, list(filter(lambda x: x is not None, line_callback_result)))
