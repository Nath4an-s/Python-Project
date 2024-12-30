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
        self.priorities = self.set_priorities()
        self.last_attack_time = 0
        self.attack_cooldown = 30  # seconds between attacks

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
        
        # Assign defensive positions if needed
        defensive_troops = self.assign_defenders(inactive_troops)
        remaining_troops = [t for t in inactive_troops if t not in defensive_troops]
        
        self.build_structures(building_villagers)
        self.gather_resources(gathering_villagers)
        
        # Handle military units based on mode
        if self.mode == "defensive":
            self.defend(remaining_troops)
        else:
            self.strategic_attack(remaining_troops)
        
        # Always train new units according to ratios
        self.strategic_training()

    def assign_defenders(self, troops):
        defensive_troops = []
        if len(troops) > self.priorities["min_defenders"]:
            # Assign some troops to defend important buildings
            important_buildings = [b for b in self.player.buildings if isinstance(b, (TownCenter, Keep))]
            for building in important_buildings:
                if troops:
                    defender = troops.pop()
                    self.defend_position(defender, building.position)
                    defensive_troops.append(defender)
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
            
        # Find closest enemy units or buildings
        enemies = self.find_nearby_enemies(max_distance=15)
        if enemies:
            for troop in troops:
                closest_enemy = min(enemies, key=lambda e: self.calculate_distance(troop.position, e.position))
                Action(self.game_map).go_battle(troop, closest_enemy, self.current_time_called)

    def strategic_attack(self, troops):
        current_time = self.current_time_called
        if not troops or len(troops) < self.priorities["attack_threshold"]:
            return
            
        if current_time - self.last_attack_time < self.attack_cooldown:
            return

        # Find strategic targets (enemy resources, military buildings, etc.)
        targets = self.find_strategic_targets()
        if targets:
            self.last_attack_time = current_time
            target = self.choose_best_target(targets)
            for troop in troops:
                Action(self.game_map).go_battle(troop, target, self.current_time_called)

    def find_strategic_targets(self):
        targets = []
        # Get all enemy buildings and units directly
        for player in self.game_map.players:
            if player != self.player:
                # Prioritize military buildings
                for building in player.buildings:
                    if isinstance(building, (Barracks, ArcheryRange, Stable)):
                        targets.append(building)
                targets.extend(player.buildings)  # Add remaining buildings
                targets.extend(player.units)      # Add all units
        
        return targets

    def choose_best_target(self, targets):
        # Choose target based on strategic value and distance
        return min(targets, key=lambda t: (
            0 if isinstance(t, (Barracks, ArcheryRange, Stable)) else 1,  # Military buildings first
            self.calculate_distance(self.get_base_position(), t.position)
        ))

    def strategic_training(self):
        total_units = len(self.player.units)
        current_villagers = len([u for u in self.player.units if isinstance(u, Villager)])
        
        desired_villagers = int(total_units * self.priorities["villager_ratio"])
        
        if current_villagers < desired_villagers:
            self.train_villagers()
        else:
            self.train_troops()

    def calculate_distance(self, pos1, pos2):
        return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5

    def get_base_position(self):
        # Find the position of the main base (TownCenter)
        for building in self.player.buildings:
            if isinstance(building, TownCenter):
                return building.position
        return (0, 0)  # Default position if no TownCenter

    def find_nearby_enemies(self, max_distance):
        enemies = []
        base_pos = self.get_base_position()
        
        # Get enemy units directly from all players
        for player in self.game_map.players:
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
        unit_building_map = {
            "Barracks": Swordsman,
            "ArcheryRange": Archer,
            "Stable": Horseman
        }
        
        for building in self.player.buildings:
            building_type = type(building).__name__
            if building_type in unit_building_map:
                unit_class = unit_building_map[building_type]
                # Vérifier si le joueur a assez de ressources
                if all(self.player.owned_resources[resource] >= amount 
                      for resource, amount in unit_class.cost.items()):
                    x, y = building.position
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            new_x = x + dx
                            new_y = y + dy
                            if self.is_position_valid(new_x, new_y, 1):
                                Unit.train_unit(unit_class, new_x, new_y, self.player, 
                                             building, self.game_map, self.current_time_called)
                                self.debug_print(f"Training {unit_class.__name__} at ({new_x}, {new_y})")
                                return
                    break

    def gather_resources(self, villagers):
        if not villagers:
            return

        # Diviser les villagers en fonction des besoins en ressources
        wood_need = self.player.owned_resources.get("Wood", 0) < 200
        food_need = self.player.owned_resources.get("Food", 0) < 200
        
        num_villagers = len(villagers)
        wood_gatherers = []
        food_gatherers = []
        gold_gatherers = []

        if wood_need and food_need:
            # Si on a besoin des deux, répartir équitablement
            wood_gatherers = villagers[:num_villagers//2]
            food_gatherers = villagers[num_villagers//2:]
        elif wood_need:
            wood_gatherers = villagers
        elif food_need:
            food_gatherers = villagers
        else:
            # Si pas de besoin urgent en bois ou nourriture, focus sur l'or
            gold_gatherers = villagers

        # Envoyer les villageois chercher les ressources
        for villager in wood_gatherers:
            Action(self.game_map).gather_resources(villager, "Wood", self.current_time_called)
        
        for villager in food_gatherers:
            Action(self.game_map).gather_resources(villager, "Food", self.current_time_called)
            
        for villager in gold_gatherers:
            Action(self.game_map).gather_resources(villager, "Gold", self.current_time_called)

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
