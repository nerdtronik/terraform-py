from typing import Optional


class CommandError(Exception):
    def __init__(self, err: str, code: int, stdout: str, stderr: str):
        self.code = code
        self.stdout = stdout
        self.stderr = stderr
        self.err = err
        # Build a detailed error message
        full_message = ""
        full_message += f"\nCode: {code}"
        if len(stdout) > 0:
            full_message += f"\nStdout:\n{stdout}"
        full_message += f"\nStderr:\n{stderr}"
        full_message += f"\nDetails:\n{err}"
        super().__init__(full_message)


class TerraformError(Exception):
    """Base exception class for all Terraform-related errors.

    This class serves as the foundation for all specialized Terraform
    exceptions, providing consistent error handling patterns.

    Attributes:
        message (str): The error message
        command (str): The Terraform command that failed (optional)
        stderr (str): Standard error output from Terraform (optional)
        duration (float): Time taken before the error occurred (optional)
    """

    def __init__(
        self,
        message,
        cmd_name: str,
        cmd: Optional[str] = None,
        stderr: Optional[str] = None,
        duration: Optional[float] = None,
    ):
        self.message = message
        self.command = cmd_name
        self.cli_command = cmd
        self.stderr = stderr
        self.duration = duration
        super().__init__(self.format_message())

    def format_message(self):
        # Build a detailed error message
        full_message = self.message + f"\nTerraform command: {self.command}"
        if self.cli_command is not None:
            full_message += f"\nCLI Call Command: {self.cli_command}"
        if self.duration is not None:
            full_message += f"\nDuration: {self.duration:.4f}s"
        if self.stderr:
            full_message += f"\nDetails:\n{self.stderr}"
        return full_message
