from utils import run_command, cmd_to_array, log
import os
import json as _json
import re
from time import time
import shlex

os.environ['TF_IN_AUTOMATION'] = '1'
# os.environ['TF_LOG'] = 'trace'

log.hide_file()
log.set_level("info")

VERSION_REGEX = re.compile(
    r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$")

TERRAFORM_ARGS = {
    "color": "-no-color",
    "lock": "-lock=",
    "lock_timeout": "-lock-timeout=",
    "input": "-input=",
    "upgrade": "-upgrade",
    "from_module": "-from-module=",
    "reconfigure": "-reconfigure",
    "migrate_state": "-migrate-state", "force_copy": "-force-copy",
    "backend": "-backend=",
    "backend_config": "-backend-config=",
    "get": "-get=",
    "get_plugins": "-get-plugins=",
    "plugin_dir": "-plugin-dir=",
    "lockfile": "-lockfile=",
    "readonly": "-lockfile=readonly",
    "chdir": "-chdir=",
    "update": "-update",
    "destroy": "-destroy",
    "out": "-out=",
    "refresh_only": "-refresh-only",
    "refresh": "-refresh=",
    "replace": "-replace=",
    "target": "-target=",
    "var": "-var=",
    "var_file": "-var-file=",
    "compact_warnings": "-compact-warnings",
    "json": "-json",
    "parallelism": "-parallelism=",
    "auto_approve": "-auto-approve",
    "state": "-state=",
    "state_out": "-state-out=",
    "backup": "-backup="
}


class Terraform:
    def __init__(self, workspace: str = "default", chdir: str = None, lock=True, lock_timeout=0, input=False, parallelism=10, color=True, var_file: str = None):
        log.set_env(workspace)
        self._workspace = workspace
        self._workdir = chdir
        self._lock = lock
        self._lock_timeout = lock_timeout
        self._input = input
        self._paralellism = parallelism
        self._color = color
        self._var_file = var_file
        self._version = self.version()
        self._planfile = "plan.tfplan"

    def version(self):
        result = run_command(cmd_to_array(
            "terraform version -json"), show_output=False)
        if not result.success:
            log.error("Error retrieving terraform version", result.stderr)
            return result.stderr
        version = _json.loads(result.stdout)
        version_str = version["terraform_version"]

        version_dict = VERSION_REGEX.match(version_str)
        if version_dict:
            version_dict = version_dict.groupdict()
            for key in version_dict.keys():
                version_dict[key] = int(version_dict[key])
        else:
            version_dict = dict(major=0, minor=0, patch=0)
        result = {"version": version_dict, "version_str": version_str,
                  "latest":  version["terraform_outdated"] == False, "platform": version["platform"]}
        self._version = result
        return result

    def color(self, enable: bool = True):
        self._color = enable

    def lock(self, enable: bool = True):
        self._lock = enable

    def input(self, enable: bool = False):
        self._input = enable

    def lock_timeout(self, timeout: int = 0):
        self._lock_timeout = timeout

    @staticmethod
    def _build_arg(arg: str, value) -> str:
        res = TERRAFORM_ARGS[arg]
        if res[-1] == "=" and value is not None:
            if isinstance(value, bool):
                res += "true" if value else "false"
            elif isinstance(value, str) and len(value) == 0:
                return ""
            elif value is not None and len(str(value)) > 0:
                res += str(value)

        elif isinstance(value, bool):
            return res if value else ""
        else:
            return ""
        return res

    def _default_args(self,  color: bool = None, lock: bool = None, lock_timeout: int = None, input: bool = None) -> list:
        args = []

        if color is not None:
            args.append(Terraform._build_arg("color", color))
        elif self._color is False:
            args.append(TERRAFORM_ARGS["color"])
        if lock is not None and lock is False:
            args.append(Terraform._build_arg("lock", lock))
        elif self.lock is False:
            args.append(Terraform._build_arg("lock", self._lock))

        if lock_timeout is not None and lock_timeout > 0:
            args.append(Terraform._build_arg("lock_timeout", lock_timeout))
        elif self._lock_timeout > 0:
            args.append(Terraform._build_arg(
                "lock_timeout", self._lock_timeout))

        if input is not None:
            args.append(Terraform._build_arg("input", input))
        elif self._input is False:
            args.append(Terraform._build_arg("input", self._input))
        return args

    def _global_args(self, chdir: str = None):
        args = []

        if chdir is not None:
            args.append(Terraform._build_arg("chdir", chdir))
        elif self._workdir is not None and self._workdir != ".":
            args.append(Terraform._build_arg("chdir", self._workdir))
        return args

    def cmd(self, command: list, title: str = None,
            chdir: str = None, show_output: bool = True,
            callback=None, line_callback=None):
        cmd = ["terraform"]
        cmd.extend(command)
        if not chdir:
            chdir = self._workdir
        return run_command(
            cmd, title=title, cwd=chdir, show_output=show_output, callback=callback, line_callback=line_callback)

    def init(self, color: bool = None, lock: bool = None,
             lock_timeout: int = None, input: bool = None,
             upgrade: bool = False, reconfigure: bool = False,
             migrate_state: bool = False, force_copy: bool = False,
             backend: bool = True, backend_config: str = None,
             get: bool = True, get_plugins: bool = True,
             plugin_dir: str = None,
             readonly: bool = False, chdir: str = None):
        start = time()
        cmd = ["init"]

        if readonly:
            cmd.append(Terraform._build_arg("readonly", readonly))

        cmd.extend(self._default_args(
            color=color, lock=lock, lock_timeout=lock_timeout, input=input))

        cmd.append(Terraform._build_arg("upgrade", upgrade))
        cmd.append(Terraform._build_arg("reconfigure", reconfigure))
        cmd.append(Terraform._build_arg("migrate_state", migrate_state))
        cmd.append(Terraform._build_arg("force_copy", force_copy))
        cmd.append(Terraform._build_arg("backend_config", backend_config))
        cmd.append(Terraform._build_arg("plugin_dir", plugin_dir))
        # cmd.append(Terraform._build_arg("lockfile", lockfile))

        if not backend:
            cmd.append(Terraform._build_arg("backend", backend))
        if not get:
            cmd.append(Terraform._build_arg("get", get))
        if not get_plugins:
            cmd.append(Terraform._build_arg("get_plugins", get_plugins))
        result = self.cmd(
            cmd, title="Terraform init", chdir=chdir)
        if result.success:
            log.success(
                f"Terraform init completed in: {round(time()-start,4)} seconds")
        else:
            log.critical(
                f"Failed to initialize terraform in: {round(time()-start,4)} seconds")
        return result.success

    def get(self, update: bool = None, color: bool = None):
        start = time()
        cmd = ["get"]
        cmd.append(Terraform._build_arg("update", update))
        cmd.append(Terraform._build_arg("color", color))
        # cmd.append(path)
        result = self.cmd(cmd, title="Terraform get")
        if result.success:
            log.success(
                f"Terraform get completed in: {round(time()-start,4)} seconds")
        else:
            log.critical(
                f"Failed to get terraform modules in: {round(time()-start,4)} seconds")
        return result.success

    @staticmethod
    def _parse_vars(vars: dict):
        if not vars:
            return []
        args = []
        for key in vars.keys():
            value = vars[key]
            if isinstance(value, str):
                value = re.sub(r'\"', '\\"', value)
                value = f'"{value}"'
            elif isinstance(value, str) or isinstance(value, dict) or isinstance(value, list) or isinstance(value, tuple):
                value = _json.dumps(value)
            args.append("-var")
            args.append(f"{key}={value}")
        return args

    def plan(self, out: str = None, destroy: bool = False,
             refresh_only: bool = False, refresh: str = None,
             replace: str = None, target: str = None,
             vars: dict = None, var_file: str = None,
             compact_warnings: bool = False,
             input: bool = None, json: bool = False,
             lock: bool = None, lock_timeout: str = None,
             color: bool = None, parallelism: int = None, chdir: str = None):
        start = time()
        cmd = ["plan"]
        cmd.extend(self._default_args(
            color=color, lock=lock, lock_timeout=lock_timeout, input=input))
        if not out:
            cmd.append(Terraform._build_arg("out", self._planfile))
        else:
            cmd.append(Terraform._build_arg("out", out))

        if self._version["version"]["major"] >= 1 and self._version["version"]["minor"] >= 0:
            cmd.append(Terraform._build_arg("refresh_only", refresh_only))
        else:
            log.warn(
                f"the option '-refresh-only' is supported since the version 1.1.0, and your version is {self._version['version_str']}")
        if self._version["version"]["major"] >= 1 and self._version["version"]["minor"] >= 0:
            cmd.append(Terraform._build_arg("json", json))
        else:
            log.warn(
                f"the option '-json' is supported since the version 1.0.0, and your version is {self._version['version_str']}")
        if not parallelism:
            cmd.append(Terraform._build_arg("parallelism", self._paralellism))
        else:
            cmd.append(Terraform._build_arg("parallelism", parallelism))

        cmd.append(Terraform._build_arg("destroy", destroy))
        cmd.append(Terraform._build_arg("refresh", refresh))
        cmd.append(Terraform._build_arg("replace", replace))
        cmd.append(Terraform._build_arg("target", target))
        cmd.append(Terraform._build_arg("var_file", var_file))
        cmd.append(Terraform._build_arg("compact_warnings", compact_warnings))

        cmd.extend(Terraform._parse_vars(vars))

        result = self.cmd(cmd, title="Terraform plan", chdir=chdir)
        if result.success:
            log.success(
                f"Terraform plan completed in: {round(time()-start,4)} seconds")
        else:
            log.critical(
                f"Failed to plan terraform in: {round(time()-start,4)} seconds")
        return result.success

    @staticmethod
    def _apply_line_callback(stdout: str = None, stderr: str = None):
        if stdout:
            stdout = _json.loads(stdout)
            log.info(stdout["@message"])

    @staticmethod
    def _apply_callback(stdout: str = None, stderr: str = None):
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

    def apply(self, plan_file: str = None, auto_approve: bool = False,
              compact_warnings: bool = False, input: bool = None,
              json: bool = False, lock: bool = None,
              lock_timeout: str = None, color: bool = None,
              parallelism: int = None, state: str = None,
              state_out: str = None, backup: str = None, chdir: str = None):
        start = time()
        cmd = ["apply"]
        cmd.extend(self._default_args(color=color, lock=lock,
                   lock_timeout=lock_timeout, input=input))
        if not parallelism:
            cmd.append(Terraform._build_arg("parallelism", self._paralellism))
        else:
            cmd.append(Terraform._build_arg("parallelism", parallelism))
        cmd.append(Terraform._build_arg("auto_approve", auto_approve))
        cmd.append(Terraform._build_arg("compact_warnings", compact_warnings))
        cmd.append(Terraform._build_arg("json", json))
        cmd.append(Terraform._build_arg("state", state))
        cmd.append(Terraform._build_arg("state_out", state_out))
        cmd.append(Terraform._build_arg("backup", backup))
        if not plan_file:
            cmd.append(shlex.quote(self._planfile))
        else:
            cmd.append(shlex.quote(plan_file))
        callback = None
        line_callback = None
        if json:
            line_callback = Terraform._apply_line_callback
            callback = Terraform._apply_callback
        result = self.cmd(
            cmd, title="Terraform apply", chdir=chdir, line_callback=line_callback, callback=callback, show_output=False)
        if result.success:
            log.success(
                f"Terraform apply completed in: {round(time()-start,4)} seconds")
        else:
            log.critical(
                f"Failed to apply terraform state in: {round(time()-start,4)} seconds")
            return False
        return result.callback_output[0]

    # def destroy(self, target: str = None, vars: dict = None, chdir: str = None):
    #     start = time()
    #     cmd = ["destroy"]
    #     cmd.append(Terraform._build_arg("target", target))
    #     cmd.extend(Terraform._parse_vars(vars))
    #     print(shlex.join(cmd))
    #     result = self.cmd(cmd, title="Terraform destroy", chdir=chdir)
    #     if result.success:
    #         log.success(
    #             f"Terraform destroy completed in: {round(time()-start,4)} seconds")
    #     else:
    #         log.critical(
    #             f"Failed to destroy terraform resources in: {round(time()-start,4)} seconds")
    #     return result.success

    def show(self, file: str = None, json=True, color: bool = None, chdir: str = None):
        start = time()
        cmd = ["show"]
        log.info("Running Terraform show")
        cmd.append(Terraform._build_arg("json", json))

        if color is not None:
            cmd.append(Terraform._build_arg("color", color))
        else:
            cmd.append(Terraform._build_arg("color", self._color))

        if not file:
            cmd.append(shlex.quote(self._planfile))
        else:
            cmd.append(shlex.quote(file))
        result = self.cmd(cmd, chdir=chdir, show_output=False)
        if result.success:
            log.success(
                f"Terraform show completed in: {round(time()-start,4)} seconds")
        else:
            log.critical(
                f"Failed to show terraform state in: {round(time()-start,4)} seconds")
        if json:
            return _json.loads(result.stdout)
        return result.stdout

    def login(self, hostname: str = None, chdir: str = None):
        start = time()
        cmd = ["login", shlex.quote(hostname)]
        result = self.cmd(cmd, title="Terraform login", chdir=chdir)
        if result.success:
            log.success(
                f"Terraform login completed in: {round(time()-start,4)} seconds")
        else:
            log.critical(
                f"Failed to login terraform in: {round(time()-start,4)} seconds")
        return result.success

    def logout(self, hostname: str = None, chdir: str = None):
        start = time()
        cmd = ["logout", shlex.quote(hostname)]
        result = self.cmd(cmd, title="Terraform logout", chdir=chdir)
        if result.success:
            log.success(
                f"Terraform logout completed in: {round(time()-start,4)} seconds")
        else:
            log.critical(
                f"Failed to logout terraform in: {round(time()-start,4)} seconds")
        return result.success


tf = Terraform(chdir="./tests/terraform")
vars = {"bucket_name": "test_bucket",
        "test_variable": {"test1": 1, "test2": None}}
log.info(tf.version())
log.info(tf.init(upgrade=False, lock=True, ))
log.info(tf.get())
log.info(tf.plan(vars=vars, destroy=False))
log.info(tf.show(json=True))
log.info(tf.apply(json=True))
# log.info(tf.destroy(vars=vars))
