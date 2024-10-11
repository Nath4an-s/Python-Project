import heapq  # For priority queue
from frontend.Terrain import *
import time

class Action:
    def __init__(self, game_map):
        self.map = game_map  # The map is passed in, so we can use it for pathfinding

    def move_unit(self, unit, target_x, target_y):
        # Check if target coordinates are within map bounds
        if not (0 <= target_x < self.map.width and 0 <= target_y < self.map.height):
            print(f"Target ({target_x}, {target_y}) is out of bounds.")
            return False

        # Check if target tile is walkable
        if not self.map.is_tile_free(target_x, target_y):
            print(f"Target ({target_x}, {target_y}) is not walkable.")
            return False

        # Get the unit's current position
        start_x, start_y = unit.position
        unit.target_position = (target_x, target_y)

        # Find the path using A* algorithm
        path = self.a_star_pathfinding((start_x, start_y), (target_x, target_y))

        # Initialize movement timer if not set
        if not hasattr(unit, 'last_move_time'):
            unit.last_move_time = time.time()  # Record the time of the first move

        # Calculate how much time has passed since the last move
        current_time = time.time()
        time_since_last_move = current_time - unit.last_move_time

        # If a path is found, move the unit step by step, respecting the unit's speed
        if path:        
            # Only move if enough time has passed for one step
            if time_since_last_move >= unit.speed:
                # Move only one step along the path
                next_step = path[0]
                step_x, step_y = next_step

                # Move the unit on the map
                self.map.move_unit(unit, step_x, step_y)  # Update unit's position on the map
                unit.position = (step_x, step_y)  # Update unit's internal position
                if step_x == target_x and step_y == target_y:
                    unit.target_position = None
                # Reset the timer after moving
                unit.last_move_time = current_time
                return True
            else:
                return False
        else:
            return False

        
    def a_star_pathfinding(self, start, goal):
        # Priority queue for open nodes
        open_list = []
        heapq.heappush(open_list, (0, start))  # (f, (x, y))
        
        # Dictionaries to store the cost and path
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        
        # Set of visited nodes
        closed_list = set()

        while open_list:
            # Get the node with the lowest f_score
            _, current = heapq.heappop(open_list)

            # If we reached the goal, reconstruct the path
            if current == goal:
                return self.reconstruct_path(came_from, current)
            
            closed_list.add(current)

            # Check for distant nodes far from obstacles and skip some checks for performance
            if self.is_far_from_obstacles(current):
                # Directly move towards goal if far from obstacles
                next_step = self.move_directly_towards_goal(current, goal)
                if next_step:
                    came_from[next_step] = current
                    return [next_step]  # Return direct path when far from obstacles

            # Otherwise, explore the neighbors (up, down, left, right, and diagonals)
            neighbors = self.get_neighbors(current)
            for neighbor in neighbors:
                if neighbor in closed_list:
                    continue

                # Diagonal move cost (can be adjusted if needed)
                tentative_g_score = g_score[current] + (1.414 if abs(neighbor[0] - current[0]) + abs(neighbor[1] - current[1]) == 2 else 1)

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    # This path to the neighbor is better than any previous one
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    
                    if neighbor not in [item[1] for item in open_list]:
                        heapq.heappush(open_list, (f_score[neighbor], neighbor))

        # No path found
        return None

    def is_far_from_obstacles(self, position):
        # Check if the unit is far from obstacles
        x, y = position
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.map.width and 0 <= ny < self.map.height:
                if not self.map.is_tile_free(nx, ny):  # If there's an obstacle within 2 tiles
                    return False
        return True

    def move_directly_towards_goal(self, current, goal):
        # Move directly in a straight line toward the goal if no obstacles nearby
        direction_x = 1 if goal[0] > current[0] else -1 if goal[0] < current[0] else 0
        direction_y = 1 if goal[1] > current[1] else -1 if goal[1] < current[1] else 0

        next_step = (current[0] + direction_x, current[1] + direction_y)
        if self.map.is_tile_free(next_step[0], next_step[1]):
            return next_step
        return None


    def heuristic(self, a, b):
        # Use Euclidean distance heuristic for better diagonal movement estimation
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

    def reconstruct_path(self, came_from, current):
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.reverse()  # Reverse the path to go from start to goal
        return path

    def get_neighbors(self, position):
        x, y = position
        neighbors = []

        # Check all eight directions (up, down, left, right, and diagonals)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), 
                       (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.map.width and 0 <= ny < self.map.height:
                # Only add walkable tiles
                if self.map.is_tile_free(nx, ny):
                    neighbors.append((nx, ny))
        
        return neighbors
