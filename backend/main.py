#main.py

import curses
import os
import sys
import argparse

# Ajouter le chemin du projet à sys.path pour ne pas à le faire dans le terminal
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from Game_Engine import GameEngine
from Starter_File import players, map_size
from frontend.gui import run_gui_mode

# Main function to initialize and start the game using curses
def main(stdscr, save_file=None):
    curses.curs_set(0)  # Hide cursor
    stdscr.clear()

    game_engine = GameEngine(players, map_size)
    
    if save_file:
        game_engine.load_game(save_file)
    else:
        print("No save file provided. Starting a new game.")
    
    # Run the game
    #run_gui_mode(game_engine)
    game_engine.run(stdscr)
    run_gui_mode(game_engine)

if __name__ == "__main__":
    # Configure argparse pour lire les arguments
    parser = argparse.ArgumentParser(description="Lancer le jeu avec ou sans sauvegarde.")
    parser.add_argument(
        "-s", "--save", 
        type=str, 
        help="Chemin vers le fichier de sauvegarde à charger (optionnel)."
    )
    args = parser.parse_args()

    # Passer le chemin de la sauvegarde (si fourni) à la fonction principale
    curses.wrapper(main, save_file=args.save)