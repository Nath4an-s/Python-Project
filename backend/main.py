# main.py

import curses
import os
import sys
import argparse

# Ajouter le chemin du projet à sys.path pour ne pas avoir à le faire dans le terminal
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from Game_Engine import GameEngine
from backend.Starter_File import players, map_size


def main(stdscr, save_file=None):
    # Initialiser curses
    curses.curs_set(0)  # Masquer le curseur
    stdscr.clear()
    if save_file:
        game_engine = GameEngine(players, map_size,True)
        game_engine.load_game(save_file)
    else :
        game_engine = GameEngine(players, map_size,False)
        print("Aucun fichier de sauvegarde fourni. Démarrage d'une nouvelle partie.")

    # Lancer le jeu
    game_engine.run(stdscr)

if __name__ == "__main__":
    # Configurer argparse pour lire les arguments
    parser = argparse.ArgumentParser(description="Lancer le jeu avec ou sans sauvegarde.")
    parser.add_argument(
        "-s", "--save", 
        type=str, 
        help="Chemin vers le fichier de sauvegarde à charger (optionnel)."
    )
    args = parser.parse_args()
    # Passer le chemin de la sauvegarde (si fourni) à la fonction principale
    curses.wrapper(main, save_file=args.save)
