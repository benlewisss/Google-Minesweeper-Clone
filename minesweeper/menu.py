import pygame as pg
import pygame_menu as pgm
import config
from config import *
import datetime
import random
import database

print("\033c")

USER_ID=1

db = database.Database("data/database.sqlite")
print("\nAll Data:")
db.get_all_data()
print("\n")

resolution = 720

pg.init()
screen = pg.display.set_mode((resolution, resolution))
textFont = pg.font.Font(TEXT_FONT, 15)
numberFont = pg.font.Font(NUMBER_FONT, 35)

mineColours = [MINE_BLUE, MINE_CYAN, MINE_MAGENTA, MINE_ORANGE, MINE_PURPLE, MINE_RED, MINE_YELLOW]
numbers = [NUMBER_1, NUMBER_2, NUMBER_3, NUMBER_4]

settingsMenuImage = pgm.baseimage.BaseImage(
    image_path=SETTINGSMENU,
    drawing_mode=pgm.baseimage.IMAGE_MODE_SIMPLE)

leaderboardMenuImage = pgm.baseimage.BaseImage(
    image_path=SETTINGSMENU,
    drawing_mode=pgm.baseimage.IMAGE_MODE_SIMPLE)

promptImage = pgm.baseimage.BaseImage(
    image_path=PROMPT,
    drawing_mode=pgm.baseimage.IMAGE_MODE_SIMPLE)

def tilesize_set_constant(tileSize):
    global TILE_SIZE
    TILE_SIZE = tileSize 

def user_set_constant(username):
    global USER_ID
    USER_ID = db.create_user(username)

def check_name_test(value: str):
    """
    This function tests the text input widget.
    :param value: The widget value
    """
    print(f'User name: {value}')


class Tile(pg.sprite.DirtySprite):

    def __init__(self, gridY, gridX):
        super().__init__()
        self.gridY = gridY
        self.gridX = gridX
        self.clicked = False
        self.mine = False
        self.flag = False
        self.update = True
        self.mineColour = random.choice(mineColours)
        self.count = 0
        self.pixelPosition = (gridX*TILE_SIZE, (gridY*TILE_SIZE) + 100)
        
    def draw(self):

        if self.flag == True:
            flagImg = pg.image.load(FLAGICON)
            self.image = pg.transform.smoothscale(flagImg, (TILE_SIZE, TILE_SIZE))

        elif (self.clicked == True) and (self.mine == True) and (self.flag == False):
            mineImg = pg.image.load(self.mineColour)
            self.image = pg.transform.smoothscale(mineImg, (TILE_SIZE, TILE_SIZE))

        else:
            if self.clicked == True:
                if ((self.gridY % 2 == 0) ^ (self.gridX % 2 == 0)):
                    colour = TILE_BROWN1
                else:
                    colour = TILE_BROWN2

            elif self.clicked == False:
                if ((self.gridY % 2 == 0) ^ (self.gridX % 2 == 0)):
                    colour = TILE_GREEN2
                else:
                    colour = TILE_GREEN1

            self.image = pg.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill(colour)

        self.image.get_rect(topleft=self.pixelPosition)
        screen.blit(self.image, self.pixelPosition)

        if (self.mine == False) and (self.flag == False) and (self.clicked == True) and (self.count > 0):
            if self.count == 1:
             index = 0
            elif self.count == 2:
             index = 1
            elif self.count == 3:
             index = 2
            elif self.count == 4:
             index = 3

            numImg = pg.image.load(numbers[index])
            self.image = pg.transform.scale(numImg, (TILE_SIZE, TILE_SIZE))
            self.image.get_rect(topleft=self.pixelPosition)
            screen.blit(self.image, self.pixelPosition)


class MinesweeperApp(object):
    _visualize: bool
    _playing: bool
    _finished: bool
    _gamestart: bool
    _menu: "pgm.Menu"
    _settings: "pgm.Menu"
    _leaderboard: "pgm.Menu"
    _prompt: "pgm.Menu"
    _gridWidth: int
    _gridHeight: int
    _mineCount: int
    _tileSize: int
    _seed: int
    _unknownTileCount: int
    _timer: int
    _flagCount: int
    _difficultyNum: int
    _difficultyName: str

    def __init__(self):
        self._seed = 17
        self._gamestart = False
        self._playing = True
        self._finished = False
        self._timer = 0
        self._difficultyNum = 1
        self.difficulty_select(None, self._difficultyNum)
        self.setup_menus()
        self.setup_grid()
        self._unknownTileCount=self._gridWidth*self._gridHeight
        

    def difficulty_select(self, item: tuple, value: int):
        if value == 0:
            self._difficultyName = "EASY"
            self._gridWidth = 10
            self._gridHeight = 8
            self._mineCount = 10
            self._tileSize = int(resolution/10)

        elif value == 1:
            self._difficultyName = "MEDIUM"
            self._gridWidth = 18
            self._gridHeight = 14
            self._mineCount = 40
            self._tileSize = int(resolution/18)

        elif value == 2:
            self._difficultyName = "HARD"
            self._gridWidth = 24
            self._gridHeight = 20
            self._mineCount = 99
            self._tileSize = int(resolution/24)

        tilesize_set_constant(self._tileSize)
        self._unknownTileCount = self._gridWidth*self._gridHeight
        self._gamestart = False
        self._playing = True
        self._finished = False
        self._timer = 0
        self._flagCount = self._mineCount
        self._difficultyNum = value
        screen.fill(COLOUR_BORDER)
        self.setup_menus()
        self.setup_grid()

    def exit_menu(self):
        self.difficulty_select(None, self._difficultyNum)

    def check_name_test(self, value: str):
        """
        This function tests the text input widget.
        :param value: The widget value
        """
        user_set_constant(value)
        self.__init__()

    def setup_menus(self):

        # Configure homeTheme 
        homeTheme = pgm.Theme()
        homeTheme.background_color = COLOUR_BORDER
        homeTheme.title = False
        homeTheme.widget_alignment = pgm.locals.ALIGN_CENTER
        homeTheme.widget_background_color = None
        homeTheme.widget_font = pgm.font.FONT_FIRACODE_BOLD
        homeTheme.widget_font_color = (255, 255, 255)
        homeTheme.widget_font_size = 40
        homeTheme.widget_padding = 0
        homeTheme.widget_selection_effect = \
            pgm.widgets.HighlightSelection(1, 0, 0).set_color((120, 120, 120))

        # Configure settingsTheme
        settingsTheme = pgm.Theme()
        settingsTheme.background_color = settingsMenuImage
        settingsTheme.title_bar_style = pgm.widgets.MENUBAR_STYLE_NONE
        settingsTheme.title_close_button = False
        settingsTheme.title_font_size = 40
        settingsTheme.widget_alignment = pgm.locals.ALIGN_CENTER
        settingsTheme.widget_font = pgm.font.FONT_FIRACODE_BOLD
        settingsTheme.widget_font_color = (100, 12, 14)
        settingsTheme.widget_font_size = 40
        settingsTheme.widget_padding = 0

        # Configure leaderboardTheme
        leaderboardTheme = pgm.Theme()
        leaderboardTheme.background_color = leaderboardMenuImage
        leaderboardTheme.title_bar_style = pgm.widgets.MENUBAR_STYLE_NONE
        leaderboardTheme.title_close_button = False
        leaderboardTheme.title_font_size = 40
        leaderboardTheme.widget_alignment = pgm.locals.ALIGN_CENTER
        leaderboardTheme.widget_font = pgm.font.FONT_FIRACODE_BOLD
        leaderboardTheme.widget_font_color = (100, 12, 14)
        leaderboardTheme.widget_font_size = 40
        leaderboardTheme.widget_padding = 0

        # Configure promptTheme
        promptTheme = pgm.Theme()
        promptTheme.background_color = promptImage
        promptTheme.title_bar_style = pgm.widgets.MENUBAR_STYLE_NONE
        promptTheme.title_close_button = False
        promptTheme.title_font_size = 40
        promptTheme.widget_alignment = pgm.locals.ALIGN_CENTER
        promptTheme.widget_font = pgm.font.FONT_FIRACODE_BOLD
        promptTheme.widget_font_color = (100, 12, 14)
        promptTheme.widget_font_size = 40
        promptTheme.widget_padding = 0
        

        self._menu = pgm.Menu(
            menu_id="home_menu_instance",
            height=100,
            mouse_motion_selection=True,
            position=(0, 0, False),
            columns=10,
            rows=10,
            theme=homeTheme,
            title="",
            width=resolution
        )

        self._settings = pgm.Menu(
            menu_id="settings_menu_instance",
            width=320, 
            height=534,
            columns=1,
            rows=10,
            mouse_motion_selection=True,
            position=(200, 110, False),
            theme=settingsTheme,
            title=""
        )

        self._leaderboard = pgm.Menu(
            menu_id="settings_menu_instance",
            width=320, 
            height=534,
            columns=1,
            rows=10,
            mouse_motion_selection=True,
            position=(200, 110, False),
            theme=settingsTheme,
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
            theme=promptTheme,
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
            button_id="leaderboard_button",
            align=pgm.locals.ALIGN_CENTER,
            float=True,
            font_color=COLOUR_WHITE,
            font_size=35,
            cursor=pgm.locals.CURSOR_HAND,
            selection_effect=pgm.widgets.NoneSelection(),
            margin=(40,40)
        )
        btn.translate(-180,-270)

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
            margin=(40, 40)
        )
        btn.translate(2,0)

        self._menu.add.image(
            image_path=SETTINGSICON,
            image_id="settingsIcon",
            margin=(40,40),
            align=pgm.locals.ALIGN_LEFT,
            cursor=pg.SYSTEM_CURSOR_HAND,
            scale_smooth=True,
            scale=(0.06, 0.06)
        )

    def prompt(self, result:bool):
        self._playing = False
        score="{:03d}".format(self._timer)

        if result:
            db.submit_score(int(score), self._difficultyNum, USER_ID)

        highscore="{:03d}".format(db.get_highscore(USER_ID)[0])

        if result == True:
            self._finished = True

            scoreText = self._prompt.add.label(
            score, 
            max_char=-1, 
            font_name=pgm.font.FONT_FIRACODE_BOLD,
            font_size=22,
            font_color=COLOUR_WHITE, 
            align=pgm.locals.ALIGN_LEFT
            )
            scoreText.translate(69,28)

            highscoreText = self._prompt.add.label(
            highscore, 
            max_char=-1, 
            font_name=pgm.font.FONT_FIRACODE_BOLD,
            font_size=22,
            font_color=COLOUR_WHITE, 
            align=pgm.locals.ALIGN_RIGHT
            )     
            highscoreText.translate(-69,28)
        
        elif result == False:
            self._finished = True

            scoreText = self._prompt.add.label(
            "000", 
            max_char=-1, 
            font_name=pgm.font.FONT_FIRACODE_BOLD,
            font_size=22,
            font_color=COLOUR_WHITE, 
            align=pgm.locals.ALIGN_LEFT
            )
            scoreText.translate(69,28)

            highscoreText = self._prompt.add.label(
            highscore, 
            max_char=-1, 
            font_name=pgm.font.FONT_FIRACODE_BOLD,
            font_size=22,
            font_color=COLOUR_WHITE, 
            align=pgm.locals.ALIGN_RIGHT
            )     
            highscoreText.translate(-69,28)

    def update_gui(self, events):
        self._menu.update(events)
        self._menu.draw(screen)
        if self._finished == True:
            self._prompt.update(events)
            self._prompt.draw(screen)

        certificateImg = pg.image.load(CERTIFICATEICON)
        #certificateImgRect = certificateImg.get_rect(center=())
        screen.blit(certificateImg, (620,16))

        flagImg = pg.image.load(FLAGICON)
        flagImg = pg.transform.smoothscale(flagImg, (50, 50))
        flagImgRect = flagImg.get_rect(center=((TILE_SIZE*self._gridWidth)//2 - 120, TAB_SIZE//2))
        screen.blit(flagImg, flagImgRect)

        flagCount = numberFont.render(str(self._flagCount).zfill(1), True, COLOUR_WHITE)
        flagCountRect = flagCount.get_rect(midleft=((TILE_SIZE*self._gridWidth)//2 - 85, TAB_SIZE//2))
        screen.blit(flagCount, flagCountRect)
        
        clockImg = pg.image.load(CLOCKICON)
        clockImg = pg.transform.smoothscale(clockImg, (50, 50))
        clockImgRect = clockImg.get_rect(center=((TILE_SIZE*self._gridWidth)//2 + 90, TAB_SIZE//2))
        screen.blit(clockImg, clockImgRect)

        counter = numberFont.render(str(self._timer).zfill(3), True, COLOUR_WHITE)
        counterRect = counter.get_rect(midleft=((TILE_SIZE*self._gridWidth)//2 + 120, TAB_SIZE//2))
        screen.blit(counter, counterRect)
    
    def setup_grid(self):
        self.grid = [[0 for column in range(self._gridWidth)] for row in range(self._gridHeight)] 
        for y in range(self._gridHeight):
                for x in range(self._gridWidth):
                    self.grid[y][x] = Tile(y, x)

    def draw_grid(self):
        for y in range(self._gridHeight):
            for x in range(self._gridWidth):
                if self.grid[y][x].update == True:
                    self.grid[y][x].draw()
                    self.grid[y][x].update = False

    def reveal_tiles(self, gridY, gridX):
        if self.grid[gridY][gridX].clicked == False:
            self._unknownTileCount -= 1
        self.grid[gridY][gridX].flag = False
        self.grid[gridY][gridX].clicked = True
        self.grid[gridY][gridX].update = True

        if (self.grid[gridY][gridX].count == 0) and (self.grid[gridY][gridX].mine == False):
            for j in range(-1, 2):
                if (0 <= (gridY+j) < len(self.grid)):
                    for i in range(-1, 2):
                        if (0 <= (gridX+i) < len(self.grid[0])):
                            if not self.grid[gridY+j][gridX+i].clicked:
                                self.reveal_tiles(gridY+j, gridX+i)

        elif self.grid[gridY][gridX].mine == True:
            for y in range(self._gridHeight):
                for x in range(self._gridWidth):
                    if self.grid[y][x].mine == True:
                        self.grid[y][x].clicked = True
                        self.grid[y][x].update = True

    def generate_grid(self, gridY, gridX):
        if self._seed != 0:
            random.seed(self._seed)

        for j in range(-1, 2):
            if (0 <= (gridY + j) < len(self.grid)):
                for i in range(-1, 2):
                    if (0 <= (gridX + i) < len(self.grid[0])):
                        self.grid[gridY + j][gridX + i].clicked = True

        currentMineCount = 0
        while currentMineCount < self._mineCount:
            clusterCount = 0
            self.gridX = random.randint(0, self._gridWidth - 1)
            self.gridY = random.randint(0, self._gridHeight - 1)

            if self.grid[self.gridY][self.gridX].clicked == True:
                continue

            if self.grid[self.gridY][self.gridX].mine == True:
                continue

            for j in range(-1, 2):
                if (0 <= (self.gridY + j) < len(self.grid)):
                    for i in range(-1, 2):
                        if (0 <= (self.gridX + i) < len(self.grid[0])):
                            if self.grid[self.gridY + j][self.gridX + i].mine == True:
                                clusterCount += 1
                            if self.grid[self.gridY + j][self.gridX + i].clicked == True:
                                continue

            if clusterCount > 3:
                continue

            else:
                self.grid[self.gridY][self.gridX].mine = True
                for j in range(-1, 2):
                    if (0 <= (self.gridY + j) < len(self.grid)):
                        for i in range(-1, 2):
                            if (0 <= (self.gridX + i) < len(self.grid[0])):
                                if not ((j == 0) and (i == 0)):
                                    if self.grid[self.gridY + j][self.gridX + i].mine == False:
                                        self.grid[self.gridY + j][self.gridX + i].count += 1
                currentMineCount += 1

        for j in range(-1, 2):
            if (0 <= (gridY + j) < len(self.grid)):
                for i in range(-1, 2):
                    if (0 <= (gridX + i) < len(self.grid[0])):
                        if not ((j == 0) and (i == 0)):
                            self.grid[gridY + j][gridX + i].clicked = False

        for y in range(self._gridHeight):
            for x in range(self._gridWidth):
                self.grid[y][x].update = True


        

    def mainLoop(self):
        pg.time.set_timer(pg.USEREVENT, 1000)
        gridClickable = True
        while True:
            current_menu = self._menu.get_current()
            current_menu_id = current_menu.get_id()
            if current_menu_id == "settings_menu_instance":
                gridClickable = False
            if current_menu_id == "home_menu_instance":
                gridClickable = True
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    exit()
                
                if (self._gamestart == True) and (self._playing == True) and (gridClickable == True) and (event.type == pg.USEREVENT):
                    self._timer += 1
                    
                elif (event.type == pg.MOUSEBUTTONDOWN) and (gridClickable == True):
                    if event.pos[1] >= 100:
                        y = int((event.pos[1] - 100)//TILE_SIZE)
                        x = int(event.pos[0]//TILE_SIZE)

                        if (y < self._gridHeight) and (x < self._gridWidth) and (self._gamestart == False):
                            self._gamestart = True

                        try:
                            if self.grid[y][x]:
                                if self._unknownTileCount == (self._gridWidth*self._gridHeight):
                                    self.generate_grid(y,x)
                                    self.reveal_tiles(y,x)

                            if self._playing == True:
                                if (event.button == 1) and (self.grid[y][x].flag == False):
                                    self.reveal_tiles(y,x)

                                    if self.grid[y][x].mine == True:
                                        self.prompt(False)

                                    if self._unknownTileCount-1 == self._mineCount:
                                        self.prompt(True)

                                elif (event.button == 3) and (self.grid[y][x].clicked == False):
                                    if (self.grid[y][x].flag == False) and (self._flagCount > 0):
                                        self.grid[y][x].update = True
                                        self.grid[y][x].flag = True
                                        self._flagCount -= 1
                                    elif (self.grid[y][x].flag == True):
                                        self.grid[y][x].update = True
                                        self.grid[y][x].flag = False
                                        self._flagCount += 1


                        except IndexError:
                            pass
        
            self.draw_grid()
            self.update_gui(events)
            pg.display.update()


App = MinesweeperApp()
App.mainLoop()