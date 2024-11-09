#main.py

import curses
import os
import sys

# Ajouter le chemin du projet à sys.path pour ne pas à le faire dans le terminal
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from Game_Engine import GameEngine
from Starter_File import players, map_size

# Main function to initialize and start the game using curses
def main(stdscr):
    curses.curs_set(0)  # Hide cursor
    stdscr.clear()

    game_engine = GameEngine(players, map_size)

    # Run the game
    game_engine.run(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)
