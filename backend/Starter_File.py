# Config File

from Players import *
import random
from Players import Player

# Game Mode
GameMode = "Utopia"  # "Utopia" or "Gold Rush"

# Set up map size
map_size = (120, 120)  # minimum 120x120

# Set up GUI size
GUI_size = type('GUI_size', (object,), {})()
GUI_size.x = 800
GUI_size.y = 600
AVAILABLE_COLORS = [
    (0, 0, 255),  # Blue
    (255, 0, 0),  # Red
    (0, 255, 0),  # Green
    (255, 255, 0),  # Yellow
    (128, 0, 128),  # Purple
    (255, 165, 0),  # Orange
    (0, 255, 255),  # Cyan
    (255, 105, 180)  # Pink
]

def start_players():
    players = []
    print("Welcome to the game!")
    num_players = int(input("Enter the number of players (2-8): "))
    assert 2 <= num_players <= 8, "The number of players must be between 2 and 8."

    for i in range(num_players):
        name = input(f"Enter name for Player {i + 1}: ")
        print("Choose a civilization: Means, Leans, or Marines")
        civilization = input(f"Player {i + 1} civilization: ").capitalize()
        assert civilization in ["Means", "Leans", "Marines"], "Invalid civilization. Choose from Means, Leans, or Marines."

        print("Choose an AI profile: aggressive or defensive")
        ai_profile = input(f"Player {i + 1} AI profile: ").lower()
        assert ai_profile in ["aggressive", "defensive"], "Invalid AI profile. Choose either aggressive or defensive."

        color = AVAILABLE_COLORS[i]
        print(f"Player {i + 1} will have color: {color}")
        
        players.append(Player(name, civilization, ai_profile, player_id=i + 1, color=color))

    return players

# Generate the PLAYER_COLORS dictionary for use in other parts of the game
players = start_players()
PLAYER_COLORS = {player.id: player.color for player in players}