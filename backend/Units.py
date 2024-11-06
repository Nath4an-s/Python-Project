import random
import math
from Building import TownCenter

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
                print(f"No town centers found for {player.name}. Skipping unit placement.")
                continue
                
            town_center = town_centers[0]  # Use the first town center
            center_x, center_y = town_center.position
            
            radius = 7  # Adjust radius as needed

            if player.civilization == "Marines":
                num_villagers = 15
            else:
                num_villagers = 3
                
            print(f"Attempting to spawn {num_villagers} villagers for {player.name} around ({center_x}, {center_y})")

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
                            cls.spawn_unit(Villager, spawn_x, spawn_y, player, game_map)  # Pass game_map
                            placed = True
                        else:
                            pass  # Try again if tile is not free
                    else:
                        pass  # Try again if out of bounds
            print(f"Spawned {num_villagers} villagers for {player.name} near the Town Center at ({center_x}, {center_y})")


    @classmethod
    def spawn_unit(cls, unit_class, x, y, player, game_map):
        unit = unit_class(player)  # Create an instance of the unit
        if (0 <= x < game_map.width and 
            0 <= y < game_map.height and 
            not (player.population >= player.max_population or 
                player.population >= sum(building.population_increase for building in player.buildings))):
            
            building = game_map.grid[y][x].building
            if not building or building.is_walkable():
                player.units.append(unit)  # Add the unit to the player's list of units
                unit.position = (x, y)
                player.population += 1
                game_map.place_unit(x, y, unit)  # Place the unit on the map
                return unit
            else:
                # There's a building that isn't walkable
                return None
        else:
            # Too much population
            return None

        
    @classmethod
    def kill_unit(cls, player, unit_to_kill, game_map):
        if unit_to_kill in player.units:
            player.units.remove(unit_to_kill)  # Remove the unit from the player's list of units
            player.population -= 1  # Decrease the player's population
            x, y = unit_to_kill.position
            game_map.remove_unit(x, y, unit_to_kill)  # Assuming game_map is a property of the player
            print(f"Unit {unit_to_kill} belonging to {player.name} at ({x}, {y}) killed.")
        else:
            print(f"Unit {unit_to_kill} does not belong to {player.name}.")

    @classmethod
    def get_all_units(cls, players):
        units = []
        for player in players:
            units.extend(player.units)
        return units


# Villager Class
class Villager(Unit):
    def __init__(self, player, name="Villager"):
        super().__init__(player, hp=25, cost={"Food": 50}, attack=2, speed=0.8, symbol="v", training_time=25)
        self.carrying = {"Wood": 0, "Food": 0, "Gold": 0}
        self.carry_capacity = 20  # Can carry up to 20 of any resource
        self.gather_rate = 25 / 60  # 25 resources per minute (in resources per second)
        self.name = name
        self.task = None
        self.position = (0, 0)  # Initial position should be set appropriately
        self.last_gathered = None

# Swordsman Class
class Swordsman(Unit):
    def __init__(self, player):
        super().__init__(player, hp=40, cost={"Food": 50, "Gold": 20}, attack=4, speed=0.9, symbol="s", training_time=20)


# Horseman Class
class Horseman(Unit):
    def __init__(self, player):
        super().__init__(player, hp=45, cost={"Food": 80, "Gold": 20}, attack=4, speed=1.2, symbol="h", training_time=30)


# Archer Class
class Archer(Unit):
    def __init__(self, player):
        super().__init__(player, hp=30, cost={"Wood": 25, "Gold": 45}, attack=4, speed=1, symbol="a", training_time=35)
        self.range = 4  # Archers have a range of 4 tiles
