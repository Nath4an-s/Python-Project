import random
import math
import curses

from backend.Starter_File import GameMode

class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[Tile(x, y) for y in range(height)] for x in range(width)]  # Ensure this is correct
        self.resources = {"Gold": [], "Wood": []}
        self.generate_map()

    def generate_map(self):
        
        self.generate_resources()

    def generate_resources(self):
        resource_symbols = {"Wood": "W", "Gold": "G"}

        num_resources = int(self.width * self.height * 0.03)  # 3% of the map as resource tiles

        # Gold Generation
        num_gold = int(num_resources * 0.3)  # 30% of resource tiles as gold

        # Check if gamemode is a starter_file and then adjust gold generation based on the mode
        if GameMode == "Utopia":
            # Utopia: Gold is randomly placed
            for _ in range(num_gold):
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                tile = self.grid[y][x]

                if tile.resource is None:  # Ensure no other resources overwrite the tile
                    resource_amount = random.randint(50, 200)
                    resource = Gold()
                    tile.resource = resource
                    self.resources["Gold"].append((x, y))  # Store the position of Gold resources


        elif GameMode == "Gold Rush":
            # Gold Rush: All gold resources are concentrated in a smaller circle within a larger circle
            center_x = self.width // 2
            center_y = self.height // 2

            # Define a larger radius and a smaller radius for gold placement
            large_radius = min(self.width, self.height) // 10
            small_radius = large_radius // 1  # Smaller radius for denser gold placement

            for _ in range(num_gold):
                # Generate coordinates within the smaller circle inside the larger circle
                while True:
                    angle = random.uniform(0, 2 * math.pi)
                    distance = random.uniform(0, small_radius)
                    x = int(center_x + distance * math.cos(angle))
                    y = int(center_y + distance * math.sin(angle))

                    # Ensure the coordinates are within the grid bounds and within the larger circle
                    if (x - center_x) ** 2 + (y - center_y) ** 2 <= large_radius ** 2:
                        x = max(0, min(x, self.width - 1))
                        y = max(0, min(y, self.height - 1))
                        tile = self.grid[y][x]

                        if tile.resource is None:  # Ensure no other resources overwrite the tile
                            resource_amount = random.randint(50, 200)
                            resource = Gold()
                            tile.resource = resource
                            self.resources["Gold"].append((x, y))  # Store the position of Gold resources
                        break  # Exit the loop once a valid position is found


        # Wood Generation
        num_wood = (num_resources - num_gold) // 10  # Remaining resource tiles as wood --> increase the '15' for less forests
        for _ in range(num_wood):
            # Generate a random forest
            forest_size = random.randint(20, 50)
            start_x = random.randint(0, self.width - 1)
            start_y = random.randint(0, self.height - 1)

            # Create an irregular forest by deciding tile placement randomly
            x, y = start_x, start_y
            tile = self.grid[y][x]
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

            for _ in range(forest_size):
                # Choose a random direction
                dx, dy = random.choice(directions)
                x += dx
                y += dy

                # Ensure the forest fits within the grid boundaries
                x = max(0, min(x, self.width - 1))
                y = max(0, min(y, self.height - 1))
                tile = self.grid[y][x]

                if tile.resource is None:  # Avoid overwriting existing resources
                    resource_amount = random.randint(50, 200)
                    resource = Wood()
                    tile.resource = resource
                    self.resources["Wood"].append((x, y))  # Store Wood resource position


    def is_tile_free(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            tile = self.grid[y][x]
            is_free = tile.resource is None and tile.building is None and tile.unit == []
            if not is_free:
                pass
            return is_free
        return False
    
    def is_tile_free_for_unit(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            tile = self.grid[y][x]
            is_free = tile.resource is None and tile.building is None
            if not is_free:
                pass
            return is_free
        return False
    
    def is_area_free(self, x, y, size):
        for i in range(size):
            for j in range(size):
                if not self.is_tile_free(x + i, y + j):
                    return False
        return True

    def place_building(self, x, y, building):
        if self.is_area_free(x, y, building.size):
            building.x = x
            building.y = y
            for i in range(building.size):
                for j in range(building.size):
                    self.grid[y + j][x + i].building = building

    def place_unit(self, x, y, unit):
        if 0 <= x < self.width and 0 <= y < self.height:
            tile = self.grid[y][x]
            tile.unit.append(unit)  # Place the unit on the tile

    def remove_unit(self, x, y, unit):
        tile = self.grid[y][x]
        if tile.unit is not None:
            tile.unit.remove(unit)  # Remove the unit from the tile
        else:
            print(f"No unit on tile ({x}, {y})")

    def move_unit(self, unit, target_x, target_y, start_x, start_y):
        if 0 <= target_x < self.width and 0 <= target_y < self.height:
            self.remove_unit(start_x, start_y, unit)
            self.place_unit(target_x, target_y, unit)
        else:
            print(f"Target ({target_x}, {target_y}) is out of bounds.")
            
    def get_viewport(self, top_left_x, top_left_y, viewport_width, viewport_height):
        viewport = []
        for y in range(top_left_y, min(top_left_y + viewport_height, self.height)):
            row = []
            for x in range(top_left_x, min(top_left_x + viewport_width, self.width)):
                row.append(self.grid[y][x])
            viewport.append(row)
        return viewport

    def display_viewport(self, stdscr, top_left_x, top_left_y, viewport_width, viewport_height, changed_tiles=None):
        if changed_tiles is None:
            changed_tiles = set()

        # Initialize colors inside display_viewport (no need to change main)
        self.setup_colors()

        for y in range(viewport_height):
            for x in range(viewport_width):
                map_x = top_left_x + x
                map_y = top_left_y + y

                if 0 <= map_x < self.width and 0 <= map_y < self.height:
                    tile = self.grid[map_y][map_x]
                    if (map_x, map_y) in changed_tiles or not changed_tiles:
                        if tile.building:
                            # Determine the color based on the building's owner
                            player = tile.building.player.name
                            if player == "Player 1":
                                color_pair = curses.color_pair(1)  # Blue
                            elif player == "Player 2":
                                color_pair = curses.color_pair(2)  # Red
                            elif player == "Player 3":
                                color_pair = curses.color_pair(3)  # Purple
                            else:
                                color_pair = curses.color_pair(0)  # Default

                            stdscr.addstr(y, x * 2, str(tile.building), color_pair)  # Display building with color
                        elif tile.unit:
                            # Determine the color based on the unit's owner
                            for unit in tile.unit:
                                player = unit.player.name
                                if player == "Player 1":
                                    color_pair = curses.color_pair(1)  # Blue
                                elif player == "Player 2":
                                    color_pair = curses.color_pair(2)  # Red
                                elif player == "Player 3":
                                    color_pair = curses.color_pair(3)  # Purple
                                else:
                                    color_pair = curses.color_pair(0)  # Default

                                stdscr.addstr(y, x * 2, str(unit), color_pair)  # Display unit with color
                        else:
                            stdscr.addstr(y, x * 2, str(tile))  # Display regular tile content

        stdscr.refresh()

    def setup_colors(self):
        curses.start_color()
        # Define color pairs: pair number, foreground color, background color
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)   # Player 1 (blue)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # Player 2 (red)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # Player 3 (purple)

    def find_nearest_resource(self, start_position, resource_type):
        min_distance = float('inf')
        nearest_resource = None

        # Iterate through each resource position for the specified type
        for resource_x, resource_y in self.resources[resource_type]:
            distance = abs(start_position[0] - resource_x) + abs(start_position[1] - resource_y)

            if distance < min_distance:
                min_distance = distance
                nearest_resource = (resource_x, resource_y)

        return nearest_resource  # Returns coordinates (x, y) of nearest resource

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.resource = None
        self.building = None
        self.unit = []

    def __str__(self):
        if self.unit:
            return getattr(self.unit, 'symbol', '?')
        elif self.building:
            return getattr(self.building, 'symbol', '?')
        elif self.resource:
            return getattr(self.resource, 'symbol', '?')
        else:
            return "." 


# Resource Class
class Resource:
    def __init__(self, resource_type, amount, symbol="R"):
        self.type = resource_type  # "Wood", "Gold", "Food"
        self.amount = amount
        self.symbol = symbol

    def gather(self, amount):
        gathered = min(self.amount, amount)
        self.amount -= gathered
        return gathered


# Wood Resource Class
class Wood(Resource):
    def __init__(self):
        super().__init__(resource_type="Wood", amount=100, symbol="W")  # 100 per tile (tree)


"""# Food Resource Class
class Food(Resource):
    def __init__(self):
        super().__init__(resource_type="Food", amount=300, symbol="F")  # 300 per farm
""" # Not used, food is in the farm building

# Gold Resource Class
class Gold(Resource):
    def __init__(self):
        super().__init__(resource_type="Gold", amount=800, symbol="G")  # 800 per tile
