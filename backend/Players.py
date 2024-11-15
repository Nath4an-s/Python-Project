# Player.py

#Civilizations' starting resources
Means_starting_resources = {"Wood": 200, "Food": 50, "Gold": 50}
Leans_starting_resources = {"Wood": 2000, "Food": 2000, "Gold": 2000}
Marines_starting_resources = {"Wood": 20000, "Food": 20000, "Gold": 20000}

# Player Class
class Player:
    def __init__(self, name, civilization, ai_profile, player_id):
        self.name = name
        self.civilization = civilization
        self.training_queue = []
        self.units = []  # Initialize the units list
        self.buildings = []
        self.ai_profile = ai_profile
        self.population = 0
        self.max_population = 200
        self.id = player_id  # Add this line to store the player's ID
        if self.civilization == "Means":
            self.owned_resources = Means_starting_resources
        elif self.civilization == "Leans":
            self.owned_resources = Leans_starting_resources
        elif self.civilization == "Marines":
            self.owned_resources = Marines_starting_resources
        
    def __str__(self):
        return self.name

    def take_turn(self, game_map):
        self.ai_profile.make_decision(self, game_map)

    def has_units(self):
        return len(self.units) > 0


# AIProfile Class
class AIProfile:
    def __init__(self, strategy_type):
        self.strategy_type = strategy_type  # "defensive", "aggressive"

    def make_decision(self, player, game_map):
        if self.strategy_type == "aggressive":
            self.attack(player, game_map)
        elif self.strategy_type == "defensive":
            self.defend(player, game_map)

    def attack(self, player, game_map):
        pass

    def defend(self, player, game_map):
        pass
