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


def generate_random_player_names(num_players):
    """Generate random player names."""
    predefined_names = [
        "Arthur", "Merlin", "Guinevere", "Lancelot", "Morgana", 
        "Percival", "Tristan", "Isolde"
    ]
    # If there are more players than predefined names, generate extra names
    if num_players > len(predefined_names):
        predefined_names += [f"Player{i}" for i in range(len(predefined_names) + 1, num_players + 1)]
    return predefined_names[:num_players]

def generate_player_colors(num_players):
    """Generate unique colors for players."""
    predefined_colors = [
        (0, 0, 255),  # Blue
        (255, 0, 0),  # Red
        (0, 255, 0),  # Green
        (255, 255, 0),  # Yellow
        (128, 0, 128),  # Purple
        (0, 255, 255),  # Cyan
        (255, 165, 0),  # Orange
        (128, 128, 128),  # Gray
    ]
    if num_players <= len(predefined_colors):
        return predefined_colors[:num_players]
    else:
        # Generate random colors for players beyond predefined ones
        colors = predefined_colors[:]
        while len(colors) < num_players:
            color = tuple(random.randint(0, 255) for _ in range(3))
            if color not in colors:  # Ensure no duplicate colors
                colors.append(color)
        return colors



def start_random_players():
    """Generate players randomly without user input."""
    num_players = random.randint(2, 8)  # Choose a random number of players between 2 and 8
    print(f"Randomly chosen number of players: {num_players}")

    player_names = generate_random_player_names(num_players)
    player_colors = generate_player_colors(num_players)
    civilizations = ["Leans", "Means", "Marines"]
    ai_profiles = ["aggressive", "defensive"]

    players = []
    for i in range(num_players):
        name = player_names[i]
        civilization = random.choice(civilizations)
        ai_profile = random.choice(ai_profiles)
        color = player_colors[i]

        print(f"Player {i + 1}: {name}, Civilization: {civilization}, AI Profile: {ai_profile}, Color: {color}")
        players.append(Player(name, civilization, ai_profile, player_id=i + 1, color=color))

    return players

def start_manual_players():
    """Configure players manually."""
    print("Welcome to the game!")
    num_players = 0
    while num_players < 2 or num_players > 8:  # Limit the number of players between 2 and 8
        try:
            num_players = int(input("Enter the number of players (2-8): "))
            if num_players < 2 or num_players > 8:
                print("Please choose between 2 and 8 players.")
        except ValueError:
            print("Invalid input. Please enter a number between 2 and 8.")
    
    player_colors = generate_player_colors(num_players)
    players = []
    for i in range(1, num_players + 1):
        name = input(f"Enter name for Player {i}: ")
        print("Choose a civilization: Leans, Means, or Marines")
        civilization = input(f"Player {i} civilization: ").capitalize()
        while civilization not in ["Leans", "Means", "Marines"]:
            print("Invalid civilization. Choose between Leans, Means, or Marines.")
            civilization = input(f"Player {i} civilization: ").capitalize()

        print("Choose an AI profile: aggressive or defensive")
        ai_profile = input(f"Player {i} AI profile: ").lower()
        while ai_profile not in ["aggressive", "defensive"]:
            print("Invalid AI profile. Choose between aggressive or defensive.")
            ai_profile = input(f"Player {i} AI profile: ").lower()

        # Assign a color to the player
        color = player_colors[i - 1]
        print(f"Player {i} will have color: {color}")

        players.append(Player(name, civilization, ai_profile, player_id=i, color=color))

    return players

def start_players():
    """Prompt the user to choose between random or manual player generation."""
    print("Choose an option:")
    print("1. Generate players randomly")
    print("2. Configure players manually")
    
    choice = 0
    while choice not in [1, 2]:
        try:
            choice = int(input("Enter 1 or 2: "))
            if choice not in [1, 2]:
                print("Invalid choice. Please enter 1 or 2.")
        except ValueError:
            print("Invalid input. Please enter a number (1 or 2).")

    if choice == 1:
        return start_random_players()
    else:
        return start_manual_players()

# Start by generating or configuring players
players = start_players()

# Create a PLAYER_COLORS dictionary for the map
PLAYER_COLORS = {player.id: player.color for player in players}

# You can now proceed with the rest of the game logic using the `players` list and `PLAYER_COLORS`