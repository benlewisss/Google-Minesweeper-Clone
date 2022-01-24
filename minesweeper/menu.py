import pygame as pg
import pygame_menu as pgm
from config import *
import random

print("\033c")

pg.init()
screen = pg.display.set_mode((1080, 1080))
textFont = pg.font.Font(TEXT_FONT, 15)

mineColours = [MINE_BLUE, MINE_CYAN, MINE_MAGENTA, MINE_ORANGE, MINE_PURPLE, MINE_RED, MINE_YELLOW]
numbers = [NUMBER_1, NUMBER_2, NUMBER_3, NUMBER_4]

settingsMenuImage = pgm.baseimage.BaseImage(
    image_path=SETTINGSMENU,
    drawing_mode=pgm.baseimage.IMAGE_MODE_SIMPLE)

def set_constant(tileSize):
    global TILE_SIZE
    TILE_SIZE = tileSize


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
    _menu: "pgm.Menu"
    _gridWidth: int
    _gridHeight: int
    _mineCount: int
    _tileSize: int
    _difficultyName: str

    def __init__(self):
        self.setup_menus()
        self.setup_grid()

    def setup_menus(self):

        def difficulty_select(item: tuple, value: int):
            if value == 0:
                self._difficultyName = "EASY"
                self._gridWidth = 10
                self._gridHeight = 8
                self._mineCount = 10
                self._tileSize = 108

            elif value == 1:
                self._difficultyName = "MEDIUM"
                self._gridWidth = 18
                self._gridHeight = 14
                self._mineCount = 40
                self._tileSize = 60

            elif value == 2:
                self._difficultyName = "HARD"
                self._gridWidth = 24
                self._gridHeight = 20
                self._mineCount = 99
                self._tileSize = 45

            set_constant(self._tileSize)
        
        difficulty_select(None, 1)

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
        

        self._menu = pgm.Menu(
            height=100,
            mouse_motion_selection=True,
            position=(0, 0, False),
            columns=10,
            rows=10,
            theme=homeTheme,
            title="",
            width=1080
        )

        settings_menu = pgm.Menu(
            width=480, 
            height=800,
            columns=1,
            rows=10,
            mouse_motion_selection=True,
            position=(300, 140, False),
            theme=settingsTheme,
            title=""
        )

        btn = settings_menu.add.button(
            "  ",
            pgm.events.BACK,
            button_id="settings_back",
            align=pgm.locals.ALIGN_LEFT,
            float=True,
            font_size=25,
            cursor=pgm.locals.CURSOR_HAND,
            selection_effect=pgm.widgets.NoneSelection(),
            margin=(40,40)
        )
        btn.translate(-25,-392)

        btn = settings_menu.add.dropselect(
            title="",
            items=[("Easy", 0),
                   ("Medium", 1),
                   ("Hard", 2)],
            dropselect_id="difficulty",
            default=1,
            font_size=16,
            onchange=difficulty_select,
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
        
        btn = self._menu.add.button(
            "  ",
            settings_menu,
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

    def update_gui(self, events):
        gameArea = pg.Surface((1080, 980))
        gameArea.fill(COLOUR_BLACK)
        #screen.blit(gameArea, [0,100])
        self._menu.update(events)
        self._menu.draw(screen)
    
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

    def mainLoop(self):
        while True:
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    exit()

                elif event.type == pg.MOUSEBUTTONDOWN:
                    print(self._difficultyName)
                    
            self.draw_grid()
            self.update_gui(events)
            pg.display.update()


App = MinesweeperApp()
App.mainLoop()