import datetime
import hashlib
import inspect
import json
import logging
import logging.handlers
import os
import shutil
import sys
from queue import Empty, Queue
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
    "CRITICAL": f"{color.BOLD}{color.HIGHLIGHTED_RED}CRIT{color.END}",
    "EXCEPTION": f"{color.BOLD}{color.HIGHLIGHTED_YELLOW}EXCP{color.END}",
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
    def __init__(
        self,
        fmt: str = None,
        datefmt: str = None,
        style="%",
        validate=True,
        colors=True,
        **args,
    ):
        super().__init__(fmt, datefmt, style, validate)
        self._show_level = args.get("level", True)
        self._show_date = args.get("date", True)
        self._show_file = args.get("file", True)
        self._show_env = args.get("env", True)
        self.colors = colors
        self.fmt = fmt

    def format(self, record):
        if self.fmt:
            return super().format(record)
        message = ""
        if self.colors:
            if self._show_date:
                message += f"{color.BLUE_DARK}{record.args['asctime']}{color.END} "
            if self._show_env:
                message += f"{color.PURPLE}({record.name}){color.END} "
            if self._show_level:
                message += (
                    f"{LOGGER_LEVEL_COLORS.get(record.levelname, record.levelname)} "
                )
            if self._show_file:
                message += f"{color.GREEN_DARK}{record.filename}{color.YELLOW_DARK}:{color.GREEN_DARK}{record.lineno}{color.END} "
        else:
            if self._show_date:
                message += f"{record.args['asctime']} "
            if self._show_env:
                message += f"({record.name}) "
            if self._show_level:
                message += f"{record.levelname} "
            if self._show_file:
                message += f"{record.filename}:{record.lineno} "
        message += f"| {record.getMessage()}"
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
        self._log_queue = Queue()  # Queue for log messages
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
        self.logger = logging.getLogger(env)
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

    def log(self, level: str, *messages, frame=None):
        """Logs a message at the specified level.

        Adds the log entry to the queue for processing in a separate thread.
        """
        level_value = LOGGER_LEVELS.get(level.upper())
        if level_value is None:
            raise ValueError(f"Invalid log level: {level}")

        if not frame:
            frame = inspect.currentframe().f_back.f_back

        # Put the log information into the queue
        now = datetime.datetime.isoformat(datetime.datetime.now())
        self._log_queue.put((level.upper(), level_value, messages, frame, now))

    def _process_log_queue(self):
        """Processes the log queue in a separate thread."""
        while not self._stop_event.is_set():
            try:
                level_str, level_value, messages, frame, now = self._log_queue.get(
                    timeout=0.2
                )
                filename = (
                    "/".join(frame.f_code.co_filename.split(os.sep)[-2:])
                    if frame
                    else "unknown"
                )
                line = frame.f_lineno if frame else 0

                message = self._get_message(*messages)
                # Use standard library logging, but format as before.
                record = self.logger.makeRecord(
                    self.env,
                    level_value,
                    filename,
                    line,
                    message,
                    ({"asctime": now},),
                    None,
                )
                self.logger.handle(record)
                if level_str == "EXCEPTION":
                    raise Exception(message)
            except Empty:
                continue  # Check stop_event
            except Exception as e:
                print(f"Error in _process_log_queue: {e}", file=sys.stderr)

    def _start_log_thread(self):
        """Starts the log processing thread."""
        if self._log_thread is None or not self._log_thread.is_alive():
            self._stop_event.clear()  # Make sure it's clear
            self._log_thread = Thread(target=self._process_log_queue, daemon=True)
            self._log_thread.start()

    def set_env(self, env: str):
        self.env = env

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

    def exception(self, *messages):
        frame = inspect.currentframe().f_back
        self.log("EXCEPTION", *messages, frame=frame)

    def _process_task_queue(self):
        """Processes tasks from the queue and logs their status."""
        animation_index = 0
        while not self._stop_event.is_set():
            try:
                # Get a task from the queue.  Use a timeout to allow checking _stop_event.
                if len(self._tasks) == 0:
                    continue
                task = self._tasks[-1]
                # if not started:
                #     self.remove_line()
                #     started=True
                while not self._task_finished.is_set():
                    task_id, message, start_time = (
                        task["id"],
                        task["message"],
                        task["start_time"],
                    )
                    num_tasks = len(self._tasks)  # +1 for the current task
                    if num_tasks == 0:
                        break
                    log_message = f"{message} ({num_tasks} bg tasks) {self._animation[animation_index]} ({format_elapsed_time(start_time, time())})"
                    # Log the task update (to console via standard logging)
                    self.log("RUNNING", log_message, frame=task["frame"])

                    animation_index = (animation_index + 1) % len(self._animation)
                    self._task_finished.wait(0.2)
                    if self._task_finished.is_set():
                        break
                    self.remove_line()
                self.remove_line()
                for task in self._end_tasks.copy():
                    self._end_tasks.remove(task)
                    if task["success"]:
                        log_level = "COMPLETED"
                        log_msg = f"{task['message']} ✅ ({format_elapsed_time(task['start_time'], time())}){task['postfix']}"
                    else:
                        log_level = "FAILED"
                        log_msg = f"{task['message']} ❌ ({format_elapsed_time(task['start_time'], time())}){task['postfix']}"

                    self.log(log_level, log_msg, frame=task["frame"])
                self._task_finished.clear()

            except Empty:
                # No tasks in the queue, but thread might not be stopped yet
                continue
            except Exception as e:
                self.logger.exception(f"Error in _process_queue: {e}")

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
        task_id = hashlib.md5(
            (message + str(start_time)).encode(), usedforsecurity=False
        ).hexdigest()
        frame = inspect.currentframe().f_back
        task = {
            "id": task_id,
            "message": message,
            "start_time": start_time,
            "frame": frame,
        }
        self._tasks.append(task)

        # Start the processing thread if it's not already running
        if self._task_thread is None or not self._task_thread.is_alive():
            self._stop_event.clear()  # Ensure the event is cleared
            self._task_finished.clear()
            self._task_thread = Thread(target=self._process_task_queue, daemon=True)
            self._task_thread.start()
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
        self._task_finished.set()

    def clear_threads(self) -> None:
        """Stop any running task animation threads."""
        self._stop_event.set()
        self._task_finished.set()
        if self._task_thread:
            self._task_thread.join()
            self._task_thread = None
        if self._log_thread:
            self._log_thread.join()
            self._log_thread = None
        self._stop_event.clear()
        self._task_finished.clear()


log = Logger("default")
