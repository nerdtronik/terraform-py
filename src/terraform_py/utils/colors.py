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

    @staticmethod
    def bold(text: str):
        return f"{color.BOLD}{text}{color.END}"

    @staticmethod
    def italic(text: str):
        return f"{color.ITALIC}{text}{color.END}"

    @staticmethod
    def underline(text: str):
        return f"{color.UNDERLINE}{text}{color.END}"

    @staticmethod
    def underline_thick(text: str):
        return f"{color.UNDERLINE_THICK}{text}{color.END}"

    @staticmethod
    def bg_white(text: str):
        return f"{color.HIGHLIGHTED}{text}{color.END}"

    @staticmethod
    def bg_black(text: str):
        return f"{color.HIGHLIGHTED_BLACK}{text}{color.END}"

    @staticmethod
    def bg_blue(text: str):
        return f"{color.HIGHLIGHTED_BLUE}{text}{color.END}"

    @staticmethod
    def bg_cyan(text: str):
        return f"{color.HIGHLIGHTED_CYAN}{text}{color.END}"

    @staticmethod
    def bg_yellow(text: str):
        return f"{color.HIGHLIGHTED_YELLOW}{text}{color.END}"

    @staticmethod
    def bg_red(text: str):
        return f"{color.HIGHLIGHTED_RED}{text}{color.END}"

    @staticmethod
    def bg_green(text: str):
        return f"{color.HIGHLIGHTED_GREEN}{text}{color.END}"

    @staticmethod
    def bg_purple(text: str):
        return f"{color.HIGHLIGHTED_PURPLE}{text}{color.END}"

    @staticmethod
    def bg_grey(text: str):
        return f"{color.HIGHLIGHTED_GREY}{text}{color.END}"

    @staticmethod
    def bg_light_grey(text: str):
        return f"{color.HIGHLIGHTED_GREY_LIGHT}{text}{color.END}"

    @staticmethod
    def bg_light_red(text: str):
        return f"{color.HIGHLIGHTED_RED_LIGHT}{text}{color.END}"

    @staticmethod
    def bg_light_yellow(text: str):
        return f"{color.HIGHLIGHTED_YELLOW_LIGHT}{text}{color.END}"

    @staticmethod
    def bg_light_blue(text: str):
        return f"{color.HIGHLIGHTED_BLUE_LIGHT}{text}{color.END}"

    @staticmethod
    def bg_light_purple(text: str):
        return f"{color.HIGHLIGHTED_PURPLE_LIGHT}{text}{color.END}"

    @staticmethod
    def bg_light_green(text: str):
        return f"{color.HIGHLIGHTED_GREEN_LIGHT}{text}{color.END}"

    @staticmethod
    def bg_light_cyan(text: str):
        return f"{color.HIGHLIGHTED_CYAN_LIGHT}{text}{color.END}"

    @staticmethod
    def bg_light_white(text: str):
        return f"{color.HIGHLIGHTED_WHITE_LIGHT}{text}{color.END}"

    @staticmethod
    def strike(text: str):
        return f"{color.STRIKE_THROUGH}{text}{color.END}"

    @staticmethod
    def margin(text: str):
        return f"{color.MARGIN_1}{text}{color.END}"

    @staticmethod
    def margin_2(text: str):
        return f"{color.MARGIN_2}{text}{color.END}"

    @staticmethod
    def black(text: str):
        return f"{color.BLACK}{text}{color.END}"

    @staticmethod
    def dark_red(text: str):
        return f"{color.RED_DARK}{text}{color.END}"

    @staticmethod
    def red(text: str):
        return f"{color.RED}{text}{color.END}"

    @staticmethod
    def green(text: str):
        return f"{color.GREEN}{text}{color.END}"

    @staticmethod
    def dark_green(text: str):
        return f"{color.GREEN_DARK}{text}{color.END}"

    @staticmethod
    def yellow(text: str):
        return f"{color.YELLOW}{text}{color.END}"

    @staticmethod
    def orange(text: str):
        return f"{color.YELLOW_DARK}{text}{color.END}"

    @staticmethod
    def blue(text: str):
        return f"{color.BLUE}{text}{color.END}"

    @staticmethod
    def dark_blue(text: str):
        return f"{color.BLUE_DARK}{text}{color.END}"

    @staticmethod
    def purple(text: str):
        return f"{color.PURPLE}{text}{color.END}"

    @staticmethod
    def dark_purple(text: str):
        return f"{color.PURPLE_DARK}{text}{color.END}"

    @staticmethod
    def cyan(text: str):
        return f"{color.CYAN}{text}{color.END}"

    @staticmethod
    def dark_cyan(text: str):
        return f"{color.CYAN_DARK}{text}{color.END}"

    @staticmethod
    def grey(text: str):
        return f"{color.GREY_DARK}{text}{color.END}"

    @staticmethod
    def white(text: str):
        return f"{color.WHITE}{text}{color.END}"
