#Actions.py

import heapq

from frontend.Terrain import *
from logger import debug_print
from Units import *
from Building import *

class Action:
    def __init__(self, game_map):
        self.map = game_map
        self.debug_print = debug_print

    def move_unit(self, unit, target_x, target_y, current_time_called):
        # Check if the target destination is valid
        if not self._is_within_bounds(target_x, target_y) or not self.map.is_tile_free_for_unit(int(target_x), int(target_y)):
            return False

        # Get current/starting position of the unit
        start_x, start_y = int(unit.position[0]), int(unit.position[1])
        unit.target_position = (target_x, target_y)

        # If path is not already constructed, construct it using A* algorithm
        if not hasattr(unit, 'path') or not unit.path:
            unit.path = self.astar_pathfinding((int(start_x), int(start_y)), (target_x, target_y))

        # Initialize last move time if not already set
        if not hasattr(unit, 'last_move_time'):
            unit.last_move_time = current_time_called

        # Calculate time passed since the last move
        current_time = current_time_called
        time_since_last_move = min(0.2, current_time - unit.last_move_time) #TODO: hardcode 0.2

        # Calculate the maximum distance the unit can move
        distance_to_move = unit.speed * time_since_last_move

        # Ensure there’s a path to follow and the unit can move
        if unit.path and distance_to_move > 0:
            # Get the next target position in the path
            next_step = unit.path[0]

            # Check if the next step is free (dynamic obstacle detection)
            if not self.map.is_tile_free_for_unit(next_step[0], next_step[1]):
                # Recalculate path if the next step is blocked
                unit.path = self.astar_pathfinding((int(start_x), int(start_y)), (target_x, target_y))
                if not unit.path:
                    self.debug_print("Path not found or obstructed")
                    return False  # No valid path found

            # Calculate the direction vector to the next step
            direction_x = next_step[0] - unit.position[0]
            direction_y = next_step[1] - unit.position[1]
            distance_to_next_step = (direction_x**2 + direction_y**2) ** 0.5

            # If within reach of the next step, move directly there
            if distance_to_move >= distance_to_next_step:
                unit.position = next_step
                unit.path.pop(0)  # Remove the step from the path

                # Snap to the tile if it's the last step before the target
                if not unit.path:  # No more steps in the path
                    unit.position = (target_x, target_y)
                    unit.path = None
                    unit.target_position = None
                    Map.move_unit(self.map, unit, int(unit.position[0]), int(unit.position[1]), int(start_x), int(start_y))
                    del unit.last_move_time
                    self.debug_print("Reached target!")
                    return True
            else:
                # Otherwise, move partway towards the next step
                normalized_x = direction_x / distance_to_next_step
                normalized_y = direction_y / distance_to_next_step

                # Calculate the new position based on the unit's speed
                unit.position = (
                    unit.position[0] + normalized_x * distance_to_move,
                    unit.position[1] + normalized_y * distance_to_move,
                )

            # Update the last move time
            unit.last_move_time = current_time
            Map.move_unit(self.map, unit, int(unit.position[0]), int(unit.position[1]), int(start_x), int(start_y))

            return True

        return False


    def astar_pathfinding(self, start, goal):
        open_list = []
        heapq.heappush(open_list, (0, start))  # Initialisation avec le point de départ

        came_from = {}  # Stocker les nœuds explorés
        g_cost = {start: 0}  # Coût actuel pour atteindre chaque nœud
        closed_set = set()  # Ensemble des nœuds déjà visités

        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Distance Manhattan

        while open_list:
            _, current = heapq.heappop(open_list)

            # Si nous atteignons l'objectif
            if current == goal:
                return self._reconstruct_path(came_from, current)

            closed_set.add(current)

            for neighbor in self._get_neighbors(current):
                if neighbor in closed_set:
                    continue

                # Vérifier si le voisin est bloqué
                if not self.map.is_tile_free_for_unit(neighbor[0], neighbor[1]):
                    continue

                # Coût du chemin jusqu'au voisin
                tentative_g_cost = g_cost[current] + self._move_cost(current, neighbor)

                if neighbor not in g_cost or tentative_g_cost < g_cost[neighbor]:
                    g_cost[neighbor] = tentative_g_cost
                    priority = tentative_g_cost + heuristic(neighbor, goal)
                    heapq.heappush(open_list, (priority, neighbor))
                    came_from[neighbor] = current

        # Aucun chemin trouvé
        return None

    def _is_within_bounds(self, x, y):
        return 0 <= x < self.map.width and 0 <= y < self.map.height

    def _get_neighbors(self, position):
        x, y = position
        neighbors = []

        # Possible directions
        directions = [
            (-1, 0), (1, 0),
            (0, -1), (0, 1),
            (-1, -1), (-1, 1),
            (1, -1), (1, 1)
        ]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self._is_within_bounds(nx, ny) and self.map.is_tile_free_for_unit(nx, ny):
                neighbors.append((nx, ny))

        return neighbors

    def get_adjacent_positions(self, x, y, size):
        adjacent_positions = []
        
        for i in range(size):
            adjacent_positions.append((x - 1, y + i))  # left side
            adjacent_positions.append((x + size, y + i))  # right side
            adjacent_positions.append((x + i, y - 1))  # top row
            adjacent_positions.append((x + i, y + size))  # bottom row

        adjacent_positions.extend([
            (x - 1, y - 1),  # corners
            (x - 1, y + size),
            (x + size, y - 1),
            (x + size, y + size)
        ])

        adjacent_positions = [
            (px, py) for px, py in adjacent_positions
            if 0 <= px < self.map.width and 0 <= py < self.map.height
        ]
        
        return adjacent_positions

    def _move_cost(self, current, neighbor):
        return 1 if abs(current[0] - neighbor[0]) + abs(current[1] - neighbor[1]) == 1 else 1.414

    def _reconstruct_path(self, came_from, current):
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.reverse()  #inverse the path for it to be in the right order
        return path
    
    def gather_resources(self, unit, resource_type, current_time_called):
        if resource_type == "Gold" or resource_type == "Wood":
            unit.last_gathered = resource_type
            # Find the coordinates of the nearest resource of the specified type
            if unit.target_resource is None:
                target = Map.find_nearest_resource(self.map, unit.position, resource_type, unit.player)
                if target is not None:
                    unit.target_resource = target
                else:
                    self.debug_print(f"No {resource_type} resources found.")
                    unit.task = None
                    unit.target_resource = None
                    unit.target_position = None
                    return False
            # Find a free tile around the target resource
            adjacent_tiles = self._get_neighbors((unit.target_resource[0], unit.target_resource[1]))
            free_tile = None

            # Check if unit is already adjacent to the resource (within a small threshold)
            if not any(abs(unit.position[0] - tile[0]) < 0.1 and abs(unit.position[1] - tile[1]) < 0.1 for tile in adjacent_tiles):
                # Move to an adjacent tile if not already there
                for tile in adjacent_tiles:
                    if self.map.is_tile_free_for_unit(tile[0], tile[1]):
                        free_tile = tile
                        break

                # If a free tile was found, move the unit towards it
                if free_tile:
                    # Update unit's position by calling move_unit
                    self.move_unit(unit, free_tile[0], free_tile[1], current_time_called)
                    unit.task = "marching"
                else:
                    self.debug_print("No free tile found around the resource.")
                    return False

            if any(abs(unit.position[0] - tile[0]) < 0.1 and abs(unit.position[1] - tile[1]) < 0.1 for tile in adjacent_tiles):
                unit.task = "gathering"
                self._gather(unit, resource_type, current_time_called)

        elif resource_type == "Food" : #should be FOod
            unit.last_gathered = resource_type
            # Find the coordinates of the nearest resource of the specified type
            target = Map.find_nearest_resource(self.map, unit.position, resource_type, unit.player)
            if target is not None:
                unit.target_resource = target
            else:
                self.debug_print(f"No {resource_type} resources found.")
                unit.task = None
                unit.target_position = None
                unit.target_resource = None
                return False
            # Move to the target tile if not already there
            if not (abs(unit.position[0] - unit.target_resource[0]) < 0.1 and abs(unit.position[1] - unit.target_resource[1]) < 0.1):
                # Update unit's position by calling move_unit
                self.move_unit(unit, unit.target_resource[0], unit.target_resource[1], current_time_called)
                unit.task = "marching"
            else:
                unit.task = "gathering"
                self._gather(unit, resource_type, current_time_called)

        else:
            self.debug_print("Invalid resource type.")
            return False

    def _gather(self, unit, resource_type, current_time_called):
        tile = self.map.grid[unit.target_resource[1]][unit.target_resource[0]] if unit.target_resource is not None else None
        # Check if there is a resource on the target tile and it's the correct type
        if (tile and tile.resource and tile.resource.type == resource_type) or (resource_type == "Food" and tile.building and tile.building.name == "Farm"):
            if resource_type == "Food":
                tile.building.is_farmed = True
            # Ensure the unit has capacity to gather more of this resource
            if unit.carrying[resource_type] < unit.carry_capacity and (tile.resource and tile.resource.amount > 0 or (tile.building and tile.building.name == "Farm" and tile.building.food > 0)):
                # Initialize last gather time if it hasn't been set
                if not hasattr(unit, 'last_gather_time'):
                    unit.last_gather_time = current_time_called

                # Calculate time since last gather action
                time_since_last_gather = current_time_called - unit.last_gather_time
                gatherable_amount = unit.gather_rate * time_since_last_gather

                # Calculate the actual amount the unit can carry
                space_left = unit.carry_capacity - unit.carrying[resource_type]
                amount_to_gather = min(gatherable_amount, space_left)

                # Update unit's carrying load and the resource amount on the tile
                if amount_to_gather > 0:
                    unit.carrying[resource_type] += amount_to_gather
                    if resource_type == "Gold" or resource_type == "Wood":
                        tile.resource.amount -= amount_to_gather
                        # If resource is depleted, remove it from the map
                        if tile.resource.amount <= 0:
                            tile.resource = None
                            self.map.resources[resource_type].remove(unit.target_resource)
                    elif resource_type == "Food" and tile.building.name == "Farm":
                        tile.building.food -= amount_to_gather
                        if tile.building.food <= 0:
                            Building.kill_building(unit.player, tile.building, self.map)                           

                    # Update the last gather time
                    unit.last_gather_time = current_time_called
        else:
            # No resource found; start returning resources if carrying any
            if unit.carrying[resource_type] > 0:
                unit.task = "returning"
        
        # Check if unit's carrying capacity is full or if it needs to return due to lack of resource
        if unit.carrying[resource_type] >= unit.carry_capacity or unit.task == "returning":
            # Locate the nearest drop-off location (Town Center or Camp)
            if resource_type == "Food" and tile.building:
                tile.building.is_farmed = False
            returning_position = None
            for building in unit.player.buildings:
                if building.name in ["Town Center", "Camp"]:
                    returning_position = building.position
                    break

            # Move the unit to the returning position if found
            if returning_position:
                self.move_unit(unit, returning_position[0] - 1, returning_position[1] - 1, current_time_called)

                # Check if unit has reached the drop-off destination to deposit resources
                if abs(unit.position[0] - (returning_position[0] - 1)) < 0.1 and abs(unit.position[1] - (returning_position[1] - 1)) < 0.1:
                    # Deposit resources and reset carrying load
                    building = next(b for b in unit.player.buildings if b.position == returning_position)
                    if isinstance(building, Building):
                        building.drop_point(unit, resource_type)
                    unit.carrying[resource_type] = 0
                    unit.task = None
                    unit.target_resource = None
                    del unit.last_gather_time
            else:
                self.debug_print("No valid building found for resource return.")

    def go_battle(self, unit, enemy_unit, current_time_called):
        unit.task = "going_to_battle"
        unit.target_attack = enemy_unit
        
        # Get the current position of the enemy
        target_x, target_y = enemy_unit.position

        # Check if the target position has changed
        if unit.target_position != (target_x, target_y):
            unit.path = None #reset path --> works but not sure if it's the best way to do it --> calcul is becoming too complex
        
        # Check if the unit is within range to attack
        if abs(unit.position[0] - target_x) < unit.range and abs(unit.position[1] - target_y) < unit.range:
            unit.task = "attacking"
            enemy_unit.is_attacked_by = unit
            enemy_unit.task = "is_attacked"
            self._attack(unit, enemy_unit, current_time_called)
        else:
            self.move_unit(unit, int(target_x), int(target_y), current_time_called)


    
    def _attack(self, unit, enemy_unit, current_time_called):
        if abs(unit.position[0] - enemy_unit.position[0]) < unit.range and abs(unit.position[1] - enemy_unit.position[1]) < unit.range:
            if not hasattr(unit, 'last_hit_time'):
                unit.last_hit_time = 0

            time_since_last_hit = current_time_called - unit.last_hit_time
            if time_since_last_hit >= 1.0:  # Ensure at least 1 second between attacks
                if unit.attack > enemy_unit.hp:
                    enemy_unit.hp = 0
                    Unit.kill_unit(enemy_unit.player, enemy_unit, self.map)
                    unit.task = None
                    del unit.last_hit_time
                    unit.target_attack = None
                else:
                    self.debug_print(f"{unit.name} is attacking {enemy_unit.name}...")
                    enemy_unit.hp -= unit.attack

                unit.last_hit_time = current_time_called
        else:
            self.debug_print("Enemy unit not in range, moving closer...")
            self.go_battle(unit, enemy_unit, current_time_called)

    def construct_building(self, unit, building_type, x, y, player, current_time_called):

        if not self.map.is_area_free(x, y, building_type(player).size):
            if unit.task != "going_to_construction_site": 
                self.debug_print(f"Cannot construct building at ({x}, {y}): area is not free.")
            return
        if not hasattr(unit, 'construction_type'):
            unit.construction_type = building_type
        if not hasattr(unit, 'target_building'):
            unit.target_building = (x, y)

        if unit.task != "going_to_construction_site":
            unit.task = "going_to_construction_site"
            
            adjacent_positions = self.get_adjacent_positions(x, y, building_type(player).size)
            for pos in adjacent_positions:
                if self.map.is_tile_free_for_unit(pos[0], pos[1]):
                    self.move_unit(unit, pos[0], pos[1], current_time_called)
                    break

        if unit.target_position == None:
            unit.task = "constructing"
            for building in player.constructing_buildings:
                if building["position"] == (x, y):
                    building["num_workers"] += 1
                    break
            else:  # If no matching building was found
                player.constructing_buildings.append({
                    "position": (x, y),
                    "num_workers": 1
                })
            self._construct(unit, building_type, x, y, player, current_time_called)

    def _construct(self, unit, building_type, x, y, player, current_time_called):
        if not self.map.is_area_free(x, y, building_type(player).size):
            if unit.task != "going_to_construction_site": 
                self.debug_print(f"Cannot construct building at ({x}, {y}): area is not free.")
            return
        else:
            actual_building_time = 3*building_type(player).build_time / (next((num for (pos, num) in player.constructing_buildings if pos == (x, y)), 1) + 2)
            if not hasattr(unit, 'start_building'):
                unit.start_building = current_time_called
                self.debug_print(f"{unit} started constructing {building_type.__name__} at ({x}, {y}).")

            elif current_time_called - unit.start_building >= actual_building_time:
                Building.spawn_building(player, x, y, building_type, self.map)
                self.debug_print(f"{building_type.__name__} constructed at ({x}, {y}) by {unit}.")
                unit.task = None
                del unit.start_building 