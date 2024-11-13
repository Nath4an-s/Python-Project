#Actions.py

import heapq

from frontend.Terrain import *
from logger import debug_print
from Units import *

class Action:
    def __init__(self, game_map):
        self.map = game_map
        self.debug_print = debug_print
        self.debug_print = debug_print

    def move_unit(self, unit, target_x, target_y, current_time_called):
        # Check if the target destination is valid
        if not self._is_within_bounds(target_x, target_y) or not self.map.is_tile_free_for_unit(int(target_x), int(target_y)):
            self.debug_print("Invalid target destination.")
            self.debug_print(self.map.is_tile_free_for_unit(int(target_x), int(target_y)))
            self.debug_print(self._is_within_bounds(target_x, target_y))
            self.debug_print(self.map.grid[int(target_y)][int(target_x)].building)
            self.debug_print(self.map.grid[int(target_y)][int(target_x)].building.is_walkable())

            return False

        # Get current/starting position of the unit
        start_x, start_y = int(unit.position[0]), int(unit.position[1])
        unit.target_position = (target_x, target_y)

        # If path is not already constructed, construct it using Dijkstra algorithm
        if not hasattr(unit, 'path') or not unit.path:
            unit.path = self.dijkstra_pathfinding((int(start_x), int(start_y)), (target_x, target_y))

        # Assuming 'unit' has a position attribute as a tuple of floats
        if not hasattr(unit, 'last_move_time'):
            unit.last_move_time = current_time_called

        # Calculate time passed since last move of the unit
        current_time = current_time_called
        time_since_last_move = current_time - unit.last_move_time

        # Calculate the distance the unit can move based on its speed
        distance_to_move = unit.speed * time_since_last_move
        # Make unit move if enough time has passed
        if unit.path and distance_to_move > 0:
            # Get the next target position in the path
            next_step = unit.path[0]

            # Check if the next step is still free (dynamic obstacle detection)
            if not self.map.is_tile_free_for_unit(next_step[0], next_step[1]):
                # Recalculate path if the next step is blocked
                unit.path = self.dijkstra_pathfinding((int(start_x), int(start_y)), (target_x, target_y))
                if not unit.path:
                    self.debug_print("Path not found or obstructed")
                    return False # No valid path found

            # Calculate direction vector to the next step
            direction_x = next_step[0] - unit.position[0]
            direction_y = next_step[1] - unit.position[1]

            # Calculate the length of the direction vector
            length = (direction_x**2 + direction_y**2) ** 0.5

            if length > 0:
                # Normalize the direction vector
                normalized_x = direction_x / length
                normalized_y = direction_y / length

                # Move the unit a fraction of the distance based on its speed
                new_position = (
                    unit.position[0] + normalized_x * distance_to_move,
                    unit.position[1] + normalized_y * distance_to_move
                )

                # Snap to the target if within a small threshold
                if abs(new_position[0] - target_x) <= 1 and abs(new_position[1] - target_y) <= 1: #maybe we'll try to improve this
                    unit.position = (target_x, target_y)
                    unit.path = None
                    unit.target_position = None
                    Map.move_unit(self.map, unit, int(unit.position[0]), int(unit.position[1]), int(start_x), int(start_y))
                    self.debug_print("Reached target!")
                    self.debug_print(unit.position)
                    return True
                else:
                    unit.position = new_position

                # Check if the unit has reached the next step
                if ((unit.position[0] - next_step[0]) ** 2 + 
                    (unit.position[1] - next_step[1]) ** 2) < (distance_to_move ** 2):
                    # The unit has reached the next step, so remove it from the path
                    unit.position = next_step
                    unit.path.pop(0)

            # Update the last move time
            unit.last_move_time = current_time
            Map.move_unit(self.map, unit, int(unit.position[0]), int(unit.position[1]), int(start_x), int(start_y))

            return True
        return False


    def dijkstra_pathfinding(self, start, goal):
        open_list = []
        heapq.heappush(open_list, (0, start))  # add a starting node to the open list

        came_from = {}  # stock where each node came from
        cost_so_far = {start: 0}  # stock costs for each node

        closed_list = set()  # already processed nodes

        while open_list:
            _, current = heapq.heappop(open_list)  # Get lowest cost node from open list

            # If destination reached, reconstruct path
            if current == goal:
                return self._reconstruct_path(came_from, current)

            closed_list.add(current)

            neighbors = self._get_neighbors(current)
            for neighbor in neighbors:
                if neighbor in closed_list:
                    continue

                new_cost = cost_so_far[current] + self._move_cost(current, neighbor)

                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost
                    heapq.heappush(open_list, (priority, neighbor))
                    came_from[neighbor] = current

        return None # no path found

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
            target = Map.find_nearest_resource(self.map, unit.position, resource_type, unit.player)
            if target is not None:
                unit.target_position = target
            else:
                self.debug_print(f"No {resource_type} resources found.")
                return False
            # Find a free tile around the target resource
            adjacent_tiles = self._get_neighbors((unit.target_position[0], unit.target_position[1]))
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
                unit.target_position = target
            else:
                self.debug_print(f"No {resource_type} resources found.")
                unit.task = None
                unit.target_position = None
                return False
            # Move to the target tile if not already there
            if not (abs(unit.position[0] - unit.target_position[0]) < 0.1 and abs(unit.position[1] - unit.target_position[1]) < 0.1):
                # Update unit's position by calling move_unit
                self.move_unit(unit, unit.target_position[0], unit.target_position[1], current_time_called)
                unit.task = "marching"
            else:
                unit.task = "gathering"
                self._gather(unit, resource_type, current_time_called)

        else:
            self.debug_print("Invalid resource type.")
            return False

    def _gather(self, unit, resource_type, current_time_called):
        tile = self.map.grid[unit.target_position[1]][unit.target_position[0]] if unit.target_position is not None else None
        # Check if there is a resource on the target tile and it's the correct type
        if (tile and tile.resource and tile.resource.type == resource_type) or (resource_type == "Food" and tile.building and tile.building.name == "Farm"):
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
                    elif resource_type == "Food" and tile.building.name == "Farm":
                        tile.building.food -= amount_to_gather
                        if tile.building.food <= 0:
                            tile.building = None

                    # Update the last gather time
                    unit.last_gather_time = current_time_called
        else:
            # No resource found; start returning resources if carrying any
            if unit.carrying[resource_type] > 0:
                unit.task = "returning"
                self.debug_print("No resource found, returning to deposit resources.")
        
        # Check if unit's carrying capacity is full or if it needs to return due to lack of resource
        if unit.carrying[resource_type] >= unit.carry_capacity or unit.task == "returning":
            # Locate the nearest drop-off location (Town Center or Camp)
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
                    unit.player.owned_resources[resource_type] += int(unit.carrying[resource_type])
                    unit.carrying[resource_type] = 0
                    unit.task = None
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

        # Move the unit toward the enemy's current position
        self.move_unit(unit, int(target_x), int(target_y), current_time_called)
        
        # Check if the unit is within range to attack
        if abs(unit.position[0] - target_x) < unit.range and abs(unit.position[1] - target_y) < unit.range:
            unit.task = "attacking"
            enemy_unit.is_attacked_by = unit
            enemy_unit.task = "is_attacked"
            self._attack(unit, enemy_unit, current_time_called)


    
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
                else:
                    self.debug_print(f"{unit.name} is attacking {enemy_unit.name}...")
                    enemy_unit.hp -= unit.attack

                unit.last_hit_time = current_time_called
        else:
            self.debug_print("Enemy unit not in range, moving closer...")
            self.go_battle(unit, enemy_unit, current_time_called)