#IA
from Actions import *
from frontend.Terrain import Map
from logger import debug_print
from backend.Building import *
from Units import *

class IA:
    def __init__(self, player, mode, game_map, current_time_called): #only one player --> IA class will be called for each player in GameEngine
        self.player = player
        self.mode = mode
        self.game_map = game_map
        self.debug_print = debug_print
        self.current_time_called = current_time_called

    def get_inactive_units(self):
        inactive_villagers = []
        inactive_troops = []
        
        for unit in self.player.units:
            if unit.task is None:
                if isinstance(unit, Villager):
                    inactive_villagers.append(unit)
                elif isinstance(unit, (Swordsman, Archer, Horseman)):
                    inactive_troops.append(unit)
        
        # Split villagers into two groups
        num_builders = max(len(inactive_villagers) // 3, 1)  # Allocate 1/3 for building, minimum 1
        building_villagers = inactive_villagers[:num_builders]
        gathering_villagers = inactive_villagers[num_builders:]
        
        return building_villagers, gathering_villagers, inactive_troops

    def run(self):
        building_villagers, gathering_villagers, inactive_troops = self.get_inactive_units()
        
        self.build_structures(building_villagers)
        
        # Any remaining building villagers who couldn't build (due to lack of resources)
        # will be added to gathering villagers
        _, remaining_builders, _ = self.get_inactive_units()
        gathering_villagers.extend(remaining_builders)
        
        # Then gather resources with remaining villagers
        self.gather_resources(gathering_villagers)
        
        # Handle military units
        self.attack(inactive_troops)
        
        # Train new units
        self.train_units()

    def train_units(self):
        if (self.player.population + self.player.training_units >= self.player.max_population or 
                self.player.population + self.player.training_units >= sum(building.population_increase for building in self.player.buildings)):
            return  # Population limit reached, cannot train more units

        if self.mode == "defensive":
            self.train_villagers()
        elif self.mode == "aggressive":
            if self.player.owned_resources["Wood"] > 500 and self.player.owned_resources["Gold"] > 500:
                self.train_troops()
            else:
                self.train_villagers()

    def train_villagers(self): #TODO: ici c'est comme si les buildings avaient tous une taille de 1 il faut changer ca
        for building in self.player.buildings:
            if isinstance(building, TownCenter):
                x, y = building.position
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        new_x = x + dx
                        new_y = y + dy
                        if self.is_position_valid(new_x, new_y, 1):  # Assuming villager size is 1
                            Unit.train_unit(Villager, new_x, new_y, self.player, building, self.game_map, self.current_time_called)
                            self.debug_print(f"Training villager at ({new_x}, {new_y})")
                            return

    def train_troops(self):
        for building in self.player.buildings:
            if type(building).__name__ == "Barracks":
                x, y = building.position
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        new_x = x + dx
                        new_y = y + dy
                        if self.is_position_valid(new_x, new_y, 1):  # Assuming villager size is 1
                            Unit.train_unit(Swordsman, new_x, new_y, self.player, building, self.game_map, self.current_time_called)
                            self.debug_print(f"Training swordsman at ({new_x}, {new_y})")
                            return
                break
            elif type(building).__name__ == "ArcheryRange":
                x, y = building.position
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        new_x = x + dx
                        new_y = y + dy
                        if self.is_position_valid(new_x, new_y, 1):  # Assuming villager size is 1
                            Unit.train_unit(Archer, new_x, new_y, self.player, building, self.game_map, self.current_time_called)
                            self.debug_print(f"Training archer at ({new_x}, {new_y})")
                            return
                break
            elif type(building).__name__ == "Stable":
                x, y = building.position
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        new_x = x + dx
                        new_y = y + dy
                        if self.is_position_valid(new_x, new_y, 1):  # Assuming villager size is 1
                            Unit.train_unit(Horseman, new_x, new_y, self.player, building, self.game_map, self.current_time_called)
                            self.debug_print(f"Training horseman at ({new_x}, {new_y})")
                            return
                break

    def gather_resources(self, villagers):
        for villager in villagers:
            if self.player.owned_resources["Wood"] < self.player.owned_resources["Gold"]:
                resource_type = "Wood"
            else:
                resource_type = "Gold"
            Action(self.game_map).gather_resources(villager, resource_type, self.current_time_called)

    def is_position_valid(self, x, y, building_size):
        # Check map boundaries
        if not (0 <= x < self.game_map.width - building_size and 
                0 <= y < self.game_map.height - building_size):
            return False
        
        # Check if area is free on map
        if not self.game_map.is_area_free(x, y, building_size):
            return False
            
        # Check for overlap with buildings under construction
        for building_info in self.player.constructing_buildings:
            # Get position from the dictionary format
            construct_x = building_info.get("position")[0]
            construct_y = building_info.get("position")[1]
            construct_size = building_info.get("size", building_size)  # Default to same size if not specified
            
            if (abs(construct_x - x) < max(building_size, construct_size) and
                abs(construct_y - y) < max(building_size, construct_size)):
                return False
                
        return True

    def build_structures(self, villagers):
        if not villagers:
            return
            
        building_types = [Farm, Barracks, House, TownCenter, Stable, ArcheryRange, Keep, Camp]
        building_costs = {
            "Farm": {"Wood": 60, "Gold": 0},
            "Barracks": {"Wood": 175, "Gold": 0},
            "House": {"Wood": 25, "Gold": 0},
            "TownCenter": {"Wood": 350, "Gold": 0},
            "Stable": {"Wood": 175, "Gold": 0},
            "ArcheryRange": {"Wood": 175, "Gold": 0},
            "Keep": {"Wood": 35, "Gold": 125},
            "Camp": {"Wood": 100, "Gold": 0}
        }

        building_counts = {building.__name__: 0 for building in building_types}
        for building in self.player.buildings:
            building_counts[type(building).__name__] += 1

        # Identify the building type that is least constructed
        least_constructed_building = min(building_counts, key=building_counts.get)
        building_class = eval(least_constructed_building)

        # Check if the player has enough resources to construct the identified building
        required_resources = building_costs[least_constructed_building]
        if all(self.player.owned_resources[resource] >= amount for resource, amount in required_resources.items()):
            build_position = None
            for existing_building in self.player.buildings:
                x, y = existing_building.position
                for radius in range(1, 10):
                    for dx in range(-radius, radius + 1):
                        for dy in range(-radius, radius + 1):
                            new_x = x + dx
                            new_y = y + dy
                            
                            if self.is_position_valid(new_x, new_y, building_class(self.player).size):
                                build_position = (new_x, new_y)
                                break
                        if build_position:
                            break
                    if build_position:
                        break
                if build_position:
                    break

            if build_position:
                for villager in villagers:
                    Action(self.game_map).construct_building(
                        villager, 
                        building_class,
                        build_position[0], 
                        build_position[1],
                        self.player,
                        self.current_time_called
                    )
                    break

    def attack(self, troops):
        if self.mode == "agressive" and len(troops) >= 5:
            # Find the nearest enemy unit to attack
            for enemy_player in self.game_map.players:
                if enemy_player != self.player:
                    for enemy_unit in enemy_player.units:
                        if enemy_unit.task != "is_attacked":
                            for troop in troops:
                                Action(self.game_map).go_battle(troop, enemy_unit, self.current_time_called)
                            return  # Attack the first found enemy unit
