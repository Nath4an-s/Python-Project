#IA
from Actions import *
from frontend.Terrain import Map
from logger import debug_print
from Building import *
from Units import *
from Starter_File import players

class IA:
    def __init__(self, player, mode, game_map, current_time_called): #only one player --> IA class will be called for each player in GameEngine
        self.player = player
        self.mode = mode
        self.game_map = game_map
        self.players = players
        self.debug_print = debug_print
        self.current_time_called = current_time_called
        self.priorities = self.set_priorities()
        self.attack_cooldown = 30  # Minimum time between strategic attacks
        self.last_attack_time = 0
        self.decided_builds = [] # Store the decided building positions to avoid overlap --> stored for whole game
        self.defending_units = []  # Track units assigned to defense
        self.target_player = None  # Targeted player for attacks

    def get_inactive_units(self):
        inactive_villagers = []
        inactive_troops = []
        
        for unit in self.player.units:
            if unit.task is None:
                if isinstance(unit, Villager):
                    inactive_villagers.append(unit)
                elif isinstance(unit, (Swordsman, Archer, Horseman)):
                    inactive_troops.append(unit)
        
        # Count active villagers
        active_builders = len([u for u in self.player.units if isinstance(u, Villager) and (u.task == "constructing" or u.task == "going_to_construction_site")])
        active_gatherers = len([u for u in self.player.units if isinstance(u, Villager) and u.task == "gathering"])
        
        total_villagers = active_builders + active_gatherers + len(inactive_villagers)
        
        desired_builders = max(1, total_villagers // 3)

        
        # Allocate inactive villagers based on desired ratios
        building_villagers = []
        gathering_villagers = []
        
        for villager in inactive_villagers:
            if active_builders < desired_builders:
                building_villagers.append(villager)
                active_builders += 1
            else:
                gathering_villagers.append(villager)

        return building_villagers, gathering_villagers, inactive_troops

    def set_priorities(self):
        if self.mode == "defensive":
            return {
                "villager_ratio": 0.7,  # 70% villagers
                "military_ratio": 0.3,  # 30% military
                "min_defenders": 3,     # minimum units for defense
                "attack_threshold": 10   # minimum units for attack
            }
        else:  # aggressive
            return {
                "villager_ratio": 0.4,  # 40% villagers
                "military_ratio": 0.6,  # 60% military
                "min_defenders": 2,     # minimum units for defense
                "attack_threshold": 5    # minimum units for attack
            }
    
    def run(self):
        building_villagers, gathering_villagers, inactive_troops = self.get_inactive_units()
        
        #if building_villagers : self.debug_print(f"Build villageois : {[villager.name for villager in building_villagers]}")
        self.build_structures(list(set(building_villagers)))
        
        # Any remaining building villagers who couldn't build (due to lack of resources)
        # will be added to gathering villagers
        _, remaining_builders, _ = self.get_inactive_units()
        remaining_builders = [v for v in remaining_builders if v not in building_villagers]
        gathering_villagers.extend(remaining_builders)
        
        # Then gather resources with remaining villagers
        gathering_villagers = list(set(gathering_villagers))  # Ensure no duplicates
        self.gather_resources(gathering_villagers)
        
        defending_troops = self.assign_defenders(inactive_troops)
        self.defending_units = defending_troops 

        remaining_troops = [t for t in inactive_troops if t not in defending_troops]

        

        # Handle military units
        if self.mode == "defensive":
            self.defend(list(set(remaining_troops)))
        
        if self.mode == "aggressive":
            self.strategic_attack(list(set(remaining_troops)))
        
        # Train new units
        self.train_units()

    def train_units(self):
        if (self.player.population + len(self.player.training_units) >= self.player.max_population or 
                self.player.population + len(self.player.training_units) >= sum(building.population_increase for building in self.player.buildings)):
            return  # Population limit reached, cannot train more units

        total_units = len(self.player.units) + len(self.player.training_units)
        current_villagers = len([u for u in self.player.units if isinstance(u, Villager)]) + len([u for u in self.player.training_units if isinstance(u, Villager)])
        current_military = len([u for u in self.player.units if isinstance(u, (Swordsman, Archer, Horseman))]) + len([u for u in self.player.training_units if isinstance(u, (Swordsman, Archer, Horseman))])
        
        desired_villagers = max(1,int(total_units * self.priorities["villager_ratio"]))
        desired_military = max(1,int(total_units * self.priorities["military_ratio"]))
        
        if current_villagers < desired_villagers and self.player.owned_resources["Food"] > 50:
            self.train_villagers()
        elif current_military < desired_military and (
                self.player.owned_resources["Wood"] > 50 and 
                self.player.owned_resources["Gold"] > 50 and 
                self.player.owned_resources["Food"] > 100 and 
                any(type(building).__name__ in ["Barracks", "Stable", "ArcheryRange"] for building in self.player.buildings)):
            self.train_troops()
        elif self.player.owned_resources["Food"] > 50:
            self.train_villagers()

    def train_villagers(self): #TODO: ici c'est comme si les buildings avaient tous une taille de 1 il faut changer ca
        for building in self.player.buildings:
            if isinstance(building, TownCenter):
                x, y = building.position
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        new_x = x + dx
                        new_y = y + dy
                        if self.is_position_valid(new_x, new_y, 1, is_building=False):  # Assuming villager size is 1
                            Unit.train_unit(Villager, new_x, new_y, self.player, building, self.game_map, self.current_time_called)
                            #self.debug_print(f"{self.player.name} : Training villager at ({new_x}, {new_y})")
                            return

    def train_troops(self):
        for building in self.player.buildings:
            if type(building).__name__ == "Barracks":
                x, y = building.position
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        new_x = x + dx
                        new_y = y + dy
                        if self.is_position_valid(new_x, new_y, 1, is_building=False):  # Assuming villager size is 1
                            Unit.train_unit(Swordsman, new_x, new_y, self.player, building, self.game_map, self.current_time_called)
                            #self.debug_print(f"{self.player.name} : Training swordsman at ({new_x}, {new_y})")
                            return
                break
            elif type(building).__name__ == "ArcheryRange":
                x, y = building.position
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        new_x = x + dx
                        new_y = y + dy
                        if self.is_position_valid(new_x, new_y, 1, is_building=False):  # Assuming villager size is 1
                            Unit.train_unit(Archer, new_x, new_y, self.player, building, self.game_map, self.current_time_called)
                            #self.debug_print(f"{self.player.name} : Training archer at ({new_x}, {new_y})")
                            return
                break
            elif type(building).__name__ == "Stable":
                x, y = building.position
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        new_x = x + dx
                        new_y = y + dy
                        if self.is_position_valid(new_x, new_y, 1, is_building=False):  # Assuming villager size is 1
                            Unit.train_unit(Horseman, new_x, new_y, self.player, building, self.game_map, self.current_time_called)
                            #self.debug_print(f"{self.player.name} : Training horseman at ({new_x}, {new_y})")
                            return
                break

    def gather_resources(self, villagers):
        #if villagers : self.debug_print(f"Farm : {[villager.name for villager in villagers]}")
        for villager in villagers:
            # Determine the resource type that the player has the least of
            resource_types = sorted(self.player.owned_resources, key=self.player.owned_resources.get)
            for resource_type in resource_types:
                #self.debug_print(f"{villager.name} : Gathering {resource_type}")
                if Action(self.game_map).gather_resources(villager, resource_type, self.current_time_called):
                    break

    def is_position_valid(self, x, y, building_size, is_building=True):
        # Check map boundaries
        if not (0 <= x < self.game_map.width - building_size and 
                0 <= y < self.game_map.height - building_size):
            return False
        if is_building:
            for build in self.decided_builds:
                if (abs(build[0] - x) < building_size + 2 and
                    abs(build[1] - y) < building_size + 2):
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
            
        villagers = list(set(villagers))  # Ensure no duplicates
        
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

        # Check if food is low and prioritize building a Farm
        if self.player.owned_resources["Food"] < 50:
            least_constructed_building = "Farm"
        # Check if population limit is reached and prioritize building a House
        elif self.player.population >= self.player.max_population or self.player.population >= sum(building.population_increase for building in self.player.buildings):
            least_constructed_building = "House"
        else:
            # Identify the building type that is least constructed
            least_constructed_building = min(building_counts, key=building_counts.get)
        
        building_class = eval(least_constructed_building)

        # Check if the player has enough resources to construct the identified building
        required_resources = building_costs[least_constructed_building]
        if all(self.player.owned_resources[resource] >= amount for resource, amount in required_resources.items()):
            build_position = None
            for existing_building in self.player.buildings:
                x, y = existing_building.position
                for radius in range(5, 15): # buildings not too close to each other nor too far
                    for dx in range(-radius, radius + 1):
                        for dy in range(-radius, radius + 1):
                            new_x = x + dx
                            new_y = y + dy
                            
                            if self.is_position_valid(new_x, new_y, building_class(self.player).size, is_building=True):
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
                    self.decided_builds.append(build_position)
                    return
    



# ATTACK STRATEGY    
    def strategic_attack(self, troops):
        if not troops or len(troops) < self.priorities["attack_threshold"]:
            return

        if self.target_player is None or (self.target_player.units == [] and self.target_player.buildings == []):
            self.target_player = self.choose_best_target()

        if not self.target_player:
            return

        targets = [t for t in self.find_strategic_targets() if t.player == self.target_player]
        if targets:
            target = self.choose_best_target_unit(self.target_player, targets)
            for troop in troops:
                troop.task = None  # Clear any existing task
                Action(self.game_map).go_battle(troop, target, self.current_time_called)
                self.debug_print(f"{self.player.name} : Attacking {target.name} with {troop.name} at {target.position}")

    def find_strategic_targets(self):
        targets = []
        # Get all enemy buildings and units directly
        for player in self.players:
            if player != self.player:
                # Prioritize military buildings
                for building in player.buildings:
                    if isinstance(building, (Barracks, ArcheryRange, Stable)):
                        targets.append(building)
                targets.extend(player.buildings)  # Add remaining buildings
                targets.extend(player.units)      # Add all units
        
        return targets

    def choose_best_target(self):
        return min(
            (p for p in self.players if p != self.player and (p.units or p.buildings)),
            key=lambda p: len([u for u in p.units if isinstance(u, Villager)]) + len(p.buildings),
            default=None
        )
    
    def choose_best_target_unit(self, target_player, targets):
        return min(
            targets,
            key=lambda t: self.calculate_distance(self.get_base_position(), t.position)
        )
    
    def calculate_distance(self, pos1, pos2):
        return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5
    
    def find_nearby_enemies(self, max_distance):
        enemies = []
        base_pos = self.get_base_position()
        
        # Get enemy units directly from all players
        for player in self.players:
            if player != self.player:
                for unit in player.units:
                    dist = self.calculate_distance(base_pos, unit.position)
                    if dist <= max_distance:
                        enemies.append(unit)
                # Include enemy buildings in defensive consideration
                for building in player.buildings:
                    dist = self.calculate_distance(base_pos, building.position)
                    if dist <= max_distance:
                        enemies.append(building)
        
        return enemies

# DEFENSE STRATEGY
    def assign_defenders(self, troops):
        defensive_troops = list(self.defending_units)  # Maintain existing defenders
        needed_defenders = self.priorities["min_defenders"] - len(defensive_troops)

        if needed_defenders > 0:
            defensive_troops.extend(troops[:needed_defenders])

        important_buildings = [b for b in self.player.buildings if isinstance(b, (TownCenter, Camp))]
        for building, defender in zip(important_buildings, defensive_troops):
            self.defend_position(defender, building.position)

        return defensive_troops

    def defend_position(self, unit, position):
        patrol_radius = 5
        x, y = position
        
        # Calculate patrol position considering unit speed and patrol radius
        patrol_x = x + patrol_radius
        patrol_y = y
        
        # Use the existing move_unit method from Actions class
        Action(self.game_map).move_unit(unit, patrol_x, patrol_y, self.current_time_called)

    def defend(self, troops):
        if not troops:
            return
            
        troops = list(set(troops))  # Ensure no duplicates
        
        # Find closest enemy units or buildings
        enemies = self.find_nearby_enemies(max_distance=15)
        if enemies:
            for troop in troops:
                closest_enemy = min(enemies, key=lambda e: self.calculate_distance(troop.position, e.position))
                Action(self.game_map).go_battle(troop, closest_enemy, self.current_time_called)

    def get_base_position(self):
        # Find the position of the main base (TownCenter)
        for building in self.player.buildings:
            if isinstance(building, TownCenter):
                return building.position
        return (0, 0)  # Default position if no TownCenter