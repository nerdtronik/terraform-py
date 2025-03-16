import sys
sys.path.append("..")
from typing import Any, Callable, Dict, List, Optional

class TerraformResult:
    def __init__(self, success: bool, result: Any):
        self.success = success
        self.result = result
        self.__dict__ = {"success": success, "result": result}

    def __str__(self):
        return f"TerraformResult(success={self.success}, result_len={len(str(self.result))})"




class Terraform:
    """
    A Python wrapper for Terraform CLI operations.

    This class provides methods for executing Terraform commands including
    init, plan, apply, show, and destroy. It handles argument formatting,
    command execution, and output parsing.

    Attributes:
        __workspace__ (str): The Terraform workspace name
        chdir (str): The directory where Terraform commands will be executed
        __lock__ (bool): Whether to use state locking
        __lock_timeout__ (str): How long to wait for state lock
        __input__ (bool): Whether to ask for input interactively
        __paralellism__ (int): Number of parallel operations
        __color__ (bool): Whether to use color in output
        __var_file__ (str): Path to variable definition file
        __version__ (dict): Terraform version information
        __planfile__ (str): Default plan file name

    Example:
        ```python
        # Initialize Terraform wrapper
        tf = Terraform(chdir="./terraform_project")

        # Run init and plan
        tf.init(upgrade=True)
        tf.plan(vars={"environment": "production"})

        # Apply the changes
        result = tf.apply(auto_approve=True)
        ```
    """
     
    chdir: str
    __version__: Dict
    __lock__: bool
    __lock_timeout__: str
    __input__: bool
    __workspace__: str
    __paralellism__: int
    __color__: bool
    __var_file__: str
    __version__:dict
    __planfile__:str

    def version(self, quiet: Optional[bool] = False) -> TerraformResult:
        """
        Retrieve Terraform version information.

        Executes 'terraform version -json' and parses the output to extract
        version details including major, minor, and patch numbers.

        Returns:
            Dict[str, Any]: A dictionary containing version information with keys:
                - version: Dict with major, minor, patch version numbers
                - version_str: Full version string
                - latest: Boolean indicating if this is the latest version
                - platform: Platform information

        Raises:
            TerraformVersionError: If unable to retrieve version information
        """
        pass

    def enable_color(self, enable: bool = True):
        """
        Set color output option.

        Args:
            enable (bool): Whether to enable color output. Defaults to True.
        """
        pass

    def enable_lock(self, enable: bool = True):
        """
        Set state locking option.

        Args:
            enable (bool): Whether to enable state locking. Defaults to True.
        """
        pass

    def enable_input(self, enable: bool = False):
        """
        Set interactive input option.

        Args:
            enable (bool): Whether to enable interactive input. Defaults to False.
        """
        pass

    def enable_lock_timeout(self, timeout: str = "0s"):
        """
        Set state lock timeout.

        Args:
            timeout (str): Lock timeout in seconds. Defaults to 0s.
        """
        pass

    @staticmethod
    def __build_arg__(arg: str, value) -> str:
        """
        Build a formatted command-line argument string for Terraform.

        Args:
            arg (str): Argument name as defined in TERRAFORM_ARGS
            value: Value for the argument, can be string, bool, or None

        Returns:
            str: Formatted argument string or empty string if the argument should be omitted
        """
        pass

    def __default_args__(
        self,
        color: Optional[bool] = None,
        lock: Optional[bool] = None,
        lock_timeout: Optional[str] = None,
        input: Optional[bool] = None,
    ) -> list:
        """Format default args

        Args:
            color (bool, optional): Enables terraform color output. Defaults to None.
            lock (bool, optional): Enables terrafom state lock. Defaults to None.
            lock_timeout (str, optional): Timeout of lock state. Defaults to None.
            input (bool, optional): Enables user input for commands that requires it. Defaults to None.

        Returns:
            list: List of cli argumments
        """

        pass

    def __global_args__(self, chdir: str = None):
        """Global terraform args formatter

        Args:
            chdir (str, optional): Workdir for terraform command to run. Defaults to None.

        Returns:
            list[str]: List of formatted cli args
        """
        pass

    @staticmethod
    def cmd(
        command: list,
        title: Optional[str] = None,
        chdir: Optional[str] = None,
        show_output: bool = True,
        callback: Optional[Callable[[Optional[str], Optional[str]], Any]] = None,
        line_callback: Optional[Callable[[Optional[str], Optional[str]], Any]] = None,
    ):
        """Run CLI Terraform command

        This method executes the specified Terraform command with the given arguments
        and returns the result. It supports callbacks for processing command output.

        Args:
            command (list): List of arguments for terraform command
            title (str, optional): Title of the command to run. Defaults to None.
            chdir (str, optional): Working directory to run the command in. Defaults to None.
            show_output (bool, optional): Show command output. Defaults to True.
            callback (Callable(str,str)->Any, optional): Function to handle command output (stdout,stderr). Defaults to None.
            line_callback (Callable(str,str)->Any, optional): Function to handle per line command output. Defaults to None.

        Returns:
            CommandResult: Result of the command with attributes:
                - success: Boolean indicating if the command succeeded
                - stdout: Standard output from the command
                - stderr: Standard error from the command
                - callback_output: Output from the callback function if provided
                - duration: Code runtime duration

        Example:
            ```python
            def process_output(stdout, stderr):
                return {"processed": stdout}

            result = tf.cmd(["show"], callback=process_output)
            ```
        """
        pass

    def cmd(
        self,
        command: list,
        title: Optional[str] = None,
        chdir: Optional[str] = None,
        show_output: bool = True,
        callback: Optional[Callable[[Optional[str], Optional[str]], Any]] = None,
        line_callback: Optional[Callable[[Optional[str], Optional[str]], Any]] = None,
    ):
        """Run CLI Terraform command

        This method executes the specified Terraform command with the given arguments
        and returns the result. It supports callbacks for processing command output.

        Args:
            command (list): List of arguments for terraform command
            title (str, optional): Title of the command to run. Defaults to None.
            chdir (str, optional): Working directory to run the command in. Defaults to None.
            show_output (bool, optional): Show command output. Defaults to True.
            callback (Callable(str,str)->Any, optional): Function to handle command output (stdout,stderr). Defaults to None.
            line_callback (Callable(str,str)->Any, optional): Function to handle per line command output. Defaults to None.

        Returns:
            CommandResult: Result of the command with attributes:
                - success: Boolean indicating if the command succeeded
                - stdout: Standard output from the command
                - stderr: Standard error from the command
                - callback_output: Output from the callback function if provided
                - duration: Code runtime duration

        Example:
            ```python
            def process_output(stdout, stderr):
                return {"processed": stdout}

            result = tf.cmd(["show"], callback=process_output)
            ```
        """
        pass

    def init(
        self,
        color: Optional[bool] = None,
        lock: Optional[bool] = None,
        lock_timeout: Optional[int] = None,
        input: Optional[bool] = None,
        upgrade: bool = False,
        reconfigure: bool = False,
        migrate_state: bool = False,
        force_copy: bool = False,
        backend: bool = True,
        backend_config: Optional[str] = None,
        get: bool = True,
        get_plugins: bool = True,
        plugin_dir: Optional[str] = None,
        readonly: bool = False,
        chdir: Optional[str] = None,
    ):
        """
        Initialize a working directory containing Terraform configuration files.

        Args:
            color (bool): Enable color output
            lock (bool): Use state locking
            lock_timeout (int): State lock timeout
            input (bool): Enable interactive input
            upgrade (bool): Upgrade modules and plugins
            reconfigure (bool): Reconfigure backend
            migrate_state (bool): Migrate state to new backend
            force_copy (bool): Force copy from previous backend
            backend (bool): Configure backend
            backend_config (str): Backend configuration
            get (bool): Download modules
            get_plugins (bool): Download plugins
            plugin_dir (str): Plugin directory
            readonly (bool): Readonly mode
            chdir (str): Directory to change to before running command

        Returns:
            bool: Success status

        Raises:
            TerraformError: If initialization fails
        """
        pass

    def get(self, update: bool = None, color: bool = None):
        """Terraform get command

        Args:
            update (bool, optional): Update state file. Defaults to None.
            color (bool, optional): Show color in outputs. Defaults to None.

        Raises:
            TerraformError: Terraform Error Exception

        Returns:
            bool: Command was successful
        """
        pass

    @staticmethod
    def __parse_vars__(vars: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Parse variable dictionary into command-line arguments.

        Args:
            vars (Dict[str, Any], optional): Dictionary of variable values.
                Defaults to None.

        Returns:
            List[str]: List of formatted variable arguments
        """
        pass

    def plan(
        self,
        out: Optional[str] = None,
        destroy: bool = False,
        refresh: Optional[bool] = True,
        refresh_only: bool = False,
        replace: Optional[str] = None,
        target: Optional[str] = None,
        vars: Optional[dict] = None,
        var_file: Optional[str] = None,
        compact_warnings: bool = False,
        input: Optional[bool] = None,
        json: bool = False,
        lock: Optional[bool] = None,
        lock_timeout: Optional[str] = None,
        color: Optional[bool] = None,
        parallelism: Optional[int] = None,
        chdir: Optional[str] = None,
        state: Optional[str] = None,
    ):
        """Terraform Plan Command

        Args:
            out (str, optional): Writes the generated plan to the given filename in an opaque file format that you can later pass to terraform apply to execute the planned changes. `-out=<filename>` arg Defaults to None.
            destroy (bool, optional): Plan terraform to destroy resources. `-destroy` arg. Defaults to False.
            refresh (bool, optional): Ignore external state changes if false. `-refresh=<true|false>` arg. Defaults to True.
            refresh_only (bool, optional): Only update terraform state. -refresh-only arg. Defaults to False.
            replace (str, optional): Instructs Terraform to plan to replace the resource instance with the given address. `-replace=<value>` arg. Defaults to None.
            target (str, optional): Instructs Terraform to focus its planning efforts only on resource instances which match the given address. `-target=<value>` arg. Defaults to None.
            vars (dict, optional): Dict of vars to pass on CLI. `-var key=value` args in dict format. Defaults to None.
            var_file (str, optional): Path to terraform vars file. `-var-file=<path>` arg. Defaults to None.
            compact_warnings (bool, optional): Shows any warning messages in a compact form. `-compact-warnings` arg. Defaults to False.
            input (bool, optional): Disables Terraform's default behavior of prompting for input for root module input variables that have not otherwise been assigned a value.`-input=<true|false>` arg. Defaults to False.
            json (bool, optional): Enables the machine readable JSON UI output. `-json` arg. Defaults to False.
            lock (bool, optional): Don't hold a state lock during the operation. `-lock=<true|false>` arg. Defaults to None.
            lock_timeout (str, optional): Unless locking is disabled with -lock=false, instructs Terraform to retry acquiring a lock for a period of time before returning an error. `-lock-timeout<int>` arg. Defaults to None.
            color (bool, optional): Enable color output. Defaults to None.
            parallelism (int, optional): Limit the number of concurrent operations as Terraform walks the graph. `-paralellism=<int>` arg. Defaults to 20.
            chdir (str, optional): Directory to run the command at. `-chdir=<path>` arg. Defaults to None.
            state (str, optional): Pass the local state file to plan. `-state=<path>` arg. Defaults to None.

        Raises:
            TerraformError: Terraform Plan Exception

        Returns:
            bool|dict: Returns true if success or the plan output file parsed with 'terraform show -json' command
        """
        pass

    @staticmethod
    def __apply_line_callback__(stdout: str = None, stderr: str = None):
        """Per line callback for apply command output

        Args:
            stdout (str, optional): Command stdout line. Defaults to None.
            stderr (str, optional): Command stderr line. Defaults to None.
        """
        pass

    @staticmethod
    def __apply_callback__(stdout: str = None, stderr: str = None):
        """Output callback for terraform apply

        Args:
            stdout (str, optional): Command result stdout. Defaults to None.
            stderr (str, optional): Command result stderr. Defaults to None.

        Returns:
            dict: Object with parsed info from the apply command in -json mode
        """
        pass

    def apply(
        self,
        plan_file: Optional[str] = None,
        auto_approve: bool = False,
        destroy: bool = False,
        refresh: Optional[bool] = True,
        refresh_only: bool = False,
        replace: Optional[str] = None,
        target: Optional[str] = None,
        vars: Optional[dict] = None,
        var_file: Optional[str] = None,
        compact_warnings: bool = False,
        input: Optional[bool] = None,
        json: bool = False,
        lock: Optional[bool] = None,
        lock_timeout: Optional[str] = None,
        color: Optional[bool] = None,
        parallelism: Optional[int] = None,
        state: Optional[str] = None,
        state_out: Optional[str] = None,
        backup: Optional[str] = None,
        chdir: Optional[str] = None,
    ):
        """Terraform Plan Command

        Args:
            plan_file (str, optional): Plan state file result. Defaults to None.
            auto_approve (bool, optional): Auto approve apply. Defaults to False.
            destroy (bool, optional): Plan terraform to destroy resources. `-destroy` arg. Defaults to False.
            refresh (bool, optional): Ignore external state changes if false. `-refresh=<true|false>` arg. Defaults to True.
            refresh_only (bool, optional): Only update terraform state. -refresh-only arg. Defaults to False.
            replace (str, optional): Instructs Terraform to plan to replace the resource instance with the given address. `-replace=<value>` arg. Defaults to None.
            target (str, optional): Instructs Terraform to focus its planning efforts only on resource instances which match the given address. `-target=<value>` arg. Defaults to None.
            vars (dict, optional): Dict of vars to pass on CLI. `-var key=value` args in dict format. Defaults to None.
            var_file (str, optional): Path to terraform vars file. `-var-file=<path>` arg. Defaults to None.
            compact_warnings (bool, optional): Shows any warning messages in a compact form. `-compact-warnings` arg. Defaults to False.
            input (bool, optional): Disables Terraform's default behavior of prompting for input for root module input variables that have not otherwise been assigned a value.`-input=<true|false>` arg. Defaults to False.
            json (bool, optional): Enables the machine readable JSON UI output. `-json` arg. Defaults to False.
            lock (bool, optional): Don't hold a state lock during the operation. `-lock=<true|false>` arg. Defaults to None.
            lock_timeout (str, optional): Unless locking is disabled with -lock=false, instructs Terraform to retry acquiring a lock for a period of time before returning an error. `-lock-timeout<int>` arg. Defaults to None.
            color (bool, optional): Enable color output. Defaults to None.
            parallelism (int, optional): Limit the number of concurrent operations as Terraform walks the graph. `-paralellism=<int>` arg. Defaults to 20.
            state (str, optional): Overrides the state filename when reading the prior state snapshot. `-state=<path>` arg. Defaults to None.
            state_out (str, optional):overrides the state filename when writing new state snapshots. `-state-out=<path>` arg. Defaults to None.
            backup (str, optional): Overrides the default filename that the local backend would normally choose dynamically to create backup files when it writes new state. `-backup=<path>` arg. Defaults to None.
            chdir (str, optional): Directory to run the command at. `-chdir=<path>` arg. Defaults to None.

        Raises:
            TerraformError: Terraform Apply Exception

        Returns:
            Any: Output from callback
        """

        pass

    def destroy(
        self,
        target: Optional[str] = None,
        vars: Optional[Dict[str, Any]] = None,
        var_file: Optional[str] = None,
        auto_approve: bool = False,
        input: Optional[bool] = None,
        color: Optional[bool] = None,
        lock: Optional[bool] = None,
        lock_timeout: Optional[str] = None,
        parallelism: Optional[int] = None,
        chdir: Optional[str] = None,
    ) -> bool:
        """
        Destroy Terraform-managed infrastructure.

        Args:
            target (str, optional): Resource address to target. Defaults to None.
            vars (Dict[str, Any], optional): Dictionary of variable values. Defaults to None.
            var_file (str, optional): Path to variable file. Defaults to None.
            auto_approve (bool): Skip interactive approval. Defaults to False.
            input (bool, optional): Enable interactive input. Defaults to None.
            color (bool, optional): Enable color output. Defaults to None.
            lock (bool, optional): Use state locking. Defaults to None.
            lock_timeout (str, optional): State lock timeout. Defaults to None.
            parallelism (int, optional): Number of parallel operations. Defaults to None.
            chdir (str, optional): Directory to change to before running command. Defaults to None.

        Returns:
            bool: Success status

        Raises:
            TerraformError: If destroy operation fails
        """
        pass

    def show(self, file: str = None, json=True, color: bool = None, chdir: str = None):
        """Terraform Show Command

        Args:
            file (str, optional): tfplan file to show. Defaults to last `plan` run output file.
            json (bool, optional): JSON output mode. `-json` arg Defaults to True.
            color (bool, optional): Enable colored output. Defines `-no-color` arg Defaults to None.
            chdir (str, optional): Directory to run the command at. `-chdir=<path>` arg. Defaults to None.

        Returns:
            dict|str: Json result of show command
        """
        pass

    def login(self, hostname: str = None, chdir: str = None):
        """Terraform Login Command

        Args:
            hostname (str, optional): Hostname to login. Defaults to None.
            chdir (str, optional): _description_. Defaults to None.

        Raises:
            TerraformLoginError: _description_

        Returns:
            _type_: _description_
        """
        pass

    def logout(self, hostname: str = None, chdir: str = None):
        pass

    @staticmethod
    def fmt(
        chdir: str = ".",
        list_files: bool = True,
        diff: bool = False,
        write: bool = True,
        check: bool = False,
        recursive: bool = False,
    ):
        pass

    def fmt(
        self,
        list_files: bool = True,
        diff: bool = False,
        write: bool = True,
        check: bool = False,
        recursive: bool = False,
        chdir: Optional[str] = None,
    ):
        pass

    def validate(
        self,
        json: Optional[bool] = False,
        color: Optional[bool] = None,
        chdir: Optional[str] = None,
    ):
        pass

    def output(
        self,
        output_name: Optional[str] = None,
        json: Optional[bool] = True,
        raw: Optional[bool] = None,
        color: Optional[bool] = None,
        state: Optional[str] = None,
        chdir: Optional[str] = None,
    ):
        pass

    def graph(
        self,
        type: Optional[str] = None,
        plan: Optional[str] = None,
        draw_cycles: Optional[bool] = False,
        module_depth: Optional[int] = None,
        chdir: Optional[str] = None,
    ):
        pass

    def Import(
        self,
        address: str,
        id: str,
        config: Optional[str] = None,
        input: Optional[bool] = None,
        lock: Optional[bool] = None,
        lock_timeout: Optional[int] = None,
        color: Optional[bool] = None,
        parallelism: Optional[int] = None,
        provider: Optional[str] = None,
        vars: Optional[Dict[str, Any]] = None,
        var_file: Optional[str] = None,
        state: Optional[str] = None,
        state_out: Optional[str] = None,
        backup: Optional[str] = None,
        chdir: Optional[str] = None,
    ):
        pass

    def __legacy_refresh__(
        self,
        target: Optional[str] = None,
        vars: Optional[dict] = None,
        var_file: Optional[str] = None,
        compact_warnings: bool = False,
        input: Optional[bool] = None,
        lock: Optional[bool] = None,
        lock_timeout: Optional[str] = None,
        color: Optional[bool] = None,
        parallelism: Optional[int] = None,
        state: Optional[str] = None,
        state_out: Optional[str] = None,
        backup: Optional[str] = None,
        chdir: Optional[str] = None,
    ):
        pass

    def refresh(
        self,
        target: Optional[str] = None,
        vars: Optional[dict] = None,
        var_file: Optional[str] = None,
        compact_warnings: bool = False,
        input: Optional[bool] = None,
        json: bool = False,
        lock: Optional[bool] = None,
        lock_timeout: Optional[str] = None,
        color: Optional[bool] = None,
        parallelism: Optional[int] = None,
        state: Optional[str] = None,
        state_out: Optional[str] = None,
        backup: Optional[str] = None,
        chdir: Optional[str] = None,
    ):
        pass

    def __legacy_taint__(
        self,
        address: str,
        backup: Optional[str] = None,
        state: Optional[str] = None,
        state_out: Optional[str] = None,
        ignore_remote_version: Optional[bool] = None,
        allow_missing: Optional[bool] = None,
        lock: Optional[bool] = None,
        lock_timeout: Optional[str] = None,
        chdir: Optional[str] = None,
    ):
        pass

    def taint(
        self,
        address: str,
        backup: Optional[str] = None,
        state: Optional[str] = None,
        state_out: Optional[str] = None,
        ignore_remote_version: Optional[bool] = None,
        allow_missing: Optional[bool] = None,
        lock: Optional[bool] = None,
        lock_timeout: Optional[str] = None,
        vars: Optional[Dict[str, Any]] = None,
        var_file: Optional[str] = None,
        chdir: Optional[str] = None,
    ):
        pass

    def untaint(
        self,
        address: str,
        backup: Optional[str] = None,
        state: Optional[str] = None,
        state_out: Optional[str] = None,
        ignore_remote_version: Optional[bool] = None,
        allow_missing: Optional[bool] = None,
        lock: Optional[bool] = None,
        lock_timeout: Optional[str] = None,
        chdir: Optional[str] = None,
    ):
        pass

    def force_unlock(
        self, lock_id: str, force: Optional[bool] = False, chdir: Optional[str] = None
    ):
        pass
