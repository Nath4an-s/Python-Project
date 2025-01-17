#IA
from Actions import *
from logger import debug_print
from Building import *
from Units import *
from backend.Starter_File import players

class IA:
    def __init__(self, player, mode, game_map, current_time_called): #only one player --> IA class will be called for each player in GameEngine
        self.player = player
        self.mode = mode
        self.game_map = game_map
        self.players = players
        self.debug_print = debug_print
        self.current_time_called = current_time_called
        self.priorities = self.set_priorities()
        self.decided_builds = [] # Store the decided building positions to avoid overlap --> stored for whole game
        self.target_player = None  # Targeted player for attacks


#### PRIORITIES and UNIT_RESOURCES ####

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

    def adjust_priorities(self):
        """
        Ajuste dynamiquement les priorités en fonction de l'état actuel du jeu.
        """
        # Analyse des ressources
        food = self.player.owned_resources["Food"]
        wood = self.player.owned_resources["Wood"]
        gold = self.player.owned_resources["Gold"]
        total_population = self.player.population
        max_population = self.player.max_population

        # Analyse des forces et des menaces
        total_villagers = len([u for u in self.player.units if isinstance(u, Villager)])
        total_military = len([u for u in self.player.units if isinstance(u, (Swordsman, Archer, Horseman))])
        enemy_threat_level = sum(len(p.units) + len(p.buildings) for p in self.players if p != self.player)

        # Ajustement des priorités de construction
        if food < 100:
            self.priorities["villager_ratio"] = 0.8  # Augmenter la priorité aux villageois
            self.priorities["military_ratio"] = 0.2  # Réduire la production militaire
        elif wood < 100 or gold < 50:
            self.priorities["villager_ratio"] = 0.7
            self.priorities["military_ratio"] = 0.3
        elif enemy_threat_level > total_military:
            self.priorities["villager_ratio"] = 0.5
            self.priorities["military_ratio"] = 0.5
        else:
            self.priorities = self.set_priorities()  # Rétablir les priorités par défaut

        # Gestion des limites de population
        if total_population >= max_population - 5:
            self.priorities["build_house"] = True
        else:
            self.priorities["build_house"] = False


#### MAIN LOOP ####

    def run(self):
        self.adjust_priorities()
        building_villagers, gathering_villagers, inactive_troops = self.get_inactive_units()
        
        self.build_structures(list(set(building_villagers)))
        
        _, remaining_builders, _ = self.get_inactive_units()
        remaining_builders = [v for v in remaining_builders if v not in building_villagers]
        gathering_villagers.extend(remaining_builders)
        
        gathering_villagers = list(set(gathering_villagers))
        self.gather_resources(gathering_villagers)
        
        # Check for nearby enemies for all units
        for unit in self.player.units:
            nearby_enemies = self.find_nearby_enemies(5, unit.position)  # 5 tile radius
            if nearby_enemies:
                closest_enemy = min(nearby_enemies, 
                    key=lambda e: self.calculate_distance(unit.position, e.position))
                Action(self.game_map).go_battle(unit, closest_enemy, self.current_time_called)
        
        # Handle remaining military strategy
        if self.mode == "aggressive":
            self.strategic_attack(list(set(inactive_troops)))
        
        self.train_units()


#### TRAINING STRATEGY ####

    def train_units(self):

        if (self.player.owned_resources["Food"] >= 2000 and 
            self.player.owned_resources["Wood"] >= 2000 and 
            self.player.owned_resources["Gold"] >= 2000 and 
            any(type(building).__name__ in ["Barracks", "Stable", "ArcheryRange"] for building in self.player.buildings) and 
            self.mode == "aggressive"):
            for unit in self.player.units:
                if isinstance(unit, Villager):
                    Unit.kill_unit(self.player, unit, self.game_map)
            free_slots = min(self.player.max_population - self.player.population - len(self.player.training_units), sum(building.population_increase for building in self.player.buildings) - self.player.population - len(self.player.training_units))
            for _ in range(free_slots):
                self.train_troops()
        else:
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

    def train_villagers(self):
        for building in self.player.buildings:
            if isinstance(building, TownCenter):
                x, y = building.position
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        new_x = x + dx
                        new_y = y + dy
                        if self.is_position_valid(new_x, new_y, 1, is_building=False):
                            Unit.train_unit(Villager, new_x, new_y, self.player, building, self.game_map, self.current_time_called)
                            #self.debug_print(f"{self.player.name} : Training villager at ({new_x}, {new_y})")
                            return

    def train_troops(self):
        buildings = [building for building in self.player.buildings if type(building).__name__ in ["Barracks", "ArcheryRange", "Stable"]]
        random.shuffle(buildings)
        
        for building in buildings:
            if type(building).__name__ == "Barracks":
                x, y = building.position
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        new_x = x + dx
                        new_y = y + dy
                        if self.is_position_valid(new_x, new_y, 1, is_building=False):
                            Unit.train_unit(Swordsman, new_x, new_y, self.player, building, self.game_map, self.current_time_called)
                            #self.debug_print(f"{self.player.name} : Training swordsman at ({new_x}, {new_y})")
                            return
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


#### GATHERING STRATEGY ####

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


#### BUILDING STRATEGY ####

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

        if building_counts["TownCenter"] == 0 and self.player.owned_resources["Wood"] >= 350:
            least_constructed_building = "TownCenter"
        # Check if food is low and prioritize building a Farm
        elif self.player.owned_resources["Food"] < 50 and self.player.owned_resources["Wood"] >= 60:
            least_constructed_building = "Farm"
        # Check if population limit is reached and prioritize building a House
        elif (self.player.population >= self.player.max_population 
              or self.player.population >= sum(building.population_increase for building in self.player.buildings) 
              and self.player.owned_resources["Wood"] >= 25) and sum(building.population_increase for building in self.player.buildings) - self.player.population - len(self.player.training_units):
            least_constructed_building = "House"
        else:
            # Identify the building type that is least constructed
            # Filter buildings that can be constructed based on available resources
            constructable_buildings = [
                b_name for b_name, costs in building_costs.items()
                if all(self.player.owned_resources[resource] >= amount 
                      for resource, amount in costs.items())
            ]
            
            # Find the least constructed among constructable buildings
            least_constructed_building = min(
                constructable_buildings,
                key=lambda b: building_counts[b],
                default="Farm"  # Default to Farm if no buildings are constructable
            )
        
        building_class = eval(least_constructed_building)
        # Check if the player has enough resources to construct the identified building
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
            self.debug_print(f"{self.player.name} : Building {building_class.__name__} at {build_position}")
            for villager in villagers:
                Action(self.game_map).construct_building(
                    villager, 
                    building_class,
                    build_position[0], 
                    build_position[1],
                    self.player,
                    self.current_time_called
                )
                if build_position not in self.decided_builds:
                    self.decided_builds.append(build_position)


#### ATTACK STRATEGY ####

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
                #troop.task = None  # Clear any existing task
                Action(self.game_map).go_battle(troop, target, self.current_time_called)

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
    
    def find_nearby_enemies(self, max_distance, unit_position):
        enemies = []
        for player in self.players:
            if player != self.player:
                for enemy in player.units:
                    dist = self.calculate_distance(unit_position, enemy.position)
                    if dist <= max_distance:
                        enemies.append(enemy)
                for building in player.buildings:
                    dist = self.calculate_distance(unit_position, building.position)
                    if dist <= max_distance:
                        enemies.append(building)
        return enemies


#### DEFENSE STRATEGY ####

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
        if unit.target_position is None:
            Action(self.game_map).move_unit(unit, patrol_x, patrol_y, self.current_time_called)
            self.defend(unit)

    def defend(self, unit):
                    
        # Find closest enemy units or buildings
        enemies = self.find_nearby_enemies(max_distance=15)
        if enemies:
            closest_enemy = min(enemies, key=lambda e: self.calculate_distance(unit.position, e.position))
            Action(self.game_map).go_battle(unit, closest_enemy, self.current_time_called)

    def get_base_position(self):
        # Find the position of the main base (TownCenter)
        for building in self.player.buildings:
            if isinstance(building, TownCenter):
                return building.position
        return (0, 0)  # Default position if no TownCenter