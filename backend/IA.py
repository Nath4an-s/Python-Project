#IA
from Actions import *
from frontend.Terrain import Map
from logger import debug_print
from backend.Building import *

class IA:
    def __init__(self, player, mode, game_map, current_time_called): #only one player --> IA class will be called for each player in GameEngine
        self.player = player
        self.mode = mode
        self.game_map = game_map
        self.debug_print = debug_print
        self.current_time_called = current_time_called

    def run(self):
        self.gather_resources()
        self.build_structures()
        self.attack()

    def gather_resources(self):
        for unit in self.player.units:
            if isinstance(unit, Villager) and unit.task is None:
                if self.player.owned_resources["Wood"] < self.player.owned_resources["Gold"]:
                    resource_type = "Wood"
                else:
                    resource_type = "Gold"
                Action(self.game_map).gather_resources(unit, resource_type, self.current_time_called)

    def build_structures(self):
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

        # Count the number of each type of building the player currently has
        building_counts = {building.__name__: 0 for building in building_types}
        
        for building in self.player.buildings:
            building_counts[type(building).__name__] += 1

        # Identify the building type that is least constructed
        least_constructed_building = min(building_counts, key=building_counts.get)

        # Check if the player has enough resources to construct the identified building
        required_resources = building_costs[least_constructed_building]
        if all(self.player.owned_resources[resource] >= amount for resource, amount in required_resources.items()):
            # Find an idle villager to construct the building
            for unit in self.player.units:
                if unit.task is None and isinstance(unit, Villager):
                    Action(self.game_map).construct_building(unit, eval(least_constructed_building), unit.x, unit.y, self.player, self.current_time_called)
                    break

    def attack(self):
        #TODO: code
        pass
