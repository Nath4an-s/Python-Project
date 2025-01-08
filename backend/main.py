# main.py

import curses
import os
import sys
import argparse

# Ajouter le chemin du projet à sys.path pour ne pas avoir à le faire dans le terminal
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from Game_Engine import GameEngine
from Starter_File import players, map_size

def init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLUE, -1)     # Texte bleu
    curses.init_pair(2, curses.COLOR_RED, -1)      # Texte rouge
    curses.init_pair(3, curses.COLOR_GREEN, -1)    # Texte vert
    curses.init_pair(4, curses.COLOR_YELLOW, -1)   # Texte jaune
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)  # Texte magenta
    curses.init_pair(6, curses.COLOR_CYAN, -1)     # Texte cyan
    curses.init_pair(7, curses.COLOR_WHITE, -1)    # Texte blanc

def init_colors():
    if not curses.has_colors():
        raise Exception("Le terminal ne supporte pas les couleurs.")
    curses.start_color()
    curses.use_default_colors()

def display_player_items(stdscr, players):
    for player in players:
        player_id = player.id
        color_pair = curses.color_pair(player_id)  # Associe l'ID du joueur à une couleur
        stdscr.addstr(f"Joueur {player_id}: {player.name} ({player.civilization})\n", color_pair)
# Main function to initialize and start the game using curses
def main(stdscr, save_file=None):
    # Initialiser curses
    curses.curs_set(0)  # Masquer le curseur
    stdscr.clear()
    init_colors()

    # Vérifier le support des couleurs
    if not curses.has_colors():
        raise Exception("Le terminal ne supporte pas les couleurs.")
    curses.start_color()
    
    # Initialiser des paires de couleurs pour chaque joueur
    for idx, player in enumerate(players, start=1):
        # Limiter aux 8 premières couleurs de base (extensible avec un terminal avancé)
        curses.init_pair(idx, idx % 8, curses.COLOR_BLACK)

    # Afficher les joueurs et leurs couleurs dans le terminal
    for idx, player in enumerate(players, start=1):
        color_pair = curses.color_pair(idx)
        stdscr.addstr(idx, 0, f"Joueur {player.id}: {player.name}, Couleur: {player.color}", color_pair)

    stdscr.refresh()
    stdscr.getch()  # Attendre une touche pour continuer

    # Initialiser le moteur de jeu
    game_engine = GameEngine(players, map_size)

    # Charger la sauvegarde si un fichier est fourni
    if save_file:
        game_engine.load_game(save_file)
    else:
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
