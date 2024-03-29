"""
This config file is a simple collection of directories and constants that are
to be used in the Minesweeper application. These values do not change between
instances of the game, unless manually changed. Many functions rely on these 
constants so removal of any would prevent the game from functioning properly.
"""

# Text font
MAIN_FONT = "assets/fonts/FORCED SQUARE.ttf"
MAIN_FONT_SIZE = 160

TEXT_FONT = "assets/fonts/Roboto-Regular.ttf"
TEXT_FONT_SIZE = 40

TEXT_FONT_BOLD = "assets/fonts/Roboto-Bold.ttf"
TEXT_FONT_BOLD_SIZE = 40

NUMBER_FONT = "assets/fonts/Roboto-Regular.ttf"
NUMBER_FONT_SIZE = 60

FLAG_ICON = "assets/icons/flag.png"
CLOCK_ICON = "assets/icons/clock.png"
SOUND_ICON = "assets/icons/sound_on.png"
MUTE_ICON = "assets/icons/sound_off.png"
EXIT_ICON = "assets/icons/exit.png"
SETTINGS_ICON = "assets/icons/settings.png"
CERTIFICATE_ICON = "assets/icons/certificate.png"
SETTINGS_MENU = "assets/elements/menu_settings_720.png"
LEADERBOARD_MENU = "assets/elements/menu_leaderboard_720_full.png"
PROMPT = "assets/elements/prompt_template.png"

NUMBER_1 = "assets/icons/num_1.png"
NUMBER_2 = "assets/icons/num_2.png"
NUMBER_3 = "assets/icons/num_3.png"
NUMBER_4 = "assets/icons/num_4.png"

MINE_BLUE = "assets/icons/mine_blue.png"
MINE_CYAN = "assets/icons/mine_cyan.png"
MINE_MAGENTA = "assets/icons/mine_magenta.png"
MINE_ORANGE = "assets/icons/mine_orange.png"
MINE_PURPLE = "assets/icons/mine_purple.png"
MINE_RED = "assets/icons/mine_red.png"
MINE_YELLOW = "assets/icons/mine_yellow.png"



# RGB Colour values
COLOUR_BLACK = (0, 0, 0)
COLOUR_WHITE = (255, 255, 255)
COLOUR_DARK_BLUE = (52, 79, 200)
COLOUR_BLUE = (74, 192, 253)
COLOUR_GREEN = (0, 128, 0)
COLOUR_RED = (210, 4, 45)
COLOUR_PURPLE = (128, 0, 128)

COLOUR_BORDER = (135, 175, 58)
COLOUR_TAB = (74, 117, 44)

COLOUR_SETTINGS = (68, 145, 187)

TILE_BROWN1 = (215, 184, 153)
TILE_BROWN2 = (229, 194, 159)
TILE_GREEN1 = (167, 217, 72)
TILE_GREEN2 = (142, 204, 57)

RESOLUTION = 720

# Feature dimensions in pixels
TAB_SIZE = 100

# Gameplay
FPS = 60