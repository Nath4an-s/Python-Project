import random
import math
from Building import TownCenter
from logger import debug_print

# Unit Class
class Unit:
    def __init__(self, player, hp, cost, attack, speed, symbol="u", training_time=0, position=(0.0, 0.0)):
        self.player = player
        self.hp = hp
        self.cost = cost
        self.attack = attack
        self.speed = speed
        self.position = None
        self.symbol = symbol
        self.training_time = training_time
        self.position = position
        self.target_position = None
        self.target_attack = None
        self.is_attacked_by = None

    def __str__(self):
        return self.symbol  # Ensure the building is represented by just the symbol
    
    def move(self, new_position):
        self.position = new_position

    def update(self):
        pass

    @classmethod
    def place_starting_units(cls, players, game_map):
        for player in players:
            town_centers = [building for building in player.buildings if isinstance(building, TownCenter)]
            
            if not town_centers:
                debug_print(f"No town centers found for {player.name}. Skipping unit placement.")
                continue
                
            town_center = town_centers[0]  # Use the first town center
            center_x, center_y = town_center.position
            
            radius = 7  # Adjust radius as needed

            if player.civilization == "Marines":
                num_villagers = 15
            else:
                num_villagers = 3
                
            debug_print(f"Attempting to spawn {num_villagers} villagers for {player.name} around ({center_x}, {center_y})")

            for _ in range(num_villagers):
                placed = False
                
                while not placed:
                    angle = random.uniform(0, 2 * math.pi)
                    distance = random.uniform(0, radius)
                    
                    spawn_x = center_x + int(distance * math.cos(angle))
                    spawn_y = center_y + int(distance * math.sin(angle))

                    if (0 <= spawn_x < game_map.width and 
                        0 <= spawn_y < game_map.height):
                        
                        if game_map.is_tile_free_for_unit(spawn_x, spawn_y):  # Check if tile is free
                            cls.spawn_unit(Villager, spawn_x, spawn_y, player, game_map)  # Place the villager --> IA should spawn them next to the appropriate building
                            placed = True
                        else:
                            pass  # Try again if tile is not free
                    else:
                        pass  # Try again if out of bounds
            debug_print(f"Spawned {num_villagers} villagers for {player.name} near the Town Center at ({center_x}, {center_y})")


    @classmethod
    def spawn_unit(cls, unit_class, x, y, player, game_map):
        if isinstance(unit_class, type):
            unit = unit_class(player)  # create an  instance
        else:
            unit = unit_class

        if (0 <= x < game_map.width and 
            0 <= y < game_map.height and 
            not (player.population >= player.max_population or 
                player.population >= sum(building.population_increase for building in player.buildings))):
            
            building = game_map.grid[y][x].building
            if not building or building.is_walkable():
                player.units.append(unit)
                unit.position = (x, y)
                player.population += 1
                game_map.place_unit(x, y, unit)
                return unit
            else:
                debug_print(f"Cannot place unit at ({x}, {y}): tile is not walkable.")
                return None
        else:
            debug_print(f"Cannot place unit at ({x}, {y}): invalid position or population limit reached.")
            return None

        
    @classmethod
    def train_unit(cls, unit_to_train, x, y, player, game_map, current_time_called):
        if isinstance(unit_to_train, type):
            unit_to_train = unit_to_train(player)
        
        if player.population < min(player.max_population, sum(building.population_increase for building in player.buildings)):
            
            if (not hasattr(unit_to_train, 'training_start') or unit_to_train.training_start is None):
                unit_to_train.training_start = current_time_called
                for resource_type, amount in unit_to_train.cost.items():
                    player.owned_resources[resource_type] -= amount
                    debug_print(f"{player.name} spent {amount} {resource_type} to train {unit_to_train.name}.")

                player.training_queue.append(unit_to_train)

            if current_time_called - unit_to_train.training_start >= unit_to_train.training_time:
                debug_print(current_time_called - unit_to_train.training_start)
                cls.spawn_unit(unit_to_train, x, y, unit_to_train.player, game_map)
                player.training_queue.remove(unit_to_train)
                debug_print(f"Should have spawned {unit_to_train.name} at ({x}, {y})")
                
                if player.training_queue:
                    next_unit = player.training_queue[0]
                    next_unit.training_start = current_time_called
                    debug_print(f"Starting training for {next_unit.name}")
        else:
            debug_print(f"Too much population or not enough resources to train {unit_to_train.name}.")
            if player.training_queue:
                player.training_queue.remove(unit_to_train)
                if player.training_queue:
                    next_unit = player.training_queue[0]
                    next_unit.training_start = current_time_called


        
    @classmethod
    def kill_unit(cls, player, unit_to_kill, game_map):
        if unit_to_kill in player.units:
            player.units.remove(unit_to_kill)  # Remove the unit from the player's list of units
            player.population -= 1  # Decrease the player's population
            x, y = unit_to_kill.position
            game_map.remove_unit(int(x), int(y), unit_to_kill)  # Assuming game_map is a property of the player
            debug_print(f"Unit {unit_to_kill.name} belonging to {player.name} at ({x}, {y}) killed. (RIP)")
        else:
            debug_print(f"Unit {unit_to_kill.name} does not belong to {player.name}.")

    @classmethod
    def get_all_units(cls, players):
        units = []
        for player in players:
            units.extend(player.units)
        return units

class Villager(Unit):
    @staticmethod
    def lire_noms_fichier(fichier="noms_villageois.txt"):
        try:
            with open(fichier, "r") as f:
                noms = [ligne.strip() for ligne in f if ligne.strip()]
            return noms
        except FileNotFoundError:
            debug_print(f"Le fichier {fichier} n'a pas été trouvé.")
            return ["Villager"]  # in case file not found

    def __init__(self, player, name=None):
        if name is None:
            noms_disponibles = self.lire_noms_fichier()
            name = random.choice(noms_disponibles)

        super().__init__(player, hp=25, cost={"Food": 50}, attack=2, speed=3, symbol="v", training_time=25) #TODO : speed 0.8
        self.carrying = {"Wood": 0, "Food": 0, "Gold": 0}
        self.carry_capacity = 20  # Can carry up to 20 of any resource
        self.gather_rate = 25 / 60  # 25 resources per minute (in resources per second)
        self.name = name
        self.task = None
        self.last_gathered = None
        self.range = 0.99


# Swordsman Class
class Swordsman(Unit):
    def __init__(self, player):
        super().__init__(player, hp=40, cost={"Food": 50, "Gold": 20}, attack=4, speed=0.9, symbol="s", training_time=20)
        self.range = 0.99
        self.task = None
        self.name = "Swordsman"


# Horseman Class
class Horseman(Unit):
    def __init__(self, player):
        super().__init__(player, hp=45, cost={"Food": 80, "Gold": 20}, attack=4, speed=1.2, symbol="h", training_time=30)
        self.range = 0.99
        self.task = None
        self.name = "Horseman"


# Archer Class
class Archer(Unit):
    def __init__(self, player):
        super().__init__(player, hp=30, cost={"Wood": 25, "Gold": 45}, attack=4, speed=1, symbol="a", training_time=35)
        self.range = 4  # Archers have a range of 4 tiles
        self.task = None
        self.name = "Archer"
