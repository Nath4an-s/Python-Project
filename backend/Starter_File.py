# Config File

from Players import *
import random

# Set up GUI size
GUI_size = type('GUI_size', (object,), {})()
GUI_size.x = 800
GUI_size.y = 600

def generate_player_colors(num_players):
    """Generate unique colors for players."""
    predefined_colors = [
        (0, 0, 255),  # Blue
        (255, 0, 0),  # Red
        (0, 255, 0),  # Green
        (255, 255, 0),  # Yellow
        (128, 0, 128),  # Purple
        (0, 255, 255),  # Cyan
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
    num_players = random.randint(2, 7)  # Choose a random number of players between 2 and 8
    print(f"Randomly chosen number of players: {num_players}")

    player_colors = generate_player_colors(num_players)
    civilizations = ["Leans", "Means", "Marines"]
    ai_profiles = ["aggressive", "defensive"]

    players = []
    for i in range(num_players):
        name = f"Player {i + 1}"
        civilization = random.choice(civilizations)
        ai_profile = random.choice(ai_profiles)
        color = player_colors[i]

        print(f"Player {i + 1}: {name}, Civilization: {civilization}, AI Profile: {ai_profile}, Color: {color}")
        players.append(Player(name, civilization, ai_profile, player_id=i + 1, color=color))

    return players

def start_manual_players():
    """Configure players manually."""
    num_players = 0
    while num_players < 2 or num_players > 8:  # Limit the number of players between 2 and 8
        try:
            num_players = int(input("Enter the number of players (2-7): "))
            if num_players < 2 or num_players > 7:
                print("Please choose between 2 and 7 players.")
        except ValueError:
            print("Invalid input. Please enter a number between 2 and 7.")
    
    player_colors = generate_player_colors(num_players)
    players = []
    for i in range(1, num_players + 1):
        name = f"Player {i}"
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
    print("Choose a game mode:")
    print("1. Utopia")
    print("2. Gold Rush")
    
    game_mode_choice = 0
    while game_mode_choice not in [1, 2]:
        try:
            game_mode_choice = int(input("Enter 1 or 2: "))
            if game_mode_choice not in [1, 2]:
                print("Invalid choice. Please enter 1 or 2.")
        except ValueError:
            print("Invalid input. Please enter a number (1 or 2).")

    game_mode = "Utopia" if game_mode_choice == 1 else "Gold Rush"
    print(f"Selected game mode: {game_mode}")

    # Prompt for map size
    map_size = (0, 0)
    while map_size[0] < 120 or map_size[1] < 120:
        try:
            map_size_input = input("Enter map size in format X*X (minimum 120*120): ")
            map_size = (int(map_size_input), int(map_size_input))
            if map_size[0] < 120 or map_size[1] < 120:
                print("Map size must be at least 120*120.")
        except ValueError:
            print("Invalid input. Please enter the map size in format X*X.")

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

    players = start_random_players() if choice == 1 else start_manual_players()

    return players, game_mode, map_size

# Start by generating or configuring players
players, GameMode, map_size = start_players()

# Create a PLAYER_COLORS dictionary for the map
PLAYER_COLORS = {player.id: player.color for player in players}