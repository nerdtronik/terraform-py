import json as _json
import os
import re
import shlex
from typing import Any, Callable, Dict, List, Optional

from .utils import cmd_to_array, log, run_command, clean_command

from .classes import *  # noqa  # isort:skip

os.environ["TF_IN_AUTOMATION"] = "1"
# os.environ['TF_LOG'] = 'trace'
log.set_env("Terraform")
log.show_file(False)
log.set_level("info")


class Terraform:

    def __init__(
        self,
        workspace: Optional[str] = "default",
        chdir: Optional[str] = None,
        lock: Optional[bool] = True,
        lock_timeout: Optional[str] = "0s",
        input: Optional[bool] = False,
        parallelism: Optional[int] = 10,
        color: Optional[bool] = True,
        var_file: Optional[str] = None,
    ):
        self.__workspace__ = workspace
        self.chdir = chdir
        self.__lock__ = lock
        self.__lock_timeout__ = lock_timeout
        self.__input__ = input
        self.__paralellism__ = parallelism
        self.__color__ = color
        self.__var_file__ = var_file
        self.__version__ = {}
        self.__planfile__ = "plan.tfplan"
        self.state = State(self)
        self.workspace = Workspace(self)
        log.set_env(self.workspace.current)
        self.version(quiet=True)
        if workspace != "default":
            log.info("Trying to select workspace")
            try:
                self.workspace.select(workspace, or_create=True, quiet=True)
            except Exception as e:
                log.warn(
                    "Failed to switch workspace, please run the 'init' command first."
                )

    def version(self, quiet: Optional[bool] = False) -> TerraformResult:
        if not quiet:
            log.info("Running: Terraform version", start_sub=True)
        result = self.cmd(["version", "-json"], show_output=False)
        if not result.success:
            if not quiet:
                log.failed("Failed to retrieve terraform version", end_sub=True)
            raise TerraformError(
                "Failed to retrieve terrform version",
                "version",
                result.command,
                result.stderr,
                result.duration,
            )
        version = _json.loads(result.stdout)
        print(version)
        version_str = version["terraform_version"]

        version_dict = VERSION_REGEX.match(version_str)
        if version_dict:
            version_dict = version_dict.groupdict()
            for key in version_dict.keys():
                version_dict[key] = int(version_dict[key])
        else:
            version_dict = dict(major=0, minor=0, patch=0)
        res = {
            "version": version_dict,
            "version_str": version_str,
            "latest": version["terraform_outdated"] == False,
            "platform": version["platform"],
        }
        self.__version__ = res
        if not quiet:
            log.success(
                f"Terraform version retrieved successfully in {result.duration}s",
                end_sub=True,
            )
        return TerraformResult(True, res)

    def enable_color(self, enable: bool = True):
        self.__color__ = enable

    def enable_lock(self, enable: bool = True):
        self.__lock__ = enable

    def enable_input(self, enable: bool = False):
        self.__input__ = enable

    def enable_lock_timeout(self, timeout: str = "0s"):
        self.__lock_timeout__ = timeout

    @staticmethod
    def __build_arg__(arg: str, value) -> str:
        res = TERRAFORM_ARGS[arg]
        if res[-1] == "=" and value is not None:
            if isinstance(value, bool):
                res += "true" if value else "false"
            elif isinstance(value, str) and len(value) == 0:
                return ""
            elif value is not None and len(str(value)) > 0:
                res += shlex.quote(str(value))

        elif isinstance(value, bool):
            return res if value else ""
        else:
            return ""
        return res

    def __default_args__(
        self,
        color: Optional[bool] = None,
        lock: Optional[bool] = None,
        lock_timeout: Optional[str] = None,
        input: Optional[bool] = None,
    ) -> list:
        args = []

        if color is not None:
            args.append(Terraform.__build_arg__("color", not color))
        elif self.__color__ is False:
            args.append(TERRAFORM_ARGS["color"])
        if lock is not None and lock is False:
            args.append(Terraform.__build_arg__("lock", lock))
        elif self.__lock__ is False:
            args.append(Terraform.__build_arg__("lock", self.__lock__))

        if lock_timeout is not None and lock_timeout != "0s":
            args.append(Terraform.__build_arg__("lock_timeout", lock_timeout))
        elif self.__lock_timeout__ != "0s":
            args.append(Terraform.__build_arg__("lock_timeout", self.__lock_timeout__))

        if input is not None:
            args.append(Terraform.__build_arg__("input", input))
        elif self.__input__ is False:
            args.append(Terraform.__build_arg__("input", self.__input__))
        return args

    def __global_args__(self, chdir: str = None):
        args = []

        if chdir is not None:
            args.append(Terraform.__build_arg__("chdir", chdir))
        elif self.chdir is not None and self.chdir != ".":
            args.append(Terraform.__build_arg__("chdir", self.chdir))
        return args

    @staticmethod
    def cmd(
        command: list,
        title: Optional[str] = None,
        chdir: Optional[str] = None,
        show_output: bool = True,
        callback: Optional[Callable[[Optional[str], Optional[str]], Any]] = None,
        line_callback: Optional[Callable[[Optional[str], Optional[str]], Any]] = None,
    ):
        cmd = ["terraform", *command]
        return run_command(
            cmd,
            title=title,
            cwd=chdir,
            show_output=show_output,
            callback=callback,
            line_callback=line_callback,
        )

    def cmd(
        self,
        command: list,
        title: Optional[str] = None,
        chdir: Optional[str] = None,
        show_output: bool = True,
        callback: Optional[Callable[[Optional[str], Optional[str]], Any]] = None,
        line_callback: Optional[Callable[[Optional[str], Optional[str]], Any]] = None,
    ):
        if not chdir:
            chdir = self.chdir
        cmd = ["terraform", *command]
        return run_command(
            cmd,
            title=title,
            cwd=chdir,
            show_output=show_output,
            callback=callback,
            line_callback=line_callback,
        )

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
        cmd = ["init"]
        if readonly:
            cmd.append(Terraform.__build_arg__("readonly", readonly))

        cmd.extend(
            self.__default_args__(
                color=color, lock=lock, lock_timeout=lock_timeout, input=input
            )
        )

        cmd.append(Terraform.__build_arg__("upgrade", upgrade))
        cmd.append(Terraform.__build_arg__("reconfigure", reconfigure))
        cmd.append(Terraform.__build_arg__("migrate_state", migrate_state))
        cmd.append(Terraform.__build_arg__("force_copy", force_copy))
        cmd.append(Terraform.__build_arg__("backend_config", backend_config))
        cmd.append(Terraform.__build_arg__("plugin_dir", plugin_dir))
        # cmd.append(Terraform.__build_arg__("lockfile", lockfile))

        if not backend:
            cmd.append(Terraform.__build_arg__("backend", backend))
        if not get:
            cmd.append(Terraform.__build_arg__("get", get))
        if not get_plugins:
            cmd.append(Terraform.__build_arg__("get_plugins", get_plugins))

        result = self.cmd(cmd, title="Terraform init", chdir=chdir)
        if not result.success:
            log.failed(
                f"Terraform init failed in: {result.duration} seconds", end_sub=True
            )
            raise TerraformError(
                "Failed to initialize terraform project",
                "init",
                result.command,
                result.stderr,
                result.duration,
            )
        log.success(
            f"Terraform init completed in: {result.duration} seconds", end_sub=True
        )
        log.info(self.workspace.current, self.__workspace__)
        if self.workspace.current != self.__workspace__:
            self.workspace.list(True)
            if self.workspace.current != self.__workspace__:
                self.__workspace__ = self.workspace.select(
                    self.__workspace__, or_create=True
                ).result
        return TerraformResult(True, result.stdout)

    def get(self, update: bool = None, color: bool = None):
        cmd = ["get"]
        cmd.append(Terraform.__build_arg__("update", update))
        cmd.append(Terraform.__build_arg__("color", not color))

        result = self.cmd(cmd, title="Terraform get", chdir=self.chdir)
        if not result.success:
            log.failed(
                f"Terraform get failed in: {result.duration} seconds", end_sub=True
            )
            raise TerraformError(
                "Failed to run terraform get",
                "get",
                result.command,
                result.stderr,
                result.duration,
            )
        log.success(
            f"Terraform get completed in: {result.duration} seconds", end_sub=True
        )
        return TerraformResult(True, result.stdout)

    @staticmethod
    def __parse_vars__(vars: Optional[Dict[str, Any]] = None) -> List[str]:
        if not vars:
            return []
        args = []
        for key in vars.keys():
            value = vars[key]
            if isinstance(value, str):
                value = re.sub(r"\"", '\\"', value)
                value = f'"{value}"'
            elif (
                isinstance(value, dict)
                or isinstance(value, list)
                or isinstance(value, tuple)
            ):
                value = _json.dumps(value)
            args.append("-var")
            args.append(f"{key}={value}")
        return args

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
        cmd = ["plan"]
        cmd.extend(
            self.__default_args__(
                color=color, lock=lock, lock_timeout=lock_timeout, input=input
            )
        )
        if not out:
            out = self.__planfile__
        cmd.append(Terraform.__build_arg__("out", out))

        if (
            self.__version__["version"]["major"] >= 1
            and self.__version__["version"]["minor"] >= 0
        ):
            cmd.append(Terraform.__build_arg__("refresh_only", refresh_only))
        else:
            log.warn(
                f"the option '-refresh-only' is supported since the version 1.1.0, and your version is {self.__version__['version_str']}"
            )
        if (
            self.__version__["version"]["major"] >= 1
            and self.__version__["version"]["minor"] >= 0
        ):
            cmd.append(Terraform.__build_arg__("json", json))
        else:
            log.warn(
                f"the option '-json' is supported since the version 1.0.0, and your version is {self.__version__['version_str']}"
            )
        if not parallelism:
            parallelism = self.__paralellism__
        cmd.append(Terraform.__build_arg__("parallelism", parallelism))

        cmd.append(Terraform.__build_arg__("destroy", destroy))
        cmd.append(Terraform.__build_arg__("refresh", refresh))
        cmd.append(Terraform.__build_arg__("replace", replace))
        cmd.append(Terraform.__build_arg__("target", target))
        cmd.append(Terraform.__build_arg__("var_file", var_file))
        cmd.append(Terraform.__build_arg__("state", state))
        cmd.append(Terraform.__build_arg__("compact_warnings", compact_warnings))

        cmd.extend(Terraform.__parse_vars__(vars))

        result = self.cmd(cmd, title="Terraform plan", chdir=chdir)
        if not result.success:
            log.failed(
                f"Terraform plan failed in: {result.duration} seconds", end_sub=True
            )
            raise TerraformError(
                "Failed to run plan terraform",
                "plan",
                result.command,
                result.stderr,
                result.duration,
            )
        log.success(
            f"Terraform plan completed in: {result.duration} seconds", end_sub=True
        )
        return TerraformResult(
            True, dict(stdout=result.stdout, output=result.callback_output)
        )

    @staticmethod
    def __apply_line_callback__(stdout: str = None, stderr: str = None):
        if stdout:
            stdout = _json.loads(stdout)
            log.info(stdout["@message"])

    @staticmethod
    def __apply_callback__(stdout: str = None, stderr: str = None):
        result = {}
        for line in stdout.splitlines():
            try:
                line = _json.loads(line)
                if line["type"] == "outputs":
                    result["outputs"] = line["outputs"]
                elif line["type"] == "change_summary":
                    result["changes"] = line["changes"]
                elif line["type"] == "apply_complete":
                    if not "result" in result:
                        result["result"] = {}
                    addr = line["hook"]["resource"]["addr"]
                    result["result"][addr] = line["hook"]

            except:
                pass
        return result

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
        cmd = ["apply"]
        cmd.extend(
            self.__default_args__(
                color=color, lock=lock, lock_timeout=lock_timeout, input=input
            )
        )

        callback = None
        line_callback = None

        if self.__version__["version"]["major"] >= 1:
            cmd.append(Terraform.__build_arg__("json", json))
            if json:
                line_callback = Terraform.__apply_line_callback__
                callback = Terraform.__apply_callback__

        if not parallelism:
            cmd.append(Terraform.__build_arg__("parallelism", self.__paralellism__))
        else:
            cmd.append(Terraform.__build_arg__("parallelism", parallelism))
        cmd.append(Terraform.__build_arg__("auto_approve", auto_approve))
        cmd.append(Terraform.__build_arg__("compact_warnings", compact_warnings))

        cmd.append(Terraform.__build_arg__("state", state))
        cmd.append(Terraform.__build_arg__("state_out", state_out))
        cmd.append(Terraform.__build_arg__("backup", backup))
        cmd.append(Terraform.__build_arg__("var_file", var_file))
        cmd.extend(Terraform.__parse_vars__(vars))

        cmd.append(Terraform.__build_arg__("destroy", destroy))
        cmd.append(Terraform.__build_arg__("refresh", refresh))
        cmd.append(Terraform.__build_arg__("replace", replace))
        cmd.append(Terraform.__build_arg__("target", target))
        if (
            self.__version__["version"]["major"] >= 1
            and self.__version__["version"]["minor"] >= 0
        ):
            cmd.append(Terraform.__build_arg__("refresh_only", refresh_only))
        else:
            log.warn(
                f"the option '-refresh-only' is supported since the version 1.1.0, and your version is {self.__version__['version_str']}"
            )
        if not plan_file:
            cmd.append(shlex.quote(self.__planfile__))
        else:
            cmd.append(shlex.quote(plan_file))
        result = self.cmd(
            cmd,
            title="Terraform apply",
            chdir=chdir,
            line_callback=line_callback,
            callback=callback,
            show_output=not (json and self.__version__["version"]["major"] >= 1),
        )
        res = TerraformResult(True, result.stdout)
        if not result.success:
            log.failed(
                f"Terraform apply failed in: {result.duration} seconds", end_sub=True
            )
            raise TerraformError(
                "Failed to apply changes to state",
                "apply",
                result.command,
                result.stderr,
                result.duration,
            )
        log.success(
            f"Terraform apply completed in: {result.duration} seconds", end_sub=True
        )
        if json and self.__version__["version"]["major"] >= 1:
            res.result = dict(stdout=result.stdout, output=result.callback_output)
        return res

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
        cmd = ["destroy"]

        cmd.extend(
            self.__default_args__(
                color=color, lock=lock, lock_timeout=lock_timeout, input=input
            )
        )

        if not parallelism:
            cmd.append(Terraform.__build_arg__("parallelism", self.__paralellism__))
        else:
            cmd.append(Terraform.__build_arg__("parallelism", parallelism))

        cmd.append(Terraform.__build_arg__("auto_approve", auto_approve))
        cmd.append(Terraform.__build_arg__("target", target))
        cmd.append(Terraform.__build_arg__("var_file", var_file))

        cmd.extend(self.__parse_vars__(vars))

        result = self.cmd(cmd, title="Terraform destroy", chdir=chdir)
        if not result.success:
            log.failed(
                f"Terraform destroy failed in: {result.duration} seconds",
                end_sub=True,
            )
            error_message = f"Failed to destroy terraform resources"
            raise TerraformError(
                error_message,
                "destroy",
                result.command,
                result.stderr,
                result.duration,
            )
        log.success(
            f"Terraform destroy completed in: {result.duration} seconds",
            end_sub=True,
        )
        return TerraformResult(True, result.stdout)

    def show(self, file: str = None, json=True, color: bool = None, chdir: str = None):
        cmd = ["show"]
        # log.info("Running Terraform show")
        cmd.append(Terraform.__build_arg__("json", json))

        if color is not None:
            cmd.append(Terraform.__build_arg__("color", not color))
        else:
            cmd.append(Terraform.__build_arg__("color", not self.__color__))

        if not file:
            cmd.append(shlex.quote(self.__planfile__))
        else:
            cmd.append(shlex.quote(file))

        result = self.cmd(cmd, title="Terraform show", chdir=chdir, show_output=True)
        res = TerraformResult(True, result.stdout)
        if not result.success:
            log.failed(
                f"Failed to show terraform state in: {result.duration} seconds",
                end_sub=True,
            )
            raise TerraformError(
                "Failed to run terraformshow command",
                "show",
                result.command,
                result.stderr,
                result.duration,
            )
        log.success(
            f"Terraform show completed in: {result.duration} seconds", end_sub=True
        )
        if json:
            res.result = _json.loads(result.stdout)
        return res

    def login(self, hostname: str = None, chdir: str = None):
        cmd = ["login"]
        if hostname:
            cmd.append(shlex.quote(hostname))

        result = self.cmd(cmd, title="Terraform login", chdir=chdir)
        res = TerraformResult(True, result.stdout)
        if result.success:
            log.failed(
                f"Terraform login failed in: {result.duration} seconds", end_sub=True
            )
            raise TerraformError(
                f"Failed to terraform login to host '{hostname}'",
                "login",
                result.command,
                result.stderr,
                result.duration,
            )
        log.success(
            f"Terraform login completed in: {result.duration} seconds", end_sub=True
        )
        return res

    def logout(self, hostname: str = None, chdir: str = None):
        cmd = ["logout"]
        if hostname:
            cmd.append(shlex.quote(hostname))

        result = self.cmd(cmd, title="Terraform logout", chdir=chdir)
        res = TerraformResult(True, result.stdout)
        if not result.success:
            log.failed(
                f"Terraform logout failed in: {result.duration} seconds",
                end_sub=True,
            )
            raise TerraformError(
                f"Failed to terraform logout to host '{hostname}'",
                "logout",
                result.command,
                result.stderr,
                result.duration,
            )
        log.success(
            f"Terraform logout completed in: {result.duration} seconds",
            end_sub=True,
        )
        return res

    @staticmethod
    def fmt(
        chdir: str = ".",
        list_files: bool = True,
        diff: bool = False,
        write: bool = True,
        check: bool = False,
        recursive: bool = False,
    ):
        cmd = ["fmt"]
        cmd.append(Terraform.__build_arg__("diff", diff))
        cmd.append(Terraform.__build_arg__("check", check))
        cmd.append(Terraform.__build_arg__("recursive", recursive))
        if list_files is False:
            cmd.append(Terraform.__build_arg__("list", list_files))
        if write is False:
            cmd.append(Terraform.__build_arg__("write", write))

        result = Terraform.cmd(cmd, "Terraform fmt", chdir=chdir)
        res = TerraformResult(True, result.stdout)
        if not result.success:
            log.failed(f"Terraform fmt failed in {result.duration}s", end_sub=True)
            raise TerraformError(
                "Failed to run terraform fmt",
                "fmt",
                result.command,
                result.stderr,
                result.duration,
            )
        log.success(f"Terraform fmt completed in {result.duration}s", end_sub=True)
        return res

    def fmt(
        self,
        list_files: bool = True,
        diff: bool = False,
        write: bool = True,
        check: bool = False,
        recursive: bool = False,
        chdir: Optional[str] = None,
    ):
        cmd = ["fmt"]

        cmd.append(Terraform.__build_arg__("diff", diff))
        cmd.append(Terraform.__build_arg__("check", check))
        cmd.append(Terraform.__build_arg__("recursive", recursive))
        if list_files is False:
            cmd.append(Terraform.__build_arg__("list", list_files))
        if write is False:
            cmd.append(Terraform.__build_arg__("write", write))
        result = self.cmd(cmd, "Terraform fmt", chdir)
        res = TerraformResult(True, result.stdout)
        if not result.success:
            log.failed(f"Terraform fmt failed in {result.duration}s", end_sub=True)
            raise TerraformError(
                "Failed to run terraform fmt",
                "fmt",
                result.command,
                result.stderr,
                result.duration,
            )
        log.success(f"Terraform fmt completed in {result.duration}s", end_sub=True)
        return res

    def validate(
        self,
        json: Optional[bool] = False,
        color: Optional[bool] = None,
        chdir: Optional[str] = None,
    ):
        cmd = ["validate"]

        if color is False:
            color = self.__color__
        cmd.append(Terraform.__build_arg__("color", not color))
        cmd.append(Terraform.__build_arg__("json", json))
        result = self.cmd(cmd, "Terraform validate", chdir)
        res = TerraformResult(True, result.stdout)
        if not result.success:
            log.failed(f"Terraform validate failed in {result.duration}s", end_sub=True)
            raise TerraformError(
                "Failed to run terraform validate",
                "validate",
                result.command,
                result.stderr,
                result.duration,
            )
        log.success(f"Terraform validate completed in {result.duration}s", end_sub=True)
        return res

    def output(
        self,
        output_name: Optional[str] = None,
        json: Optional[bool] = True,
        raw: Optional[bool] = None,
        color: Optional[bool] = None,
        state: Optional[str] = None,
        chdir: Optional[str] = None,
    ):
        cmd = ["output"]
        if json:
            log.info("Terraform output started", start_sub=True)
        if not color:
            color = self.__color__
        cmd.append(Terraform.__build_arg__("color", not color))
        cmd.append(Terraform.__build_arg__("json", json))
        cmd.append(Terraform.__build_arg__("raw", raw))
        cmd.append(Terraform.__build_arg__("state", state))
        if output_name:
            cmd.append(shlex.quote(output_name))
        result = self.cmd(cmd, "Terraform output", chdir, show_output=not json)
        res = TerraformResult(True, result.stdout)
        if not result.success:
            log.failed(f"Terraform output failed in {result.duration}s", end_sub=True)
            raise TerraformError(
                "Failed to run terraform output",
                "output",
                result.command,
                result.stderr,
                result.duration,
            )
        log.success(f"Terraform output completed in {result.duration}s", end_sub=True)
        if json:
            res.result = _json.loads(result.stdout)
        return res

    def graph(
        self,
        type: Optional[str] = None,
        plan: Optional[str] = None,
        draw_cycles: Optional[bool] = False,
        module_depth: Optional[int] = None,
        chdir: Optional[str] = None,
    ):
        cmd = ["graph"]

        if type:
            if type not in TERRAFORM_GRAPH_TYPES:
                raise TerraformError(
                    f"The type:{type} is not available, please choose one of: {', '.join(TERRAFORM_GRAPH_TYPES)}",
                    "graph",
                )
            cmd.append(Terraform.__build_arg__("type", type))
        cmd.append(Terraform.__build_arg__("plan", plan))
        cmd.append(Terraform.__build_arg__("draw_cycles", draw_cycles))
        cmd.append(Terraform.__build_arg__("module_depth", module_depth))

        result = self.cmd(cmd, "Terraform graph", chdir)
        res = TerraformResult(True, result.stdout)
        if not result.success:
            log.failed(f"Terraform graph failed in {result.duration}s", end_sub=True)
            raise TerraformError(
                "Failed to run terraform graph",
                "graph",
                result.command,
                result.stderr,
                result.duration,
            )
        log.success(f"Terraform graph completed in {result.duration}s", end_sub=True)
        return res

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
        cmd = ["import"]
        cmd.extend(
            self.__default_args__(
                color=color, lock=lock, lock_timeout=lock_timeout, input=input
            )
        )

        cmd.append(Terraform.__build_arg__("config", config))
        cmd.append(Terraform.__build_arg__("paralellism", parallelism))
        cmd.append(Terraform.__build_arg__("provider", provider))
        cmd.append(Terraform.__build_arg__("var_file", var_file))
        cmd.append(Terraform.__build_arg__("state", state))
        cmd.append(Terraform.__build_arg__("state_out", state_out))
        cmd.append(Terraform.__build_arg__("backup", backup))
        cmd.extend(Terraform.__parse_vars__(vars))

        cmd.append(shlex.quote(address))
        cmd.append(shlex.quote(id))

        result = self.cmd(cmd, "Terraform import", chdir)
        res = TerraformResult(True, result.stdout)
        if not result.success:
            log.failed(f"Terraform import failed in {result.duration}s", end_sub=True)
            raise TerraformError(
                "Failed to run terraform import",
                "import",
                result.command,
                result.stderr,
                result.duration,
            )
        log.success(f"Terraform import completed in {result.duration}s", end_sub=True)
        return res

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
        cmd = ["refresh"]
        cmd.extend(
            self.__default_args__(
                color=color, lock=lock, lock_timeout=lock_timeout, input=input
            )
        )
        if not parallelism:
            cmd.append(Terraform.__build_arg__("parallelism", self.__paralellism__))
        else:
            cmd.append(Terraform.__build_arg__("parallelism", parallelism))
        cmd.append(Terraform.__build_arg__("target", target))
        cmd.append(Terraform.__build_arg__("compact_warnings", compact_warnings))

        cmd.append(Terraform.__build_arg__("state", state))
        cmd.append(Terraform.__build_arg__("state_out", state_out))
        cmd.append(Terraform.__build_arg__("backup", backup))
        cmd.append(Terraform.__build_arg__("var_file", var_file))
        cmd.extend(Terraform.__parse_vars__(vars))

        result = self.cmd(cmd, "Terraform refresh", chdir)
        res = TerraformResult(True, result.stdout)
        if not result.success:
            log.failed(f"Terraform refresh failed in {result.duration}s", end_sub=True)
            raise TerraformError(
                "Failed to run terraform refresh",
                "refresh",
                result.command,
                result.stderr,
                result.duration,
            )
        log.success(f"Terraform refresh completed in {result.duration}s", end_sub=True)
        return res

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
        if self.__version__["version"]["major"] == 0 or (
            self.__version__["version"]["major"] >= 1
            and self.__version__["version"]["minor"] < 1
        ):
            return self.__legacy_refresh__(
                target=target,
                vars=vars,
                var_file=var_file,
                compact_warnings=compact_warnings,
                input=input,
                lock=lock,
                lock_timeout=lock_timeout,
                color=color,
                parallelism=parallelism,
                state=state,
                state_out=state_out,
                backup=backup,
                chdir=chdir,
            )
        else:
            log.warn(
                f"Command 'terraform refresh' is deprecated since 1.1.0, using 'terraform apply -refresh-only -auto-approve' instead"
            )
            return self.apply(
                auto_approve=True,
                refresh_only=True,
                target=target,
                vars=vars,
                var_file=var_file,
                compact_warnings=compact_warnings,
                input=input,
                json=json,
                lock=lock,
                lock_timeout=lock_timeout,
                color=color,
                parallelism=parallelism,
                state=state,
                state_out=state_out,
                backup=backup,
                chdir=chdir,
            )

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
        cmd = ["taint"]
        if not lock:
            lock = self.__lock__
        if not lock_timeout:
            lock_timeout = self.__lock_timeout__

        if lock is False:
            cmd.append(Terraform.__build_arg__("lock", lock))
        if lock_timeout != "0s":
            cmd.append(Terraform.__build_arg__("lock_timeout", lock_timeout))

        cmd.append(
            Terraform.__build_arg__("ignore_remote_version", ignore_remote_version)
        )
        cmd.append(Terraform.__build_arg__("backup", backup))
        cmd.append(Terraform.__build_arg__("state", state))
        cmd.append(Terraform.__build_arg__("state_out", state_out))
        cmd.append(Terraform.__build_arg__("allow_missing", allow_missing))
        cmd.append(shlex.quote(address))

        result = self.cmd(cmd, "Terraform taint", chdir)
        res = TerraformResult(True, result.stdout)
        if not result.success:
            log.failed(f"Terraform taint failed in {result.duration}s", end_sub=True)
            raise TerraformError(
                "Failed to run terraform taint",
                "taint",
                result.command,
                result.stderr,
                result.duration,
            )
        log.success(f"Terraform taint completed in {result.duration}s", end_sub=True)
        return res

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
        if (
            self.__version__["version"]["major"] == 0
            and self.__version__["version"]["minor"] <= 15
        ):
            if (
                self.__version__["version"]["minor"] == 15
                and self.__version__["version"]["patch"] > 2
            ):
                log.warn(
                    f"Command 'terraform taint' is deprecated since 0.15.2, using 'terraform apply -replace=<address>' instead"
                )
                return self.apply(
                    replace=address,
                    lock=lock,
                    lock_timeout=lock_timeout,
                    chdir=chdir,
                    vars=vars,
                    var_file=var_file,
                    backup=backup,
                    state=state,
                    state_out=state_out,
                )
            else:
                return self.__legacy_taint__(
                    address,
                    lock=lock,
                    allow_missing=allow_missing,
                    lock_timeout=lock_timeout,
                    chdir=chdir,
                    backup=backup,
                    state=state,
                    state_out=state_out,
                    ignore_remote_version=ignore_remote_version,
                )
        else:
            log.warn(
                f"Command 'terraform taint' is deprecated since 0.15.2, using 'terraform apply -replace=<address>' instead"
            )
            return self.apply(
                replace=address,
                lock=lock,
                lock_timeout=lock_timeout,
                chdir=chdir,
                vars=vars,
                var_file=var_file,
                backup=backup,
                state=state,
                state_out=state_out,
            )

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
        cmd = ["untaint"]
        if not lock:
            lock = self.__lock__
        if not lock_timeout:
            lock_timeout = self.__lock_timeout__

        if lock is False:
            cmd.append(Terraform.__build_arg__("lock", lock))
        if lock_timeout != "0s":
            cmd.append(Terraform.__build_arg__("lock_timeout", lock_timeout))

        cmd.append(
            Terraform.__build_arg__("ignore_remote_version", ignore_remote_version)
        )
        cmd.append(Terraform.__build_arg__("backup", backup))
        cmd.append(Terraform.__build_arg__("state", state))
        cmd.append(Terraform.__build_arg__("state_out", state_out))
        cmd.append(Terraform.__build_arg__("allow_missing", allow_missing))
        cmd.append(shlex.quote(address))

        result = self.cmd(cmd, "Terraform untaint", chdir)
        res = TerraformResult(True, result.stdout)
        if not result.success:
            log.failed(f"Terraform untaint failed in {result.duration}s", end_sub=True)
            raise TerraformError(
                "Failed to run terraform untaint",
                "untaint",
                result.command,
                result.stderr,
                result.duration,
            )
        log.success(f"Terraform untaint completed in {result.duration}s", end_sub=True)
        return res

    def force_unlock(
        self, lock_id: str, force: Optional[bool] = False, chdir: Optional[str] = None
    ):
        cmd = ["force-ublock"]
        cmd.append(Terraform.__build_arg__("force", force))

        if not chdir:
            chdir = self.chdir
        cmd.append(shlex.quote(lock_id))

        result = self.cmd(cmd, "Terraform force-unlock", chdir=chdir)
        res = TerraformResult(True, result.stdout)
        if not result.success:
            log.failed(
                f"Terraform force-unlock failed in {result.duration}s", end_sub=True
            )
            raise TerraformError(
                "Failed to run terraform force-unlock",
                "force-unlock",
                result.command,
                result.stderr,
                result.duration,
            )
        log.success(
            f"Terraform force-unlock completed in {result.duration}s", end_sub=True
        )
        return res
