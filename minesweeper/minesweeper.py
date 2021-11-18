import pygame as pg
import random
from config import *

pg.init()
font = pg.font.Font(FONT, FONTSIZE)
flagImg = pg.image.load(FLAGICON)


def displayNumber(number, yPos, xPos):
    colour = COLOUR_WHITE
    if number == 1:
        colour = COLOUR_BLUE
    elif number == 2:
        colour = COLOUR_GREEN
    elif number == 3:
        colour = COLOUR_RED
    elif number == 4:
        colour = COLOUR_PURPLE
    elif number == -1:
        number = "•"
        colour = COLOUR_BLACK

    number = str(number)
    number = font.render(number, True, colour)

    yCenter = ((yPos*TILE_SIZE) - 5) + 6
    xCenter = (xPos*TILE_SIZE) + 12

    returnString = (pg.transform.scale(number, (20, 40)), (xCenter, yCenter))

    return returnString


class Tile(pg.sprite.DirtySprite):

    def __init__(self, position):
        super().__init__()
        self.image = pg.Surface((TILE_SIZE, TILE_SIZE))
        self.position = position

        if (((position[1]//TILE_SIZE)+1) % 2 == 0) ^ (((position[0]//TILE_SIZE)+1) % 2 == 0):
            self.colour = TILE_GREEN2
        else:
            self.colour = TILE_GREEN1

        self.image.fill(self.colour)
        self.rect = self.image.get_rect(topleft=position)

    def reveal(self):
        if (((self.position[1]//TILE_SIZE)+1) % 2 == 0) ^ (((self.position[0]//TILE_SIZE)+1) % 2 == 0):
            colour = TILE_BROWN2
        else:
            colour = TILE_BROWN1
        self.image.fill(colour)


class Grid():

    def __init__(self, seed, gridWidth, gridHeight, mineCount):
        self.seed = seed
        self.gridWidth = gridWidth
        self.gridHeight = gridHeight
        self.mineCount = mineCount

        self.tileValues = [[0 for column in range(self.gridWidth)] for row in range(self.gridHeight)]
        self.tileStatus = [[0 for column in range(self.gridWidth)] for row in range(self.gridHeight)]
        self.showNumbers = []

    def generate(self, xGrid, yGrid):

        if self.seed != 0:
            random.seed(self.seed)

        for j in range(-1, 2):
            if (0 <= (yGrid + j) < len(self.tileValues)):
                for i in range(-1, 2):
                    if (0 <= (xGrid + i) < len(self.tileValues[0])):
                        self.tileStatus[yGrid + j][xGrid + i] = 1

        currentMineCount = 0
        while currentMineCount < self.mineCount:
            clusterCount = 0
            xPos = random.randint(0, self.gridWidth - 1)
            yPos = random.randint(0, self.gridHeight - 1)

            if self.tileStatus[yPos][xPos] == 1:
                continue

            if self.tileValues[yPos][xPos] == -1:
                continue

            for j in range(-1, 2):
                if (0 <= (yPos + j) < len(self.tileValues)):
                    for i in range(-1, 2):
                        if (0 <= (xPos + i) < len(self.tileValues[0])):
                            if self.tileValues[yPos + j][xPos + i] == -1:
                                clusterCount += 1
                            if self.tileStatus[yPos + j][xPos + i] == 1:
                                continue

            if clusterCount > 3:
                continue

            else:
                self.tileValues[yPos][xPos] = -1
                for j in range(-1, 2):
                    if (0 <= (yPos + j) < len(self.tileValues)):
                        for i in range(-1, 2):
                            if (0 <= (xPos + i) < len(self.tileValues[0])):
                                if not ((j == 0) and (i == 0)):
                                    if self.tileValues[yPos + j][xPos + i] != -1:
                                        self.tileValues[yPos + j][xPos + i] += 1
                currentMineCount += 1

        for j in range(-1, 2):
            if (0 <= (yGrid + j) < len(self.tileValues)):
                for i in range(-1, 2):
                    if (0 <= (xGrid + i) < len(self.tileValues[0])):
                        if not ((j == 0) and (i == 0)):
                            self.tileStatus[yGrid + j][xGrid + i] = 0

    def draw(self):
        global all_sprites
        all_sprites = pg.sprite.Group()

        # Create the tiles and add them to the all_sprites group.
        for y in range(self.gridHeight):
            for x in range(self.gridWidth):
                position = (x*(TILE_SIZE), y*(TILE_SIZE))
                all_sprites.add(Tile(position))

    def update(self):
        for y in range(self.gridHeight):
            for x in range(self.gridWidth):
                if (self.tileStatus[y][x] == 1) and (self.tileValues[y][x] > 0):
                    number = (displayNumber(self.tileValues[y][x], y, x))
                    self.showNumbers.append(number)


def main():

    board = Grid(17, 18, 14, 40)
    board.generate(1, 1)

    clock = pg.time.Clock()
    flags = pg.RESIZABLE | pg.SCALED | pg.HWSURFACE | pg.DOUBLEBUF
    screen = pg.display.set_mode(((TILE_SIZE) * board.gridWidth, (TILE_SIZE) * board.gridHeight), flags)
    done = False

    board.draw()

    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            # If a mouse button was pressed.
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Iterate over the sprites in the group.
                    for sprite in all_sprites:
                        # Check if the sprite's rect collides with the mouse pos.
                        if sprite.rect.collidepoint(event.pos):
                            print(event.pos[0] // TILE_SIZE, event.pos[1] // TILE_SIZE)
                            # Finally change the colour.
                            sprite.reveal()
                            board.tileStatus[event.pos[1] // TILE_SIZE][event.pos[0] // TILE_SIZE] = 1

        all_sprites.update()
        screen.fill(COLOUR_BORDER)
        all_sprites.draw(screen)
        board.update()
        screen.blits(board.showNumbers)

        newImg = pg.transform.scale(flagImg, (20, 40)), (20, 20)
        screen.blit(flagImg, (10, 10))

        pg.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
