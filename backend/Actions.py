import heapq
from frontend.Terrain import *

class Action:
    def __init__(self, game_map):
        self.map = game_map

    def move_unit(self, unit, target_x, target_y, current_time_called):
        # Check if the target destination is valid
        if not self._is_within_bounds(target_x, target_y) or not self.map.is_tile_free_for_unit(target_x, target_y):
            return False

        # Get current/starting position of the unit
        start_x, start_y = unit.position[0], unit.position[1]
        unit.target_position = (target_x, target_y)

        # If path is not already constructed, construct it using Dijkstra algorithm
        if not hasattr(unit, 'path') or not unit.path:
            unit.path = self.dijkstra_pathfinding((start_x, start_y), (target_x, target_y))

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
                    print("Reached target!")
                    print(unit.position)
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
        unit.last_gathered = resource_type
        # Find the coordinates of the nearest resource of the specified type
        target_x, target_y = Map.find_nearest_resource(self.map, unit.position, resource_type)
        # Find a free tile around the target resource
        adjacent_tiles = self._get_neighbors((target_x, target_y))
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
                print("No free tile found around the resource.")
                return False

        if any(abs(unit.position[0] - tile[0]) < 0.1 and abs(unit.position[1] - tile[1]) < 0.1 for tile in adjacent_tiles):
            unit.task = "gathering"
            self._gather(unit, resource_type, current_time_called)

    def _gather(self, unit, resource_type, current_time_called):
        if unit.carrying[resource_type] < unit.carry_capacity:
            # Initialize the last gather time
            if not hasattr(unit, 'last_gather_time'):
                unit.last_gather_time = current_time_called

            # Calculate time since last gather action
            time_since_last_gather = current_time_called - unit.last_gather_time
            gatherable_amount = unit.gather_rate * time_since_last_gather

            # Calculate the actual amount the unit can carry
            space_left = unit.carry_capacity - unit.carrying[resource_type]
            amount_to_gather = min(gatherable_amount, space_left)

            # Update the unit's inventory and last gather time if there is space left
            if amount_to_gather > 0:
                unit.carrying[resource_type] += amount_to_gather
                unit.last_gather_time = current_time_called

        # Check if unit is full and ready to return resources
        if unit.carrying[resource_type] >= unit.carry_capacity:
            unit.task = "returning"
            
            # Initialize returning_position as None
            returning_position = None

            # Find the closest "TownCenter" or "Camp"
            for building in unit.player.buildings:
                if building.name in ["Town Center", "Camp"]:
                    returning_position = building.position
                    break

            # Move the unit to the returning position if found
            if returning_position:
                self.move_unit(unit, returning_position[0] - 1, returning_position[1] - 1, current_time_called)
                if abs(unit.position[0] - (returning_position[0] - 1)) < 0.1 and abs(unit.position[1] - (returning_position[1] - 1)) < 0.1:
                    unit.player.owned_resources[resource_type] += int(unit.carrying[resource_type])
                    unit.carrying[resource_type] = 0
                    unit.task = None
            else:
                print("No valid building found for resource return.")


