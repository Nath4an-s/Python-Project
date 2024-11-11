#Config File

from Players import *

# Game Mode
GameMode = "Utopia" # "Utopia" or "Gold Rush"

# Set up map size
map_size = (120, 120) #minimum 120x120

# Set up GUI size
GUI_size = type('GUI_size', (object,), {})()
GUI_size.x = 800
GUI_size.y = 600

# Initialize players with both name and AI profile
#Civilizations are either Leans, Means or Marines
players = [
    Player('Player 1', "Means", AIProfile(strategy_type="aggressive"), player_id=1),
    Player('Player 2', "Leans", AIProfile(strategy_type="defensive"), player_id=2),
    Player('Player 3', "Marines", AIProfile(strategy_type="defensive"), player_id=3),
]