import traceback
import atexit
import datetime
import hashlib
import inspect
import json
import logging
import logging.handlers
import os
import shutil
import sys
from queue import Queue
from threading import Event, Thread
from time import time
# ANSI escape codes for colors and styles (cross-platform)


class color:
    DEFAULT = "\033[0m"
    END = "\033[0m"
    # Styles
    BOLD = "\033[1m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    UNDERLINE_THICK = "\033[21m"
    HIGHLIGHTED = "\033[7m"
    HIGHLIGHTED_BLACK = "\033[40m"
    HIGHLIGHTED_RED = "\033[41m"
    HIGHLIGHTED_GREEN = "\033[42m"
    HIGHLIGHTED_YELLOW = "\033[43m"
    HIGHLIGHTED_BLUE = "\033[44m"
    HIGHLIGHTED_PURPLE = "\033[45m"
    HIGHLIGHTED_CYAN = "\033[46m"
    HIGHLIGHTED_GREY = "\033[47m"

    HIGHLIGHTED_GREY_LIGHT = "\033[100m"
    HIGHLIGHTED_RED_LIGHT = "\033[101m"
    HIGHLIGHTED_GREEN_LIGHT = "\033[102m"
    HIGHLIGHTED_YELLOW_LIGHT = "\033[103m"
    HIGHLIGHTED_BLUE_LIGHT = "\033[104m"
    HIGHLIGHTED_PURPLE_LIGHT = "\033[105m"
    HIGHLIGHTED_CYAN_LIGHT = "\033[106m"
    HIGHLIGHTED_WHITE_LIGHT = "\033[107m"

    STRIKE_THROUGH = "\033[9m"
    MARGIN_1 = "\033[51m"
    MARGIN_2 = "\033[52m"  # seems equal to MARGIN_1
    # colors
    BLACK = "\033[30m"
    RED_DARK = "\033[31m"
    GREEN_DARK = "\033[32m"
    YELLOW_DARK = "\033[33m"
    BLUE_DARK = "\033[34m"
    PURPLE_DARK = "\033[35m"
    CYAN_DARK = "\033[36m"
    GREY_DARK = "\033[37m"

    BLACK_LIGHT = "\033[90m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"


__LOGGERS__ = []


HANDLE_EXCEPTIONS = True


def __catcher__(type, value, tback):
    if HANDLE_EXCEPTIONS:
        for logger in __LOGGERS__:
            for line in traceback.format_tb(tback):
                for ln in line.splitlines():
                    log.exception(ln, _raise=False)
            for line in str(value).splitlines():
                log.exception(line, _raise=False)
    else:
        sys.__excepthook__(type, value, tback)
        # log.exception("\n", "\n".join(traceback.format_tb(tback)),
        #   value, _raise=False)


sys.excepthook = __catcher__

LOGGER_LEVEL_COLORS = {
    "TRACE": f"{color.BOLD}{color.PURPLE}TRAC{color.END}",
    "RUNNING": f"{color.BOLD}{color.PURPLE}RUNN{color.END}",
    "DEBUG": f"{color.BOLD}{color.CYAN}DEBG{color.END}",
    "INFO": f"{color.BOLD}{color.WHITE}INFO{color.END}",
    "DONE": f"{color.BOLD}{color.GREEN}DONE{color.END}",
    "SUCCESS": f"{color.BOLD}{color.HIGHLIGHTED_GREEN_LIGHT}SUCC{color.END}",
    "COMPLETED": f"{color.BOLD}{color.HIGHLIGHTED_GREEN}COMP{color.END}",
    "WARNING": f"{color.BOLD}{color.YELLOW_DARK}WARN{color.END}",
    "ERROR": f"{color.BOLD}{color.RED}ERRR{color.END}",
    "FAILED": f"{color.BOLD}{color.HIGHLIGHTED_RED}FAIL{color.END}",
    "CRITICAL": f"{color.BOLD}{color.HIGHLIGHTED_RED_LIGHT}CRIT{color.END}",
    "EXCEPTION": f"{color.BOLD}{color.HIGHLIGHTED_RED}EXCP{color.END}",
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
    "EXCEPTION": logging.CRITICAL + 1,  # Above CRITICAL
}

# Define custom logging levels
logging.addLevelName(LOGGER_LEVELS["TRACE"], "TRACE")
logging.addLevelName(LOGGER_LEVELS["SUCCESS"], "SUCCESS")
logging.addLevelName(LOGGER_LEVELS["EXCEPTION"], "EXCEPTION")
logging.addLevelName(LOGGER_LEVELS["RUNNING"], "RUNNING")
logging.addLevelName(LOGGER_LEVELS["FAILED"], "FAILED")
logging.addLevelName(LOGGER_LEVELS["COMPLETED"], "COMPLETED")
logging.addLevelName(LOGGER_LEVELS["DONE"], "DONE")


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

        message = ""

        # Safely access record arguments with defaults
        args = getattr(record, 'args', {})
        if not isinstance(args, dict):
            args = {}

        asctime = args.get(
            'asctime', datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))

        # Handle line continuation
        if not args.get('last_log', True) and args.get('started', False):
            message += "\033[A\033[K"  # Move up one line and clear it

        if self.colors:
            if self._show_date:
                message += f"{color.BLUE_DARK}{asctime}{color.END} "
            if self._show_env:
                message += f"{color.PURPLE}({args.get('env', 'default')}){color.END} "
            if self._show_level:
                message += (
                    f"{LOGGER_LEVEL_COLORS.get(record.levelname, record.levelname)} "
                )
            if self._show_file:
                message += f"{color.GREEN_DARK}{record.filename}{color.YELLOW_DARK}:{color.GREEN_DARK}{record.lineno}{color.END} "
        else:
            if self._show_date:
                message += f"{asctime} "
            if self._show_env:
                message += f"({args.get('env', 'default')}) "
            if self._show_level:
                message += f"{record.levelname} "
            if self._show_file:
                message += f"{record.filename}:{record.lineno} "
        message += f"| {record.msg}"
        return message


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
        self._tasks = []
        self._end_tasks = []
        self._log_queue = Queue()
        self._animation = ["⠙", "⠘", "⠰", "⠴", "⠤", "⠦", "⠆", "⠃", "⠋", "⠉"]
        self.h_separator = "─"
        self.v_separator = " "
        self._enable_colors = colors
        self._log_file = log_file
        self._max_log_size = max_log_size_mb
        self._backup_count = backup_count
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
        self._custom_formatters()

        # --- Threading for background tasks and logging ---
        self._task_thread: Thread = None
        self._log_thread: Thread = None
        self._stop_event = Event()  # Use an Event for cleaner thread stopping
        self._task_finished = Event()

        self._start_log_thread()
        __LOGGERS__.append(self)

    def _custom_formatters(self):
        """Formats log messages with colors and additional info."""
        self.file_formatter = LoggerFormatter(colors=False, **self.flags)
        self.formatter = LoggerFormatter(colors=True, **self.flags)

        if self.console_handler is not None:
            self.logger.removeHandler(self.console_handler)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.formatter)  # Use custom formatter
        console_handler.setLevel(logging.INFO)  # Default console level
        self.console_handler = console_handler
        self.logger.addHandler(self.console_handler)

        if self._log_file:
            if self.file_handler is not None:
                self.logger.removeHandler(self.file_handler)
            file_handler = logging.handlers.RotatingFileHandler(
                self._log_file,
                maxBytes=self._max_log_size * 1024 * 1024,  # Convert MB to bytes
                backupCount=self._backup_count,
            )
            file_handler.setFormatter(self.file_formatter)
            file_handler.setLevel(logging.DEBUG)  # Log everything to file
            self.file_handler = file_handler
            self.logger.addHandler(file_handler)

    def show_file(self, show=True):
        self.flags["file"] = show
        self._custom_formatters()

    def show_date(self, show=True):
        self.flags["date"] = show
        self._custom_formatters()

    def show_env(self, show=True):
        self.flags["env"] = show
        self._custom_formatters()

    def show_level(self, show=True):
        self.flags["level"] = show
        self._custom_formatters()

    def set_level(self, level: str):
        """Set the logging level for the console handler."""
        level = level.upper()
        if level not in LOGGER_LEVELS:
            raise ValueError(f"Invalid log level: {level}")
        self.console_handler.setLevel(LOGGER_LEVELS[level])
        self._custom_formatters()

    def log(self, level: str, *messages, frame=None, _raise=False):
        """Logs a message at the specified level.

        Adds the log entry to the queue for processing in a separate thread.
        """
        level_value = LOGGER_LEVELS.get(level.upper())
        if level_value is None:
            raise ValueError(f"Invalid log level: {level}")

        if not frame:
            frame = inspect.currentframe().f_back.f_back

        message = self._get_message(*messages)
        # Put the log information into the queue
        now = datetime.datetime.isoformat(datetime.datetime.now())
        self._log_queue.put_nowait(
            (level.upper(), level_value, message, frame, now, _raise))

    def _process_log_queue(self):
        """Processes the log queue in a separate thread."""
        animation_index = 0
        last_message_log = True
        started = False
        cycle_start = time()
        delta = 0.2
        while not self._stop_event.is_set() or not self._log_queue.empty():
            cycle_period = time()
            try:
                # Get a task from the queue.  Use a timeout to allow checking _stop_event.
                num_tasks = len(self._tasks)  # +1 for the current task
                if num_tasks > 0 and (cycle_period - cycle_start) >= delta:
                    cycle_start = time()
                    task = self._tasks[0]
                    message, start_time, now, frame, level_value = (
                        task["message"],
                        task["start_time"],
                        task["now"],
                        task["frame"],
                        task["level"],
                    )
                    log_message = f"{message} ({num_tasks} bg tasks) {self._animation[animation_index]} ({format_elapsed_time(start_time, time())})"

                    self.log("RUNNING", log_message, frame=task["frame"])
                    # sleep(0.1)
                    # self.remove_line()
                    animation_index = (animation_index +
                                       1) % len(self._animation)

                if len(self._end_tasks) > 0:
                    for task in self._end_tasks.copy():
                        self._end_tasks.remove(task)
                        if task["success"]:
                            log_level = "COMPLETED"
                            log_msg = f"{task['message']} ✅ ({format_elapsed_time(task['start_time'], time())}){task['postfix']}"
                        else:
                            log_level = "FAILED"
                            log_msg = f"{task['message']} ❌ ({format_elapsed_time(task['start_time'], time())}){task['postfix']}"

                        self.log(log_level, log_msg, frame=task["frame"])

                if not self._log_queue.empty():
                    level_str, level_value, message, frame, now, _raise = self._log_queue.get(
                        timeout=0.1
                    )
                    filename = (
                        "/".join(frame.f_code.co_filename.split(os.sep)[-2:])
                        if frame
                        else "unknown"
                    )
                    line = frame.f_lineno if frame else 0

                    # Use standard library logging, but format as before.
                    log_record = self.logger.makeRecord(
                        self.env,
                        level_value,
                        filename,
                        line,
                        message,
                        (
                            {
                                "asctime": now,
                                "last_log": last_message_log,
                                "started": started,
                                "env": self.env
                            },
                        ),
                        None,
                    )
                    self.logger.handle(log_record)
                    if LOGGER_LEVELS["RUNNING"] == level_value:
                        last_message_log = False
                    else:
                        last_message_log = True
                    if not started:
                        started = True
                    if _raise:
                        raise Exception(message)

            except Exception as e:
                print(e)
                raise e

    def _start_log_thread(self):
        """Starts the log processing thread."""
        if self._log_thread is None or not self._log_thread.is_alive():
            self._stop_event.clear()  # Make sure it's clear
            self._log_thread = Thread(
                target=self._process_log_queue, daemon=True)
            self._log_thread.start()

    def set_env(self, env: str):
        self.env = env
        self._custom_formatters()

    def sep(self):
        """Prints a horizontal separator."""
        width = shutil.get_terminal_size((80, 20))[0]
        # Use logger to go through the queue
        self.logger.info(self.h_separator * width)

    def _get_message(self, *messages) -> str:
        res = []
        for msg in messages:
            if isinstance(msg, (dict, list)):  # Use isinstance for type checking
                res.append(json.dumps(msg))
            else:
                res.append(str(msg))
        return self.v_separator.join(res)

    def trace(self, *messages):
        frame = inspect.currentframe().f_back
        self.log("TRACE", *messages, frame=frame)

    def debug(self, *messages):
        frame = inspect.currentframe().f_back
        self.log("DEBUG", *messages, frame=frame)

    def info(self, *messages):
        frame = inspect.currentframe().f_back
        self.log("INFO", *messages, frame=frame)

    def success(self, *messages):
        frame = inspect.currentframe().f_back
        self.log("SUCCESS", *messages, frame=frame)

    def warn(self, *messages):
        frame = inspect.currentframe().f_back
        self.log("WARNING", *messages, frame=frame)

    def error(self, *messages):
        frame = inspect.currentframe().f_back
        self.log("ERROR", *messages, frame=frame)

    def critical(self, *messages):
        frame = inspect.currentframe().f_back
        self.log("CRITICAL", *messages, frame=frame)

    def done(self, *messages):
        frame = inspect.currentframe().f_back
        self.log("DONE", *messages, frame=frame)

    def exception(self, *messages, _raise=True):
        frame = inspect.currentframe().f_back
        self.log("EXCEPTION", *messages, frame=frame, _raise=_raise)

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
        message = self._get_message(*messages)
        try:
            task_id = hashlib.md5(
                (message + str(start_time)).encode(), usedforsecurity=False
            ).hexdigest()
        except:
            task_id = hashlib.md5(
                (message + str(start_time)).encode()
            ).hexdigest()  # nosec
        frame = inspect.currentframe().f_back
        task = {
            "id": task_id,
            "message": message,
            "start_time": start_time,
            "now": datetime.datetime.isoformat(datetime.datetime.now()),
            "frame": frame,
            "level": LOGGER_LEVELS.get("RUNNING"),
        }
        # Put the log information into the queue
        self._tasks.append(task)

        # # Start the processing thread if it's not already running
        # if self._task_thread is None or not self._task_thread.is_alive():
        #     self._stop_event.clear()  # Ensure the event is cleared
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
        message = self._get_message(*messages)
        postfix = f" {message}" if message.strip() else ""
        # Find the task in the queue by ID and remove it
        task = list(filter(lambda x: x["id"] == task_id, self._tasks))
        if len(task) == 0:
            return
        task = task[0]
        self._tasks.remove(task)
        task["result_message"] = message
        task["postfix"] = postfix
        task["success"] = success
        task["frame"] = frame
        self._end_tasks.append(task.copy())

    def clear_threads(self) -> None:
        """Stop any running task animation threads."""
        self._stop_event.set()

        if self._log_thread:
            self._log_thread.join()
            self._log_thread = None
        self._stop_event.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clear_threads()

    def on_destroy(self):
        print("Object was destroyed...")


log = Logger("default")


def __clean__():
    global log
    log.clear_threads()


atexit.register(__clean__)
