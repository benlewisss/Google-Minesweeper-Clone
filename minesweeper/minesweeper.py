import pygame as pg
from pygame import gfxdraw
import random
from config import *

pg.init()

mainFont = pg.font.Font(MAIN_FONT, MAIN_FONT_SIZE)
textFont = pg.font.Font(TEXT_FONT, TEXT_FONT_SIZE)
numberFont = pg.font.Font(NUMBER_FONT, NUMBER_FONT_SIZE)

mineColours = [MINE_BLUE, MINE_CYAN, MINE_MAGENTA, MINE_ORANGE, MINE_PURPLE, MINE_RED, MINE_YELLOW]
numbers = [NUMBER_1, NUMBER_2, NUMBER_3, NUMBER_4]

displayInfo = pg.display.Info()
displayResolution = (displayInfo.current_w, displayInfo.current_h)
print(displayResolution)

difficulty = "Easy"

if difficulty == "Easy":
    gridWidth = 10
    gridHeight = 8
    mineCount = 10
    TILE_SIZE = 80

elif difficulty == "Medium":
    gridWidth = 18
    gridHeight = 14
    mineCount = 40
    TILE_SIZE = 60

elif difficulty == "Hard":
    gridWidth = 24
    gridHeight = 20
    mineCount = 99
    TILE_SIZE = 40


flags = pg.HWSURFACE | pg.DOUBLEBUF
screen = pg.display.set_mode((TILE_SIZE * gridWidth, (TILE_SIZE * gridHeight) + TAB_SIZE), flags)


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
        self.pixelPosition = (gridX*TILE_SIZE, (gridY*TILE_SIZE) + TAB_SIZE)
        
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


    def reveal(self):
        if self.clicked == False:
            Grid.unknownTileCount -= 1
        self.flag = False
        self.clicked = True
        self.update = True

        if (self.count == 0) and (self.mine == False):
            for j in range(-1, 2):
                if (0 <= (self.gridY+j) < len(Grid.grid)):
                    for i in range(-1, 2):
                        if (0 <= (self.gridX+i) < len(Grid.grid[0])):
                            if not Grid.grid[self.gridY+j][self.gridX+i].clicked:
                                Grid.grid[self.gridY+j][self.gridX+i].reveal()

        elif self.mine == True:
            for y in range(gridHeight):
                for x in range(gridWidth):
                    if Grid.grid[y][x].mine == True:
                        Grid.grid[y][x].clicked = True
                        Grid.grid[y][x].update = True


class Grid():
    def __init__(self, seed=0):
        self.seed = seed
        Grid.grid = [[0 for column in range(gridWidth)] for row in range(gridHeight)]
        Grid.unknownTileCount = gridWidth*gridHeight
        
    def initiate(self):
        for y in range(gridHeight):
                for x in range(gridWidth):
                    self.grid[y][x] = Tile(y, x)

    def generate(self, gridY, gridX):

        if self.seed != 0:
            random.seed(self.seed)

        for j in range(-1, 2):
            if (0 <= (gridY + j) < len(self.grid)):
                for i in range(-1, 2):
                    if (0 <= (gridX + i) < len(self.grid[0])):
                        self.grid[gridY + j][gridX + i].clicked = True

        currentMineCount = 0
        while currentMineCount < mineCount:
            clusterCount = 0
            self.gridX = random.randint(0, gridWidth - 1)
            self.gridY = random.randint(0, gridHeight - 1)

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


    def draw(self):
        for y in range(gridHeight):
            for x in range(gridWidth):
                if self.grid[y][x].update == True:
                    self.grid[y][x].draw()
                    self.grid[y][x].update = False

  
class Tab():
    def __init__(self):
        self.elapsedTime = 0

    def draw(self, elapsedTime, remainingFlags):
        self.elapsedTime = elapsedTime

        tabRect = pg.Rect(0, 0, gridWidth*TILE_SIZE, TAB_SIZE)
        pg.draw.rect(screen, COLOUR_TAB, tabRect)

        difficultyBox = pg.Rect(25, 25, 200, TAB_SIZE//2)
        pg.draw.rect(screen, COLOUR_WHITE, difficultyBox, border_radius=10)
        
        difficultyText = textFont.render(difficulty, True, COLOUR_BLACK)
        difficultyTextRect = difficultyText.get_rect(center=(125, TAB_SIZE//2 + 2))
        screen.blit(difficultyText, difficultyTextRect)


        flagImg = pg.image.load(FLAGICON)
        flagImg = pg.transform.smoothscale(flagImg, (70, 70))
        flagImgRect = flagImg.get_rect(center=((TILE_SIZE*gridWidth)//2 - 120, TAB_SIZE//2))
        screen.blit(flagImg, flagImgRect)

        flagCount = numberFont.render(str(remainingFlags).zfill(1), True, COLOUR_WHITE)
        flagCountRect = flagCount.get_rect(midleft=((TILE_SIZE*gridWidth)//2 - 85, TAB_SIZE//2))
        screen.blit(flagCount, flagCountRect)

        clockImg = pg.image.load(CLOCKICON)
        clockImg = pg.transform.smoothscale(clockImg, (60, 60))
        clockImgRect = clockImg.get_rect(center=((TILE_SIZE*gridWidth)//2 + 40, TAB_SIZE//2))
        screen.blit(clockImg, clockImgRect)

        counter = numberFont.render(str(self.elapsedTime).zfill(3), True, COLOUR_WHITE)
        counterRect = counter.get_rect(midleft=((TILE_SIZE*gridWidth)//2 + 80, TAB_SIZE//2))
        screen.blit(counter, counterRect)



def main():
    clock = pg.time.Clock()
    
    done = False
    
    board = Grid(17)
    board.initiate()

    tab = Tab()

    pg.time.set_timer(pg.USEREVENT, 1000)
    counter = 0
    flagCount = mineCount

    initialRun = True
    playing = True
    
    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True

            if (event.type == pg.USEREVENT) and (initialRun == False) and (playing == True):
                counter += 1
    
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.pos[1] <= TAB_SIZE:
                    y = event.pos[1]
                    x = event.pos[0]
                else:
                    y = (event.pos[1] - TAB_SIZE)//TILE_SIZE
                    x = event.pos[0]//TILE_SIZE
                    board.grid[y][x].update = True

                    if initialRun == True:
                        board.generate(y, x)
                        board.grid[y][x].reveal()
                        initialRun = False

                    elif playing == True:
                        if (event.button == 1) and (board.grid[y][x].flag == False):
                            board.grid[y][x].reveal()
                            print(Grid.unknownTileCount)

                            if board.grid[y][x].mine == True:
                                playing = False
                                print("You died!")

                            if Grid.unknownTileCount == mineCount:
                                playing = False
                                print("You win!")

                        elif (event.button == 3) and (board.grid[y][x].clicked == False):
                            if (board.grid[y][x].flag == False) and (flagCount > 0):
                                board.grid[y][x].flag = True
                                flagCount -= 1
                            elif (board.grid[y][x].flag == True):
                                board.grid[y][x].flag = False
                                flagCount += 1
                                

        tab.draw(counter, flagCount)
        board.draw()
        pg.display.flip()


    clock.tick(30) 



if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
