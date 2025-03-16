from typing import Any, Callable, Dict, List, Optional
from .base import *
from .exceptions import *
from ..utils import log
import shlex

class Workspace:
    __tf__: Terraform
    __cmd__: str
    def __init__(self, terraform_object: Terraform):
        self.current = "default"
        self.__cmd__="workspace"
        self.__tf__=terraform_object    

    def list(
        self,
        quiet: Optional[bool] = None,
        color: Optional[bool] = None,
        chdir: Optional[str] = None,
    ):
        cmd = [self.__cmd__, "list"]
        if not color:
            color = self.__tf__.__color__
        cmd.append(self.__tf__.__build_arg__("color", not color))

        result = self.__tf__.cmd(
            cmd, "Terraform workspace list", chdir=chdir, show_output=not quiet
        )

        res = TerraformResult(result.success, "")
        if not result.success:
            if not quiet:
                log.failed(
                    f"Terraform workspace list failed in {result.duration}s",
                    end_sub=True,
                )
            raise TerraformError(
                "Failed to execute terraform workspace list",
                "workspace list",
                result.command,
                result.stderr,
                result.duration,
            )
        if not quiet:
            log.success(
                f"Terraform workspace list succeded in {result.duration}s", end_sub=True
            )
        self.current = (
            list(
                filter(
                    lambda x: len(x.strip()) > 0 and "*" in x,
                    result.stdout.splitlines(),
                )
            )[0]
            .replace("*", "")
            .strip()
        )
        log.set_env(self.current)

        res.result = [
            line.replace("*", "").strip() for line in result.stdout.splitlines()
        ]
        res.result = list(filter(lambda x: len(x) > 0, res.result))
        return res

    def select(
        self,
        workspace: str,
        or_create: Optional[bool] = False,
        color: Optional[bool] = None,
        chdir: Optional[str] = None,
        quiet:Optional[bool]=False
    ):
        cmd = [self.__cmd__, "select"]

        if not color:
            color = self.__tf__.__color__
        cmd.append(self.__tf__.__build_arg__("color", not color))
        if or_create is True:
            if (
                self.__tf__.__version__["version"]["major"] >= 1
                and self.__tf__.__version__["version"]["minor"] >= 4
            ):
                cmd.append(self.__tf__.__build_arg__("or_create", or_create))
            else:
                existing = self.list(True, color=color, chdir=chdir).result
                if workspace not in existing:
                    if not quiet:
                        log.warn(
                        "The arg -or-create is available since version 1.4.x, and your version is",
                        self.__tf__.__version__["version_str"],
                        "Using alternate method",
                    )
                    return self.new(workspace, color=color, chdir=chdir)
        cmd.append(shlex.quote(workspace))

        result = self.__tf__.cmd(cmd, "Terraform workspace select", chdir=chdir, show_output=not quiet)

        if not result.success:
            if not quiet:
                log.failed(
                f"Terraform workspace select failed in {result.duration}s", end_sub=True
            )
            raise TerraformError(
                "Failed to execute terraform workspace list",
                "workspace select",
                result.command,
                result.stderr,
                result.duration,
            )
        if not quiet:
            log.success(
            f"Terraform workspace select succeded in {result.duration}s", end_sub=True
        )
        self.__tf__.__workspace__ = workspace
        self.current = workspace
        log.set_env(workspace)
        return TerraformResult(result.success, workspace)

    def new(
        self,
        workspace: str,
        lock: Optional[bool] = None,
        lock_timeout: Optional[str] = None,
        state: Optional[str] = None,
        color: Optional[bool] = None,
        chdir: Optional[str] = None,
    ):
        cmd = [self.__cmd__, "new"]
        if not lock:
            lock = self.__tf__.__lock__
        if not color:
            color = self.__tf__.__color__
        if not lock_timeout:
            lock_timeout = self.__tf__.__lock_timeout__

        cmd.append(self.__tf__.__build_arg__("lock", lock))
        cmd.append(self.__tf__.__build_arg__("color", not color))
        cmd.append(self.__tf__.__build_arg__("lock_timeout", lock_timeout))
        cmd.append(self.__tf__.__build_arg__("state", state))

        cmd.append(shlex.quote(workspace))

        result = self.__tf__.cmd(cmd, "Terraform workspace new", chdir=chdir)

        if not result.success:
            log.failed(
                f"Terraform workspace new failed in {result.duration}s", end_sub=True
            )
            raise TerraformError(
                "Failed to execute terraform workspace new",
                "workspace new",
                result.command,
                result.stderr,
                result.duration,
            )
        log.success(
            f"Terraform workspace new succeded in {result.duration}s", end_sub=True
        )
        self.__tf__.__workspace__ = workspace
        self.current = workspace
        log.set_env(workspace)
        return TerraformResult(result.success, workspace)