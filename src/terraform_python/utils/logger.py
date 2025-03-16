import traceback
import atexit
import datetime
import inspect
import json
import logging
import logging.handlers
import shutil
import sys
import os
from queue import Queue
from threading import Event, Thread
from time import time

# ANSI escape codes for colors and styles (cross-platform)
from .colors import color

__LOGGERS__ = []

# Logger handle exception outputs
HANDLE_EXCEPTIONS = True

HORIZONTAL_SEPARATOR = "─"


def __catcher__(type, value, tback):
    global HANDLE_EXCEPTIONS
    if HANDLE_EXCEPTIONS:
        for logger in __LOGGERS__:
            for line in traceback.format_tb(tback):
                for ln in line.splitlines():
                    logger.exception(ln, _raise=False)
            for line in str(value).splitlines():
                logger.exception(line, _raise=False)
            for task in logger.__tasks__:
                logger.finish(task["id"], success=False)
    else:
        sys.__excepthook__(type, value, tback)


sys.excepthook = __catcher__

LOGGER_LEVEL_COLORS = {
    "TRACE": color.bold(color.cyan("TRACE")),
    "RUNNING": color.bold(color.purple("RUNNI")),
    "DEBUG": color.bold(color.cyan("DEBUG")),
    "INFO": color.bold(color.white("INFO ")),
    "DONE": color.bold(color.green("DONE ")),
    "SUCCESS": color.bold(color.italic(color.green("SUCES"))),
    "COMPLETED": color.bold(color.bg_green("COMPL")),
    "WARNING": color.bold(color.orange("WARN ")),
    "ERROR": color.bold(color.red("ERROR")),
    "FAILED": color.bold(color.italic(color.red("FAIL "))),
    "CRITICAL": color.bold(color.bg_light_red("CRITI")),
    "EXCEPTION": color.bold(color.bg_red("EXCEP")),
}

# Map custom levels to standard logging levels (and define custom levels)
LOGGER_LEVELS = {
    "TRACE": logging.DEBUG - 1,  # Below DEBUG
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "DONE": logging.INFO + 1,
    "RUNNING": logging.INFO + 2,
    "FAILED": logging.ERROR + 1,
    "COMPLETED": logging.INFO + 3,
    "SUCCESS": logging.INFO + 4,  # Above INFO
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
    "SEP": logging.CRITICAL + 1,  # Above CRITICAL
    "EXCEPTION": logging.CRITICAL + 2,  # Above CRITICAL
}

# Define custom logging levels
logging.addLevelName(LOGGER_LEVELS["TRACE"], "TRACE")
logging.addLevelName(LOGGER_LEVELS["SUCCESS"], "SUCCESS")
logging.addLevelName(LOGGER_LEVELS["EXCEPTION"], "EXCEPTION")
logging.addLevelName(LOGGER_LEVELS["RUNNING"], "RUNNING")
logging.addLevelName(LOGGER_LEVELS["FAILED"], "FAILED")
logging.addLevelName(LOGGER_LEVELS["COMPLETED"], "COMPLETED")
logging.addLevelName(LOGGER_LEVELS["DONE"], "DONE")
logging.addLevelName(LOGGER_LEVELS["SEP"], "SEP")


def format_elapsed_time(start_time: float, end_time: float) -> str:
    """Function to format elapsed time in <h>h, <m>m, <s>s, <ms>ms

    Args:
        start_time (float): Start time in epoch format
        end_time (float): Finish time in epoch format

    Returns:
        str: Formatted elapsed time
    """
    elapsed_time = end_time - start_time
    result = ""
    hours = int(elapsed_time // 3600)
    if hours > 0:
        result += f"{hours}h, "
    elapsed_time %= 3600
    minutes = int(elapsed_time // 60)
    if minutes > 0:
        result += f"{minutes}min, "
    elapsed_time %= 60
    seconds = int(elapsed_time)
    if seconds > 0:
        result += f"{seconds}s, "
    milliseconds = int((elapsed_time - int(elapsed_time)) * 1000)
    if milliseconds > 0:
        result += f"{milliseconds}ms"
    return result.rstrip(", ")  # Remove trailing comma and space


class LoggerFormatter:
    pass


class LoggerFormatter(logging.Formatter):
    """
    Custom logging formatter that supports colored output and configurable display options.

    This formatter extends the standard logging.Formatter with additional features:
    - Configurable color output for different message components
    - Selective display of timestamp, log level, file information, and environment
    - Support for message continuation (erasing previous line)

    Attributes:
        _show_level (bool): Whether to show the log level in the output
        _show_date (bool): Whether to show the timestamp in the output
        _show_file (bool): Whether to show the file name and line number
        _show_env (bool): Whether to show the environment/logger name
        colors (bool): Whether to use colored output
    """

    def __init__(
        self,
        fmt: str = None,
        datefmt: str = None,
        style="%",
        validate=True,
        colors=True,
        old: LoggerFormatter = None,
        **args,
    ):
        """
        Initialize the LoggerFormatter.

        Args:
            fmt: Log message format string. If None, custom formatting is applied.
            datefmt: Date format string for timestamps. If None, ISO format is used.
            style: Style of the fmt string ('%', '{', or '$').
            validate: Whether to validate the format string.
            colors: Whether to use colored output in log messages.
            **kwargs: Additional configuration options:
                - level (bool): Whether to show the log level
                - date (bool): Whether to show the timestamp
                - file (bool): Whether to show file name and line number
                - env (bool): Whether to show the environment/logger name
        """
        super().__init__(fmt, datefmt, style, validate)
        self._show_level = args.get("level", True)
        self._show_date = args.get("date", True)
        self._show_file = args.get("file", True)
        self._show_env = args.get("env", True)
        self.colors = colors
        self.fmt = fmt
        self.__proc_level__ = 0
        if old:
            self.__proc_level__ = old.__proc_level__
        self.__start_proc_prefix__ = "\u256d○ "
        self.__end_proc_prefix__ = "\u2570● "
        self.__subproc_prefix__ = "│ "

    def __process_line_fmt__(self, line: str, bold: bool, success: bool, fail: bool):
        if bold:
            line = color.bold(line)
        if success:
            line = color.green(line)
        elif fail:
            line = color.red(line)
        return line

    def format(self, record):
        """
        Format the specified record as text.

        Args:
            record: The log record to format

        Returns:
            str: The formatted log message

        Raises:
            KeyError: If required keys are missing from record.args
        """
        if self.fmt:
            return super().format(record)
        msg = record.msg

        if record.levelname == "SEP":
            return msg if self.colors else msg.replace("─", "-")
        prefix = []
        # Safely access record arguments with defaults
        args = getattr(record, "args", {})
        if not isinstance(args, dict):
            args = {}

        env = args.get("env", "default")
        raw = args.get("raw", False)
        if raw:
            return msg

        timestamp = args.get(
            "timestamp", datetime.datetime.now().isoformat(timespec="milliseconds")
        )

        # Handle line continuation
        delete_last = ""
        if not args.get("last_log", True) and args.get("started", False):
            delete_last = "\033[A\033[K"  # Move up one line and clear it

        lines = []
        if self.colors:
            proc_prefix = self.__subproc_prefix__ * self.__proc_level__
            end_proc = args.get("end_proc", False)
            start_proc = args.get("start_proc", False)
            bold = args.get("bold", False)
            success = record.levelname == "SUCCESS"
            fail = record.levelname == "FAILED"

            if end_proc and self.__proc_level__ <= 0:
                end_proc = False
            if start_proc:
                self.__proc_level__ += 1
            elif end_proc:
                self.__proc_level__ -= 1
            self.__proc_level__ = max(self.__proc_level__, 0)

            if "\n" in msg:
                lines = []
                messages = msg.splitlines()
                if start_proc:
                    first_line = (
                        proc_prefix
                        + self.__start_proc_prefix__ * 2
                        + self.__process_line_fmt__(messages[0], bold, success, fail)
                    )
                    self.__proc_level__ += 1
                    proc_prefix = self.__subproc_prefix__ * self.__proc_level__
                elif end_proc:
                    proc_prefix = self.__subproc_prefix__ * self.__proc_level__
                    first_line = (
                        proc_prefix
                        + self.__start_proc_prefix__
                        + self.__process_line_fmt__(messages[0], bold, success, fail)
                    )
                    lines.append(proc_prefix + self.__end_proc_prefix__)

                else:
                    first_line = (
                        proc_prefix
                        + self.__start_proc_prefix__
                        + self.__process_line_fmt__(messages[0], bold, success, fail)
                    )
                    self.__proc_level__ += 1
                    proc_prefix = self.__subproc_prefix__ * self.__proc_level__

                lines.append(first_line)
                lines.extend(
                    [
                        proc_prefix
                        + self.__process_line_fmt__(line, bold, success, fail)
                        for line in messages[1:-2]
                    ]
                )

                self.__proc_level__ -= 1
                proc_prefix = self.__subproc_prefix__ * self.__proc_level__

                last_line = (
                    proc_prefix
                    + self.__end_proc_prefix__
                    + self.__process_line_fmt__(messages[-1], bold, success, fail)
                )
                if end_proc:
                    last_line = (
                        proc_prefix
                        + self.__end_proc_prefix__
                        + self.__process_line_fmt__(messages[-1], bold, success, fail)
                    )
                lines.append(last_line)
            elif record.levelname == "RUNNING":
                lines.append(">> " + msg)
            else:
                if start_proc:
                    message = (
                        proc_prefix
                        + self.__start_proc_prefix__
                        + self.__process_line_fmt__(msg, bold, success, fail)
                    )

                elif end_proc:
                    proc_prefix = self.__subproc_prefix__ * self.__proc_level__
                    message = (
                        proc_prefix
                        + self.__end_proc_prefix__
                        + self.__process_line_fmt__(msg, bold, success, fail)
                    )

                else:
                    proc_prefix = self.__subproc_prefix__ * self.__proc_level__
                    message = proc_prefix + self.__process_line_fmt__(
                        msg, bold, success, fail
                    )

                lines.append(message)

            if self._show_date:
                prefix.append(color.dark_blue(timestamp))
            if self._show_env:
                prefix.append(color.purple(f"({env})"))
            if self._show_level:
                prefix.append(
                    f"{LOGGER_LEVEL_COLORS.get(record.levelname, color.bold(record.levelname))}"
                )
            if self._show_file:
                prefix.append(
                    f"{color.dark_green(record.filename)}{color.orange(':')}{color.dark_green(str(record.lineno))}"
                )

            message = (
                delete_last
                + " ".join(prefix)
                + f" {lines[0]}"
                + ("\n" if len(lines) > 1 else "")
            )
            message += "\n".join(
                [(" ".join(prefix) + f" {line}").strip() for line in lines[1:]]
            )
            return message
        else:
            if self._show_date:
                prefix.append(f"{timestamp}")
            if self._show_env:
                prefix.append(f"({env})")
            if self._show_level:
                prefix.append(f"{record.levelname:9s}")
            if self._show_file:
                prefix.append(f"{record.filename}:{record.lineno}")
            return " ".join(prefix) + f" | {msg}"


class Logger:
    """Logger helper to pretty format and follow processes in the background."""

    def __init__(
        self, env: str, log_file=None, max_log_size_mb=10, backup_count=5, colors=True
    ):
        """
        Initializes the logger.

        Args:
            env (str): Environment name (e.g., 'dev', 'prod').
            log_file (str, optional): Path to the log file.  If None, file logging is disabled.
            max_log_size_mb (int, optional): Maximum log file size in MB (only used if log_file is provided).
            backup_count (int, optional): Number of backup log files to keep (only used if log_file is provided).
        """
        self.env = env
        self.__tasks__ = []
        self.__total_tasks__ = 0
        self.__end_tasks__ = []
        self.__log_queue__ = Queue()
        self.__animation__ = ["⠙", "⠘", "⠰", "⠴", "⠤", "⠦", "⠆", "⠃", "⠋", "⠉"]
        self.v_separator = " "
        self.__enable_colors__ = colors
        self.__log_file__ = log_file
        self.__max_log_size__ = max_log_size_mb
        self.__backup_count__ = backup_count
        # Configuration flags
        self.flags = {"file": True, "date": True, "env": True, "level": True}

        # --- Standard Library Logging Setup ---
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)  # Set the *root* logger to DEBUG

        # Create a handler that outputs to the console (StreamHandler)
        self.console_handler = None
        self.file_handler = None  # Initialize to None
        # Create a formatter
        self.file_formatter: LoggerFormatter = None
        self.formatter: LoggerFormatter = None
        self.__custom_formatters__()

        # --- Threading for background tasks and logging ---
        self.__log_thread__: Thread = None
        self.__stop_event__ = Event()  # Use an Event for cleaner thread stopping

        self.__start_log_thread__()
        __LOGGERS__.append(self)

    def __custom_formatters__(self):
        """Formats log messages with colors and additional info."""
        self.file_formatter = LoggerFormatter(
            colors=False, **self.flags, old=self.file_formatter
        )
        self.formatter = LoggerFormatter(colors=True, **self.flags, old=self.formatter)

        if self.console_handler is not None:
            self.logger.removeHandler(self.console_handler)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.formatter)  # Use custom formatter
        console_handler.setLevel(logging.INFO)  # Default console level
        self.console_handler = console_handler
        self.logger.addHandler(self.console_handler)

        if self.__log_file__:
            if self.file_handler is not None:
                self.logger.removeHandler(self.file_handler)
            file_handler = logging.handlers.RotatingFileHandler(
                self.__log_file__,
                maxBytes=self.__max_log_size__ * 1024 * 1024,  # Convert MB to bytes
                backupCount=self.__backup_count__,
                encoding="utf-8",
                delay=True,
            )
            file_handler.setFormatter(self.file_formatter)
            file_handler.setLevel(logging.DEBUG)  # Log everything to file
            self.file_handler = file_handler
            self.logger.addHandler(file_handler)

    def __process_log_queue__(self):
        """Processes the log queue in a separate thread."""
        animation_index = 0
        last_message_log = True
        started = False
        cycle_start = time()
        delta = 0.2
        while not self.__stop_event__.is_set() or not self.__log_queue__.empty():
            cycle_period = time()
            try:
                # Get a task from the queue.  Use a timeout to allow checking _stop_event.
                num_tasks = len(self.__tasks__)  # +1 for the current task
                if num_tasks > 0 and (cycle_period - cycle_start) >= delta:
                    cycle_start = time()
                    task = self.__tasks__[0]
                    message, start_time, now, frame, level_value = (
                        task["message"],
                        task["start_time"],
                        task["now"],
                        task["frame"],
                        task["level"],
                    )
                    log_message = f"{message} ({num_tasks} bg tasks) {self.__animation__[animation_index]} ({format_elapsed_time(start_time, time())})"

                    self.log("RUNNING", log_message, frame=task["frame"])
                    # sleep(0.1)
                    # self.remove_line()
                    animation_index = (animation_index + 1) % len(self.__animation__)

                if len(self.__end_tasks__) > 0:
                    for task in self.__end_tasks__.copy():
                        self.__end_tasks__.remove(task)
                        if task["success"]:
                            log_level = "COMPLETED"
                            log_msg = f"{task['message']} ✅ ({format_elapsed_time(task['start_time'], time())}){task['postfix']}"
                        else:
                            log_level = "FAILED"
                            log_msg = f"{task['message']} ❌ ({format_elapsed_time(task['start_time'], time())}){task['postfix']}"

                        self.log(log_level, log_msg, frame=task["frame"])

                if not self.__log_queue__.empty():
                    log_event = self.__log_queue__.get(timeout=0.1)
                    filename = (
                        "/".join(
                            log_event["frame"].f_code.co_filename.split(os.sep)[-2:]
                        )
                        if log_event["frame"]
                        else "unknown"
                    )
                    line = log_event["frame"].f_lineno if log_event["frame"] else 0

                    # Use standard library logging, but format as before.
                    log_record = self.logger.makeRecord(
                        self.env,
                        log_event["level"],
                        filename,
                        line,
                        log_event["log"],
                        (
                            {
                                "timestamp": log_event["timestamp"],
                                "last_log": last_message_log,
                                "started": started,
                                "env": self.env,
                                "bold": log_event["bold"],
                                "start_proc": log_event["start_proc"],
                                "end_proc": log_event["end_proc"],
                                "raw": log_event["raw"],
                            },
                        ),
                        None,
                    )
                    self.logger.handle(log_record)
                    if LOGGER_LEVELS["RUNNING"] == log_event["level"]:
                        last_message_log = False
                    else:
                        last_message_log = True
                    if not started:
                        started = True
                    if log_event["raise"]:
                        raise Exception(message)

            except Exception as e:
                print(e)
                raise e

    def __start_log_thread__(self):
        """Starts the log processing thread."""
        if self.__log_thread__ is None or not self.__log_thread__.is_alive():
            self.__stop_event__.clear()  # Make sure it's clear
            self.__log_thread__ = Thread(target=self.__process_log_queue__, daemon=True)
            self.__log_thread__.start()

    def __get_message__(self, *messages) -> str:
        res = []
        for msg in messages:
            if isinstance(msg, (dict, list)):  # Use isinstance for type checking
                res.append(json.dumps(msg))
            else:
                res.append(str(msg))
        return self.v_separator.join(res)

    def set_env(self, env: str):
        self.env = env
        self.__custom_formatters__()

    def set_level(self, level: str):
        """Set the logging level for the console handler."""
        level = level.upper()
        if level not in LOGGER_LEVELS:
            raise ValueError(f"Invalid log level: {level}")
        self.console_handler.setLevel(LOGGER_LEVELS[level])
        self.__custom_formatters__()

    def show_file(self, show=True):
        self.flags["file"] = show
        self.__custom_formatters__()

    def show_date(self, show=True):
        self.flags["date"] = show
        self.__custom_formatters__()

    def show_env(self, show=True):
        self.flags["env"] = show
        self.__custom_formatters__()

    def show_level(self, show=True):
        self.flags["level"] = show
        self.__custom_formatters__()

    def log(
        self,
        level: str,
        *messages,
        frame=None,
        _raise=False,
        start_sub=False,
        end_sub=False,
        raw=False,
        bold=False,
    ):
        """Logs a message at the specified level.

        Adds the log entry to the queue for processing in a separate thread.
        """
        now = datetime.datetime.now().isoformat(timespec="milliseconds")

        level_value = LOGGER_LEVELS.get(level.upper())
        if level_value is None:
            raise ValueError(f"Invalid log level: {level}")

        if not frame:
            frame = inspect.currentframe().f_back.f_back

        message = self.__get_message__(*messages)

        body = {
            "level_name": level.upper(),
            "level": level_value,
            "log": message,
            "frame": frame,
            "timestamp": now,
            "raise": _raise,
            "bold": start_sub or bold or end_sub,
            "start_proc": start_sub,
            "end_proc": end_sub,
            "raw": raw,
        }
        return self.__log_queue__.put_nowait(body)

    def sep(self):
        global HORIZONTAL_SEPARATOR
        """Prints a horizontal separator."""
        width = shutil.get_terminal_size((80, 20))[0]
        frame = inspect.currentframe().f_back
        # Use logger to go through the queue
        self.log("SEP", HORIZONTAL_SEPARATOR * width, frame=frame)

    def trace(self, *messages, start_sub=False, end_sub=False, raw=False):
        frame = inspect.currentframe().f_back
        self.log(
            "TRACE",
            *messages,
            frame=frame,
            start_sub=start_sub,
            end_sub=end_sub,
            raw=raw,
        )

    def debug(self, *messages, start_sub=False, end_sub=False, raw=False):
        frame = inspect.currentframe().f_back
        self.log(
            "DEBUG",
            *messages,
            frame=frame,
            start_sub=start_sub,
            end_sub=end_sub,
            raw=raw,
        )

    def info(self, *messages, start_sub=False, end_sub=False, raw=False):
        frame = inspect.currentframe().f_back
        self.log(
            "INFO",
            *messages,
            frame=frame,
            start_sub=start_sub,
            end_sub=end_sub,
            raw=raw,
        )

    def success(self, *messages, start_sub=False, end_sub=False, raw=False):
        frame = inspect.currentframe().f_back
        self.log(
            "SUCCESS",
            *messages,
            frame=frame,
            start_sub=start_sub,
            end_sub=end_sub,
            raw=raw,
        )

    def failed(self, *messages, start_sub=False, end_sub=False, raw=False):
        frame = inspect.currentframe().f_back
        self.log(
            "FAILED",
            *messages,
            frame=frame,
            start_sub=start_sub,
            end_sub=end_sub,
            raw=raw,
        )

    def warn(self, *messages, start_sub=False, end_sub=False, raw=False):
        frame = inspect.currentframe().f_back
        self.log(
            "WARNING",
            *messages,
            frame=frame,
            start_sub=start_sub,
            end_sub=end_sub,
            raw=raw,
        )

    def error(self, *messages, start_sub=False, end_sub=False, raw=False):
        frame = inspect.currentframe().f_back
        self.log(
            "ERROR",
            *messages,
            frame=frame,
            start_sub=start_sub,
            end_sub=end_sub,
            raw=raw,
        )

    def critical(self, *messages, start_sub=False, end_sub=False, raw=False):
        frame = inspect.currentframe().f_back
        self.log(
            "CRITICAL",
            *messages,
            frame=frame,
            start_sub=start_sub,
            end_sub=end_sub,
            raw=raw,
        )

    def done(self, *messages, start_sub=False, end_sub=False, raw=False):
        frame = inspect.currentframe().f_back
        self.log(
            "DONE",
            *messages,
            frame=frame,
            start_sub=start_sub,
            end_sub=end_sub,
            raw=raw,
        )

    def exception(self, *messages, _raise=True):
        frame = inspect.currentframe().f_back
        self.log(
            "EXCEPTION",
            *messages,
            frame=frame,
            _raise=_raise,
            start_sub=False,
            end_sub=False,
            raw=False,
        )

    def remove_line(self):
        """Method to remove one line from the command line"""
        print("\033[A\033[K", end="")

    def remove_lines(self, num: int):
        """Method to remove multiple line from the command line

        Args:
            num (int): Number of lines to be cleared
        """
        for i in range(num):
            self.remove_line()

    def start(self, *messages) -> str:
        """Starts a background task, adding it to the queue."""
        start_time = time()
        message = self.__get_message__(*messages)
        self.__total_tasks__ += 1
        task_id = self.__total_tasks__
        frame = inspect.currentframe().f_back
        task = {
            "id": task_id,
            "message": message,
            "start_time": start_time,
            "now": datetime.datetime.now().isoformat(timespec="milliseconds"),
            "frame": frame,
            "level": LOGGER_LEVELS.get("RUNNING"),
        }
        # Put the log information into the queue
        self.__tasks__.append(task)

        # # Start the processing thread if it's not already running
        # if self._task_thread is None or not self._task_thread.is_alive():
        #     self.__stop_event__.clear()  # Ensure the event is cleared
        #     self._task_finished.clear()
        #     self._task_thread = Thread(
        #         target=self._process_task_queue, daemon=True)
        #     self._task_thread.start()
        return task_id

    def finish(self, task_id: str, *messages, success: bool = True):
        """Marks a task as finished and logs the result.

        Since we're using a queue,  we don't "finish" a specific task by ID.
        Instead we log a completion message, and the processing thread
        will eventually clear the queue.
        """
        frame = inspect.currentframe().f_back
        message = self.__get_message__(*messages)
        postfix = f" {message}" if message.strip() else ""
        # Find the task in the queue by ID and remove it
        task = list(filter(lambda x: x["id"] == task_id, self.__tasks__))
        if len(task) == 0:
            return
        task = task[0]
        self.__tasks__.remove(task)
        task["result_message"] = message
        task["postfix"] = postfix
        task["success"] = success
        task["frame"] = frame
        self.__end_tasks__.append(task.copy())

    def clear_threads(self) -> None:
        """Stop any running task animation threads."""
        self.__stop_event__.set()

        if self.__log_thread__:
            self.__log_thread__.join()
            self.__log_thread__ = None
        self.__stop_event__.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clear_threads()

    def on_destroy(self):
        print("Object was destroyed...")


log = Logger("default", "test.log")


def __clean__():
    global log
    log.clear_threads()


atexit.register(__clean__)
