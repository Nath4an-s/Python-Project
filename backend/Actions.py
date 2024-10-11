import heapq
import time
from frontend.Terrain import *

class Action:
    def __init__(self, game_map):
        self.map = game_map
        #self.block_size = 5 #Essayer d'ajouter la granularité plus tard, pour l'instant c'est 1 et ca ne bug pas grace à dikjstra

    def move_unit(self, unit, target_x, target_y):
        # Check if the target destination is valid
        if not self._is_within_bounds(target_x, target_y) or not self.map.is_tile_free(target_x, target_y):
            return False

        # get current/starting position of the unit
        start_x, start_y = unit.position
        unit.target_position = (target_x, target_y)

        # If path is not already constructed, construct it using dijkstra algorithm
        if not hasattr(unit, 'path') or not unit.path:
            unit.path = self.dijkstra_pathfinding((start_x, start_y), (target_x, target_y))

        if not hasattr(unit, 'last_move_time'):
            unit.last_move_time = time.time()

        # calculate time passed since last move of the unit
        current_time = time.time()
        time_since_last_move = current_time - unit.last_move_time

        # make unit move if enough time has passed
        if unit.path and time_since_last_move >= unit.speed:
            next_step = unit.path.pop(0)
            self.map.move_unit(unit, *next_step)
            unit.position = next_step

            # update last move time of the unit 
            unit.last_move_time = current_time

            # If unit reach destination, flush path
            if next_step == (target_x, target_y):
                unit.target_position = None
                unit.path = None
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
            if self._is_within_bounds(nx, ny) and self.map.is_tile_free(nx, ny):
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
