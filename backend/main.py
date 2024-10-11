import curses
import os
import sys

from Game_Engine import GameEngine
from Starter_File import players, map_size

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Main function to initialize and start the game using curses
def main(stdscr):
    curses.curs_set(0)  # Hide cursor
    stdscr.clear()

    game_engine = GameEngine(players, map_size)

    # Run the game
    game_engine.run(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)

