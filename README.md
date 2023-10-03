# Minesweeper Program Documentation

This documentation provides a detailed explanation of my Minesweeper program, a clone of the Google Minesweeper game. The program is implemented in Python using the Pygame library. It includes various features such as customizable difficulty levels, a timer, a flag counter, and a user leaderboard, just like the actual Google game.

This project was originally an A-Level NEA (*UK High School CS Project*), and it has been revisited and touched up with some better documentation, code readability, PEP8 conformation, and a few optimisations.

## Table of Contents

1. [Introduction](#1-introduction)
2. [Installation](#2-installation)
3. [Getting Started](#3-getting-started)
4. [Program Structure](#4-program-structure)
   * [Imported Libraries](#imported-libraries)
   * [Global Constants](#global-constants)
   * [Database Initialization](#database-initialization)
   * [Tile Class](#tile-class)
   * [MinesweeperApp Class](#minesweeperapp-class)
5. [Gameplay](#5-gameplay)
   * [Difficulty Selection](#difficulty-selection)
   * [Exiting Menus](#exiting-menus)
   * [Changing User](#changing-user)
   * [Grid Setup](#grid-setup)
   * [Drawing the Grid](#drawing-the-grid)
   * [Revealing Tiles](#revealing-tiles)
   * [Generating the Grid](#generating-the-grid)
   * [Main Game Loop](#main-game-loop)
6. [Major Issues](#6-issues)
7. [Contributors](#7-contributors)

## 1. Introduction

The Minesweeper program is a Python implementation of the classic Minesweeper game. It offers customizable difficulty levels, a timer, a flag counter, and a leaderboard feature. The game is played on a grid of tiles, some of which contain hidden mines. The player's goal is to reveal all tiles that do not contain mines without triggering any mines.

This implementation is a Python clone of Googles very clean implementation. Although Googles was achieved using JavaScript, this project fully uses Python.

It was never fully completed, but I decided to revisit it and give it a facelift. There are still a few remaining bugs, but it is playable and the database system works locally.

The fact this was made in Python presented many challenges, the main of which being it is hard to write optimised code for GUIs as there is a very limited selection of libraries, as well as the fact that PyGame is now deprecated.

## 2. Installation

To get started, ensure you have the necessary libraries installed. The only non-standard library this program uses is Pygame and Pygame-menu, which can be installed with the following ***pip*** commands:

```
pip install -U pygame --user
pip install -U pygame_menu --user
```

## 3. Getting Started

To start the Minesweeper game, run the program using Python:

`python minesweeper.py`

Upon launching the game, click the settings icon in the top left to show a menu that allows you to select a difficulty level and enter a username. After making your selections, close the settings menu.

## 4. Program Structure

The Minesweeper program consists of several components and classes:

### Imported Libraries

The program imports the following Python libraries:

* `os`: Used for clearing the terminal (for debugging).
* `random`: Used for randomizing mine placement.
* `pygame` and `pygame_menu`: Main libraries for game development and menu creation.
* `config`: Imports various constants and file paths.
* `database`: Manages user data and leaderboard entries.

### Global Constants

* `TILE_SIZE`: The size of each tile, determined by the selected difficulty.
* `USER_ID`: The ID of the current user (default is 1).
* `mineColours`, `numbers`: Lists of mine colors and number images.
* Constants for menu images and fonts.

### Database Initialization

The program initializes a SQLite database using the `database` module. It creates tables and a default user ("Guest").

### Tile Class

The `Tile` class represents each tile on the game grid. It has attributes such as position, mine status, click status, flag status, and count (number of neighboring mines). Tiles are responsible for rendering themselves on the screen using Pygame functions.

### MinesweeperApp Class

The `MinesweeperApp` class manages the core game logic. It handles difficulty selection, user interaction, grid generation, and gameplay mechanics. The game loop continually updates and draws the game interface, responding to user events.

## 5. Gameplay

### Difficulty Selection

Players can select from three difficulty levels: Easy, Medium, and Hard. Each difficulty level specifies the grid size, mine count, and tile size. Difficulty settings are defined in the `difficulties` list, and the `difficulty_select` method initializes the game with the chosen settings.

### Changing User

Players can enter their username, which is then stored in the database. The `check_name_test` method updates the global user ID and reinitializes the game with the new user settings, and allows for highscores to be stored in a leaderboard for comparison againsts other users.

### Grid Setup

The game grid is initialized using the `setup_grid` method, creating a matrix of `Tile` objects based on the selected difficulty.

### Drawing the Grid

The `draw_grid` method updates and draws the game grid. It optimizes drawing to reduce unnecessary operations by checking the `update` attribute of each tile.

### Revealing Tiles

The `reveal_tiles` method enables the "cluster reveal" effect, revealing adjacent empty tiles when a tile with no neighboring mines is clicked. This function recursively reveals tiles.

### Generating the Grid

The `generate_grid` method generates the game grid by randomly placing mines. It ensures that the first click location is safe and avoids clusters of more than four mines in a 3x3 grid to allow for a mathematically solveable game!

### Main Game Loop

The main game loop continuously updates the game interface, handles user input, and manages the game state. The timer counts up during gameplay, and the player wins by revealing all non-mine tiles. The `prompt` method displays the player's score and high score when the game is won or lost.

## 6. Issues

* Selecting difficulty causes background to go black
* Selecting difficulty can reset the logged in user
* Pygame causes major performance problems at higher refresh rates
* The program has a set window size and is not dynamic, causing minimal portability
  * This causes very high resolution screens or extremely low resolution screens to have adverse effects (best played on 1080p or 1440p resolutions)
* Database is not encrypted
* Some elements drawn over twice when opening settings menu
* Leaderboard formatting is incorrect, and data is placed in wrong locations

## 7. Contributors

*[Ben Lewis](https://github.com/benlewisss "Click here to be taken to Ben's GitHub profile!")*
