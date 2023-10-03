import os
import random
import pygame as pg
import pygame_menu as pgm
from config import *
import database

# If PyGame cannot be imported, install using the following PIP commands:

# > py -m pip install -U pygame --user
# > py -m pip install -U pygame_menu --user

# Clear the terminal for debugging purposes
os.system("cls")

# Initialize pygame and set window parameters
pg.init()
screen = pg.display.set_mode((RESOLUTION, RESOLUTION))

# Fonts used by numbers such as the timer and flag counter
numberFont = pg.font.Font(NUMBER_FONT, 35)

# List of possible mine colors once revealed
mineColours = [MINE_BLUE, MINE_CYAN, MINE_MAGENTA, MINE_ORANGE, MINE_PURPLE, MINE_RED, MINE_YELLOW]

# Directories of number images to use on the board
numbers = [NUMBER_1, NUMBER_2, NUMBER_3, NUMBER_4]

# Create Pygame-Menu base images for menu interfaces
settingsMenuImage = pgm.baseimage.BaseImage(image_path=SETTINGS_MENU, drawing_mode=pgm.baseimage.IMAGE_MODE_SIMPLE)
leaderboardMenuImage = pgm.baseimage.BaseImage(image_path=LEADERBOARD_MENU, drawing_mode=pgm.baseimage.IMAGE_MODE_SIMPLE)
promptImage = pgm.baseimage.BaseImage(image_path=PROMPT, drawing_mode=pgm.baseimage.IMAGE_MODE_SIMPLE)

# Constants
TILE_SIZE = None  # Tile size will be set based on difficulty
USER_ID = 1  # Default user when the game first starts

# Database initialization
db = database.Database("data/database.sqlite")
db.create_tables()
db.create_user("Guest")

def tilesize_set_constant(tileSize):
    """
    Set the global TILE_SIZE based on the chosen difficulty.
    Args:
        tileSize (int): The size of each tile.
    """
    global TILE_SIZE
    TILE_SIZE = tileSize 

def user_set_constant(username):
    """
    Set the global USER_ID to the user's ID.
    Args:
        username (str): The username of the user.
    """
    global USER_ID
    USER_ID = db.create_user(username)

class Tile(pg.sprite.DirtySprite):
    """
    This class creates an object for each tile on the board, and provides
    each tile with different attributes for use in further calculations
    and operations.
    It is inhertied from the sprite class in pygame so it can be drawn
    and updated using pygame functions.
    """
    def __init__(self, gridY, gridX):
        """
        Initialize a tile with its attributes.
        Args:
            gridY (int): The y-coordinate on the grid.
            gridX (int): The x-coordinate on the grid.
        """
        super().__init__()
        self.gridY = gridY
        self.gridX = gridX
        self.clicked = False
        self.mine = False
        self.flag = False
        self.update = True
        self.mineColour = random.choice(mineColours)
        self.count = 0
        self.pixelPosition = (gridX * TILE_SIZE, (gridY * TILE_SIZE) + 100)
        
    def draw(self):
        """
        Draw the tile on the screen based on its attributes.

        This method updates and draws the tile based on its current state,
        including whether it's flagged, clicked, contains a mine, or shows
        a number. The drawing is optimized to avoid unnecessary operations.

        Returns:
            None
        """
        if self.flag:
            flag_img = pg.image.load(FLAG_ICON)
            self.image = pg.transform.smoothscale(flag_img, (TILE_SIZE, TILE_SIZE))
        elif self.clicked and self.mine and not self.flag:
            mine_img = pg.image.load(self.mineColour)
            self.image = pg.transform.smoothscale(mine_img, (TILE_SIZE, TILE_SIZE))
        else:
            if self.clicked:
                if (self.gridY % 2 == 0) ^ (self.gridX % 2 == 0):
                    colour = TILE_BROWN1
                else:
                    colour = TILE_BROWN2
            else:
                if (self.gridY % 2 == 0) ^ (self.gridX % 2 == 0):
                    colour = TILE_GREEN2
                else:
                    colour = TILE_GREEN1

            self.image = pg.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill(colour)

        self.image.get_rect(topleft=self.pixelPosition)
        screen.blit(self.image, self.pixelPosition)

        if not self.mine and not self.flag and self.clicked and self.count > 0:
            index = self.count - 1 if 1 <= self.count <= 4 else 0
            num_img = pg.image.load(numbers[index])
            self.image = pg.transform.scale(num_img, (TILE_SIZE, TILE_SIZE))
            self.image.get_rect(topleft=self.pixelPosition)
            screen.blit(self.image, self.pixelPosition)


class MinesweeperApp(object):
    """
    This class is the minesweeper application that is used to instance the game itself,
    and perform all necessary operations for a fully functioning game. It has many attributes
    that have predefined types, as some attributes can change between instances of the game,
    without closing the window.
    """

    def __init__(self):
        """
        This is run at the start of the game; or whenever a main setting has been changed,
        such as the user that is logged in. The game then initiates with any new settings.
        """
        self._seed = 17
        self._gamestart = False
        self._playing = True
        self._finished = False
        self._timer = 0
        self._difficultyNum = 1
        self.leaderboard = db.get_leaderboard()
        self.difficulty_select(None, self._difficultyNum)
        self.setup_menus()
        self.setup_grid()
        self._unknownTileCount=self._gridWidth*self._gridHeight
        

    def difficulty_select(self, item: tuple, value: int):
        """
        Re-initializes the game with new difficulty settings.

        This method updates main attribute constants when the difficulty is changed,
        such as grid size, mine count, tile size, and others. It also resets game
        attributes and reconfigures the interface accordingly.

        Args:
            item (tuple): An unused tuple from the text-input.
            value (int): The value representing the selected difficulty:
                        - 0: EASY
                        - 1: MEDIUM
                        - 2: HARD

        Returns:
            None
        """
        difficulties = [
            ("EASY", 10, 8, 10, RESOLUTION // 10),
            ("MEDIUM", 18, 14, 40, RESOLUTION // 18),
            ("HARD", 24, 20, 99, RESOLUTION // 24)
        ]

        self._difficultyName, self._gridWidth, self._gridHeight, self._mineCount, self._tileSize = difficulties[value]
        
        tilesize_set_constant(self._tileSize)
        self._unknownTileCount = self._gridWidth * self._gridHeight
        self._gamestart = False
        self._playing = True
        self._finished = False
        self._timer = 0
        self._flagCount = self._mineCount
        self._difficultyNum = value
        self.leaderboard = db.get_leaderboard()
        screen.fill(COLOUR_BORDER)
        self.setup_menus()
        self.setup_grid()


    def exit_menu(self):
        """
        Exits the current menu without making any changes.

        This method allows the user to exit a menu without applying any changes to
        the game settings. It calls the `difficulty_select` method with the current
        difficulty value to ensure no modifications are made.

        Args:
            None

        Returns:
            None
        """
        self.difficulty_select(None, self._difficultyNum)


    def check_name_test(self, value: str):
        """
        Update the current user's global value and reinitialize the game.

        This method takes a new user name as input, updates the global value of the
        current user, and then reinitializes the game with the new user settings.

        Args:
            value (str): The new user name.

        Returns:
            None
        """
        user_set_constant(value)
        self.__init__()


    def setup_menus(self):
        """
        Set up the game menus, interface elements, and formatting.

        This function configures themes for various menus, such as the home menu,
        settings menu, leaderboard menu, and prompts. It also adds buttons and other
        interactable elements to the menus and assigns their related functions.

        Args:
            None

        Returns:
            None
        """
        # Configure home_theme 
        home_theme = pgm.Theme()
        home_theme.background_color = COLOUR_BORDER
        home_theme.title = False
        home_theme.widget_alignment = pgm.locals.ALIGN_CENTER
        home_theme.widget_background_color = None
        home_theme.widget_font = pgm.font.FONT_FIRACODE_BOLD
        home_theme.widget_font_color = (255, 255, 255)
        home_theme.widget_font_size = 40
        home_theme.widget_padding = 0
        home_theme.widget_selection_effect = \
            pgm.widgets.HighlightSelection(1, 0, 0).set_color((120, 120, 120))

        # Configure settings_theme
        settings_theme = pgm.Theme()
        settings_theme.background_color = settingsMenuImage
        settings_theme.title_bar_style = pgm.widgets.MENUBAR_STYLE_NONE
        settings_theme.title_close_button = False
        settings_theme.title_font_size = 40
        settings_theme.widget_alignment = pgm.locals.ALIGN_CENTER
        settings_theme.widget_font = pgm.font.FONT_FIRACODE_BOLD
        settings_theme.widget_font_color = (100, 12, 14)
        settings_theme.widget_font_size = 40
        settings_theme.widget_padding = 0

        # Configure leaderboard_theme
        leaderboard_theme = pgm.Theme()
        leaderboard_theme.background_color = leaderboardMenuImage
        leaderboard_theme.title_bar_style = pgm.widgets.MENUBAR_STYLE_NONE
        leaderboard_theme.title_close_button = False
        leaderboard_theme.title_font_size = 40
        leaderboard_theme.widget_alignment = pgm.locals.ALIGN_CENTER
        leaderboard_theme.widget_font = pgm.font.FONT_FIRACODE_BOLD
        leaderboard_theme.widget_font_color = COLOUR_BLACK
        leaderboard_theme.widget_font_size = 40
        leaderboard_theme.widget_padding = 0

        # Configure prompt_theme
        prompt_theme = pgm.Theme()
        prompt_theme.background_color = promptImage
        prompt_theme.title_bar_style = pgm.widgets.MENUBAR_STYLE_NONE
        prompt_theme.title_close_button = False
        prompt_theme.title_font_size = 40
        prompt_theme.widget_alignment = pgm.locals.ALIGN_CENTER
        prompt_theme.widget_font = pgm.font.FONT_FIRACODE_BOLD
        prompt_theme.widget_font_color = (100, 12, 14)
        prompt_theme.widget_font_size = 40
        prompt_theme.widget_padding = 0
        

        self._menu = pgm.Menu(
            menu_id="home_menu_instance",
            height=100,
            mouse_motion_selection=True,
            position=(0, 0, False),
            columns=10,
            rows=10,
            theme=home_theme,
            title="",
            width=RESOLUTION
        )

        self._settings = pgm.Menu(
            menu_id="settings_menu_instance",
            width=320, 
            height=534,
            columns=1,
            rows=10,
            mouse_motion_selection=True,
            position=(200, 110, False),
            theme=settings_theme,
            title=""
        )

        self._leaderboard = pgm.Menu(
            menu_id="leaderboard_menu_instance",
            width=534, 
            height=534,
            columns=1,
            rows=10,
            mouse_motion_selection=True,
            position=(110, 110, False),
            theme=leaderboard_theme,
            title=""
        )

        self._prompt = pgm.Menu(
            menu_id="prompt_menu_instance",
            width=320, 
            height=160,
            columns=2,
            rows=2,
            mouse_motion_selection=True,
            position=(200, 110, False),
            theme=prompt_theme,
            title=""
        )

        btn = self._prompt.add.button(
            " ",
            self.exit_menu,
            button_id="prompt_back",
            align=pgm.locals.ALIGN_CENTER,
            float=True,
            font_color=COLOUR_WHITE,
            font_size=30,
            cursor=pgm.locals.CURSOR_HAND,
            selection_effect=pgm.widgets.NoneSelection(),
            margin=(40,40)
        )
        btn.translate(-100,-84)

        btn = self._settings.add.button(
            " ",
            self.exit_menu,
            button_id="settings_back",
            align=pgm.locals.ALIGN_CENTER,
            float=True,
            font_color=COLOUR_WHITE,
            font_size=35,
            cursor=pgm.locals.CURSOR_HAND,
            selection_effect=pgm.widgets.NoneSelection(),
            margin=(40,40)
        )
        btn.translate(-180,-250)

        btn = self._leaderboard.add.button(
            " ",
            self.exit_menu,
            button_id="leaderboard_back",
            align=pgm.locals.ALIGN_CENTER,
            float=True,
            font_color=COLOUR_WHITE,
            font_size=35,
            cursor=pgm.locals.CURSOR_HAND,
            selection_effect=pgm.widgets.NoneSelection(),
            margin=(40,40)
        )
        btn.translate(-286,-238)

        btn = self._settings.add.dropselect(
            title="",
            items=[("Easy", 0),
                   ("Medium", 1),
                   ("Hard", 2)],
            dropselect_id="difficulty",
            default=1,
            font_size=16,
            onchange=self.difficulty_select,
            padding=0,
            placeholder='Select one',
            selection_box_height=5,
            selection_box_inflate=(0, 20),
            selection_box_margin=0,
            selection_box_text_margin=10,
            selection_box_width=200,
            selection_option_font_size=20,
            shadow_width=20
        )

        btn = self._settings.add.text_input(
            "    ",
            default="",
            onreturn=self.check_name_test,
            textinput_id="username",
            background_color=COLOUR_WHITE,
            border_color=COLOUR_BLACK,
            border_width=1,
            font_color=COLOUR_BLACK,
            font_name=TEXT_FONT,
            font_size=32,
            padding=1,
            selection_effect=pgm.widgets.NoneSelection(),
            text_ellipsis="..."
        )
        btn.translate(0,15)

        btn = self._settings.add.label(
            db.get_user(USER_ID)[1], 
            font_name=TEXT_FONT, 
            font_size=15
        )
        btn.translate(0,-110)
        
        btn = self._menu.add.button(
            "   ",
            self._leaderboard,
            button_id="leaderboardButton",
            align=pgm.locals.ALIGN_RIGHT,
            float=True,
            font_size=40,
            cursor=pg.SYSTEM_CURSOR_HAND,
            selection_effect=pgm.widgets.NoneSelection(),
            margin=(0, 0)
        )
        btn.translate(-40,0)

        btn = self._menu.add.button(
            "  ",
            self._settings,
            button_id="settingsButton",
            align=pgm.locals.ALIGN_LEFT,
            float=True,
            font_size=40,
            cursor=pg.SYSTEM_CURSOR_HAND,
            selection_effect=pgm.widgets.NoneSelection(),
            margin=(40, 40))
        
        btn.translate(2,0)

        self._menu.add.image(
            image_path=SETTINGS_ICON,
            image_id="settingsIcon",
            margin=(40,40),
            align=pgm.locals.ALIGN_LEFT,
            cursor=pg.SYSTEM_CURSOR_HAND,
            scale_smooth=True,
            scale=(0.06, 0.06)
        )


        try:
            easy_place1score = ("  " + "{:03d}".format(self.leaderboard[0][0][1])) + "  "
            easy_place1name = "  " + db.get_user(self.leaderboard[0][0][0])[1].ljust(40) 
        except IndexError:
            easy_place1score = ""
            easy_place1name = ""
        try:
            easy_place2score = "  " + "{:03d}".format(self.leaderboard[0][1][1]) + "  "
            easy_place2name = "  " + db.get_user(self.leaderboard[0][1][0])[1].ljust(40) 
        except IndexError:
            easy_place2score = ""
            easy_place2name = ""
        try:
            easy_place3score = "  " + "{:03d}".format(self.leaderboard[0][2][1]) + "  " 
            easy_place3name = "  " + db.get_user(self.leaderboard[0][2][0])[1].ljust(40) 
        except IndexError:
            easy_place3score = ""
            easy_place3name = ""

        easy_table = self._leaderboard.add.table(font_size=20, float=True)
        easy_table.default_cell_padding = 7
        easy_table.default_cell_align = pgm.locals.ALIGN_LEFT
        easy_table.default_row_background_color = (0,0,0,0)
        easy_table.add_row([easy_place1score, easy_place1name], cell_font=TEXT_FONT_BOLD, cell_border_width=0)
        easy_table.add_row([easy_place2score, easy_place2name], cell_font=TEXT_FONT_BOLD, cell_border_width=0)
        easy_table.add_row([easy_place3score, easy_place3name], cell_font=TEXT_FONT_BOLD, cell_border_width=0)
        easy_table.translate(8,-157)

        try:
            medium_place1score = "  " + "{:03d}".format(self.leaderboard[1][0][1]) + "  " 
            medium_place1name = "  " + db.get_user(self.leaderboard[1][0][0])[1].ljust(40) 
        except IndexError:
            medium_place1score = ""
            medium_place1name = ""
        try:
            medium_place2score = "  " + "{:03d}".format(self.leaderboard[1][1][1]) + "  " 
            medium_place2name = "  " + db.get_user(self.leaderboard[1][1][0])[1].ljust(40) 
        except IndexError:
            medium_place2score = ""
            medium_place2name = ""
        try:
            medium_place3score = "  " + "{:03d}".format(self.leaderboard[1][2][1]) + "  " 
            medium_place3name = "  " + db.get_user(self.leaderboard[1][2][0])[1].ljust(40) 
        except IndexError:
            medium_place3score = ""
            medium_place3name = ""

        medium_table = self._leaderboard.add.table(font_size=20, float=True)
        medium_table.default_cell_padding = 7
        medium_table.default_cell_align = pgm.locals.ALIGN_LEFT
        medium_table.default_row_background_color = (0,0,0,0)
        medium_table.add_row([medium_place1score, medium_place1name], cell_font=TEXT_FONT_BOLD, cell_border_width=0)
        medium_table.add_row([medium_place2score, medium_place2name], cell_font=TEXT_FONT_BOLD, cell_border_width=0)
        medium_table.add_row([medium_place3score, medium_place3name], cell_font=TEXT_FONT_BOLD, cell_border_width=0)
        medium_table.translate(8,-17)

        try:
            hard_place1score = "  " + "{:03d}".format(self.leaderboard[2][0][1]) + "  "
            hard_place1name = "  " + db.get_user(self.leaderboard[2][0][0])[1].ljust(40)
        except IndexError:
            hard_place1score = ""
            hard_place1name = ""
        try:
            hard_place2score = "  " + "{:03d}".format(self.leaderboard[2][1][1]) + "  "
            hard_place2name = "  " + db.get_user(self.leaderboard[2][1][0])[1].ljust(40)
        except IndexError:
            hard_place2score = ""
            hard_place2name = ""
        try:
            hard_place3score = "  " + "{:03d}".format(self.leaderboard[2][2][1]) + "  "
            hard_place3name = "  " + db.get_user(self.leaderboard[2][2][0])[1].ljust(40)
        except IndexError:
            hard_place3score = ""
            hard_place3name = ""

        hard_table = self._leaderboard.add.table(font_size=20, float=True)
        hard_table.default_cell_padding = 7
        hard_table.default_cell_align = pgm.locals.ALIGN_LEFT
        hard_table.default_row_background_color = (0,0,0,0)
        hard_table.add_row([hard_place1score, hard_place1name], cell_font=TEXT_FONT_BOLD, cell_border_width=0)
        hard_table.add_row([hard_place2score, hard_place2name], cell_font=TEXT_FONT_BOLD, cell_border_width=0)
        hard_table.add_row([hard_place3score, hard_place3name], cell_font=TEXT_FONT_BOLD, cell_border_width=0)
        hard_table.translate(8,123)


    def prompt(self, result: bool):
        """
        Display the user's current score and high score when the game is won or lost.

        This function sets the game state to finished and displays the user's score and
        high score in the prompt menu.

        Args:
            result (bool): True if the user has won, False if the user has lost

        Returns:
            None
        """
        self._playing = False
        score = "{:03d}".format(self._timer)
        highscore = "{:03d}".format(db.get_highscore(self._difficultyNum, USER_ID)[0] or 0)

        self._finished = True

        scoreText = self._prompt.add.label(
            score,
            max_char=-1,
            font_name=pgm.font.FONT_FIRACODE_BOLD,
            font_size=22,
            font_color=COLOUR_WHITE,
            align=pgm.locals.ALIGN_LEFT
        )
        scoreText.translate(69, 28)

        highscoreText = self._prompt.add.label(
            highscore,
            max_char=-1,
            font_name=pgm.font.FONT_FIRACODE_BOLD,
            font_size=22,
            font_color=COLOUR_WHITE,
            align=pgm.locals.ALIGN_RIGHT
        )
        highscoreText.translate(-69, 28)


    def update_gui(self, events):
        """
        Update and draw the main interface excluding the grid, and handle non-pygame-menu images.

        This function updates and draws the main game interface, including elements like
        flags, timers, and icons. It also handles drawing images that are not part of
        the pygame-menu system.

        Args:
            events (event): Pygame events such as user inputs and click coordinates

        Returns:
            None
        """
        self._menu.update(events)
        self._menu.draw(screen)

        if self._finished:
            self._prompt.update(events)
            self._prompt.draw(screen)

        certificate_img = pg.image.load(CERTIFICATE_ICON)
        screen.blit(certificate_img, (620, 16))

        flag_img = pg.image.load(FLAG_ICON)
        flag_img = pg.transform.smoothscale(flag_img, (50, 50))
        flag_img_rect = flag_img.get_rect(center=((TILE_SIZE * self._gridWidth) // 2 - 120, TAB_SIZE // 2))
        screen.blit(flag_img, flag_img_rect)

        flag_count = numberFont.render(str(self._flagCount).zfill(1), True, COLOUR_WHITE)
        flag_count_rect = flag_count.get_rect(midleft=((TILE_SIZE * self._gridWidth) // 2 - 85, TAB_SIZE // 2))
        screen.blit(flag_count, flag_count_rect)

        clock_img = pg.image.load(CLOCK_ICON)
        clock_img = pg.transform.smoothscale(clock_img, (50, 50))
        clock_img_rect = clock_img.get_rect(center=((TILE_SIZE * self._gridWidth) // 2 + 90, TAB_SIZE // 2))
        screen.blit(clock_img, clock_img_rect)

        timer_value = numberFont.render(str(self._timer).zfill(3), True, COLOUR_WHITE)
        timer_value_rect = timer_value.get_rect(midleft=((TILE_SIZE * self._gridWidth) // 2 + 120, TAB_SIZE // 2))
        screen.blit(timer_value, timer_value_rect)
    

    def setup_grid(self):
        """
        Initialize the game grid.

        This function creates an empty matrix based on the size of the grid and initializes
        Tile objects at each coordinate.

        Args:
            None

        Returns:
            None
        """
        self.grid = [[Tile(row, column) for column in range(self._gridWidth)] for row in range(self._gridHeight)]


    def draw_grid(self):
        """
        Draw the grid, updating only changed tiles.

        This function handles the drawing of the grid. It iterates through the grid and 
        draws only the tiles that have changed since the last drawing by checking the 
        `update` attribute.

        Args:
            None

        Returns:
            None
        """
        for row in self.grid:
            for tile in row:
                if tile.update:
                    tile.draw()
                    tile.update = False

    def reveal_tiles(self, gridY, gridX):
        """
        This function allows for the 'cluster reveal' effect that causes a section of
        tiles to be revealed at once when the user clicks on an empty collection of
        tiles.

        Args:
            gridY (int): The y-axis coordinate for the location of the tile to reveal around
            gridX (int): The x-axis coordinate for the location of the tile to reveal around

        Return:
            None
        """
        def is_valid(y, x):
            return 0 <= y < len(self.grid) and 0 <= x < len(self.grid[0])

        tile = self.grid[gridY][gridX]

        if not tile.clicked:
            self._unknownTileCount -= 1

        tile.flag = False
        tile.clicked = True
        tile.update = True

        if tile.count == 0 and not tile.mine:
            for j in range(-1, 2):
                for i in range(-1, 2):
                    if i == 0 and j == 0:
                        continue  # Skip the current tile
                    if is_valid(gridY + j, gridX + i):
                        neighbor_tile = self.grid[gridY + j][gridX + i]
                        if not neighbor_tile.clicked:
                            self.reveal_tiles(gridY + j, gridX + i)

        elif tile.mine:
            for y in range(self._gridHeight):
                for x in range(self._gridWidth):
                    if self.grid[y][x].mine:
                        self.grid[y][x].clicked = True
                        self.grid[y][x].update = True


    def generate_grid(self, gridY, gridX):
        """
        Generate a random game board with mines and initial tile clicks based on game difficulty.

        This function generates a random game board with mines placed in different locations.
        The initial click coordinates are used to prevent mines from being placed where the
        user first clicks, ensuring that the game starts fairly. Cluster checks are performed
        to avoid placing more than four mines in any 3x3 grid in the matrix, making the game
        mathematically solvable without the user having to guess.
        
        Args:

        Return:
            None
        """

        # This is for debugging purposes.
        if self._seed != 0:
            random.seed(self._seed)

        def check_cluster_count(y, x):
            count = 0
            for j in range(max(-1, -y), min(2, len(self.grid) - y)):
                for i in range(max(-1, -x), min(2, len(self.grid[0]) - x)):
                    if self.grid[y + j][x + i].mine:
                        count += 1
            return count

        for j in range(max(-1, -gridY), min(2, len(self.grid) - gridY)):
            for i in range(max(-1, -gridX), min(2, len(self.grid[0]) - gridX)):
                self.grid[gridY + j][gridX + i].clicked = True

        currentMineCount = 0
        while currentMineCount < self._mineCount:
            self.gridX = random.randint(0, self._gridWidth - 1)
            self.gridY = random.randint(0, self._gridHeight - 1)

            if self.grid[self.gridY][self.gridX].clicked or self.grid[self.gridY][self.gridX].mine:
                continue

            clusterCount = check_cluster_count(self.gridY, self.gridX)

            if clusterCount > 3:
                continue

            self.grid[self.gridY][self.gridX].mine = True
            for j in range(max(-1, -self.gridY), min(2, len(self.grid) - self.gridY)):
                for i in range(max(-1, -self.gridX), min(2, len(self.grid[0]) - self.gridX)):
                    if not (j == 0 and i == 0):
                        neighbor_tile = self.grid[self.gridY + j][self.gridX + i]
                        if not neighbor_tile.mine:
                            neighbor_tile.count += 1
            currentMineCount += 1

        for j in range(max(-1, -gridY), min(2, len(self.grid) - gridY)):
            for i in range(max(-1, -gridX), min(2, len(self.grid[0]) - gridX)):
                self.grid[gridY + j][gridX + i].clicked = False

        for y in range(self._gridHeight):
            for x in range(self._gridWidth):
                self.grid[y][x].update = True


    def mainLoop(self):
        """
        Main game loop that handles the constant updating of the interface and user inputs.

        Args:
            None
        
        Returns:
            None
        """

        pg.time.set_timer(pg.USEREVENT, 1000)
        grid_clickable = True

        while True:
            current_menu = self._menu.get_current()
            current_menu_id = current_menu.get_id()
            
            if current_menu_id == "settings_menu_instance" or current_menu_id == "leaderboard_menu_instance":
                grid_clickable = False
            elif current_menu_id == "home_menu_instance":
                grid_clickable = True
            
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    exit()

                if self._gamestart and self._playing and grid_clickable and event.type == pg.USEREVENT:
                    self._timer += 1

                elif event.type == pg.MOUSEBUTTONDOWN and grid_clickable:
                    if event.pos[1] >= 100:
                        y = int((event.pos[1] - 100) // TILE_SIZE)
                        x = int(event.pos[0] // TILE_SIZE)

                        if y < self._gridHeight and x < self._gridWidth and not self._gamestart:
                            self._gamestart = True

                        tile = self.grid[y][x]

                        try:
                            if tile:
                                if self._unknownTileCount == self._gridWidth * self._gridHeight:
                                    self.generate_grid(y, x)
                                    self.reveal_tiles(y, x)

                                if self._playing:
                                    if event.button == 1 and not tile.flag:
                                        self.reveal_tiles(y, x)

                                        if tile.mine:
                                            self.prompt(False)

                                        if self._unknownTileCount - 1 == self._mineCount:
                                            self.prompt(True)

                                    elif event.button == 3 and not tile.clicked:
                                        if not tile.flag and self._flagCount > 0:
                                            tile.update = True
                                            tile.flag = True
                                            self._flagCount -= 1
                                        elif tile.flag:
                                            tile.update = True
                                            tile.flag = False
                                            self._flagCount += 1

                        except IndexError:
                            pass

            self.draw_grid()
            self.update_gui(events)
            pg.display.flip()


if __name__ == "__main__":
    App = MinesweeperApp()
    App.mainLoop()