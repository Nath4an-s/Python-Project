import pygame
from pygame.locals import FULLSCREEN
from pygame.locals import HIDDEN
import threading
import queue as Queue
from pathlib import Path
import time
import traceback

class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.offset_x = 0
        self.offset_y = 0

    def apply(self, x, y):
        return x - self.offset_x, y - self.offset_y

    def update(self, target_x, target_y, map_width, map_height):
        min_x = -(self.width // 2)
        min_y = -(self.height // 2)
        max_x = max(min_x, map_width - self.width // 2)
        max_y = max(min_y, map_height - self.height // 2)

        self.offset_x = max(min_x, min(target_x - self.width // 2, max_x))
        self.offset_y = max(min_y, min(target_y - self.height // 2, max_y))

    def move(self, dx, dy, map_width, map_height):
        min_x = -(self.width // 2)
        min_y = -(self.height // 2)
        max_x = map_width - (self.width // 2)
        max_y = map_height - (self.height // 2)

        self.offset_x = max(min_x, min(self.offset_x + dx, max_x))
        self.offset_y = max(min_y, min(self.offset_y + dy, max_y))

def tint_image(image, color):
    """Tint an image with the given color."""
    tinted_image = image.copy()
    tinted_image.fill(color + (0,), special_flags=pygame.BLEND_RGBA_MULT)
    return tinted_image

class GUI(threading.Thread):
    def __init__(self, data_queue):
        super().__init__()
        self.data_queue = data_queue
        self.running = False
        self.game_data = None

        self.TILE_WIDTH = 64
        self.TILE_HEIGHT = 32
        self.WINDOW_WIDTH = 800
        self.WINDOW_HEIGHT = 600

        self.screen = None
        self.clock = None
        self.font = None

        self.camera = Camera(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        self.last_fps_update = 0
        self.fps_text = None
        self.fps_refresh_interval = 0.5

        self.tile_polygon = None
        self.pre_rendered_map = None

        self.building_images = {}
        self.IMAGES = {}
        self.villager_images = {}
        self.swordman_images = {}
        self.show_resources = False
        
        self.PLAYER_COLORS = {
            1: (0, 0, 255),    # Blue
            2: (255, 0, 0),    # Red
            3: (0, 100, 0),    # Green
            4: (255, 255, 0),  # Yellow
            5: (128, 0, 128),  # Purple
            6: (0, 255, 255),  # Cyan
            7: (255, 165, 0),  # Orange
            8: (128, 128, 128),# Gray
        }
        
        self.COLORS = {
            "Wood": (34, 139, 34),   # Dark green for wood
            "Gold": (255, 215, 0),   # Gold color
            "Soil": (0, 255, 0)      # Green for soil
        }

        # Timing for mini-map updates
        self.last_mini_map_update = time.time()
        self.mini_map_update_interval = 50  # Update every 50 seconds
        # Initialize mini-map surface
        self.mini_map_surface = None

    def flip_image_horizontally(self, image):
        return pygame.transform.flip(image, True, False)

    def setup_paths(self):
        self.BASE_PATH = Path(__file__).resolve().parent.parent
        self.RESOURCES_PATH = self.BASE_PATH / "assets" / "resources"
        self.BUILDINGS_PATH = self.BASE_PATH / "assets" / "buildings"

        assert self.RESOURCES_PATH.exists(), f"Resources directory {self.RESOURCES_PATH} does not exist."
        assert self.BUILDINGS_PATH.exists(), f"Buildings directory {self.BUILDINGS_PATH} does not exist."

    def load_image(self, file_path):
        try:
            return pygame.image.load(file_path).convert_alpha()
        except pygame.error as e:
            print(f"Error loading image {file_path}: {e}")
            return pygame.Surface((self.TILE_WIDTH, self.TILE_HEIGHT))

    def load_resources(self):
        # Load basic images
        self.IMAGES = {
            "Wood": self.load_image(self.RESOURCES_PATH / "tree.png"),
            "Gold": self.load_image(self.RESOURCES_PATH / "gold.png"),
            "Soil": self.load_image(self.RESOURCES_PATH / "soil.png"),
        }


        for player_id, color in self.PLAYER_COLORS.items():
            #self.PLAYER_COLORS[player_id] = color + (200,)  # Add alpha channel
            self.villager_images[player_id] = {}
            self.swordman_images[player_id] = {}
            
            for unit_type, images in self.villager_images.items():
                for direction, frames in images.items():
                    self.villager_images[unit_type][direction] = [tint_image(frame, self.unit_colors["villager"]) for frame in frames]

            for unit_type, images in self.swordman_images.items():
                for direction, frames in images.items():
                    self.swordman_images[unit_type][direction] = [tint_image(frame, self.unit_colors["swordman"]) for frame in frames]
                    
        # Load and scale building images
        building_types = {
            "TownCenter": (256, 256),
            "Barracks": (self.TILE_WIDTH * 3.5, self.TILE_HEIGHT * 6),
            "House": (self.TILE_WIDTH * 2, self.TILE_HEIGHT * 4),
            "Rubble": (64, 64),
            "Stable": (self.TILE_WIDTH * 3, self.TILE_HEIGHT * 6),
            "ArcheryRange": (self.TILE_WIDTH * 3, self.TILE_HEIGHT * 6),
            "Camp": (self.TILE_WIDTH * 2, self.TILE_HEIGHT * 4),
            "Farm": (self.TILE_WIDTH * 2, self.TILE_HEIGHT * 2),
            "Keep": (64, 64),
        }

        for building_type, size in building_types.items():
            image = self.load_image(self.BUILDINGS_PATH / f"{building_type.lower()}.png")
            self.building_images[building_type] = pygame.transform.scale(image, size)



        self.villager_images = {
            "walking": {
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "walk" / f"Villagerwalk{i:03}.png")
                    for i in range(1, 15)
                ],
                "north": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "walk" / f"Villagerwalk{i:03}.png")
                    for i in range(61, 75)
                ],
                "west": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "walk" / f"Villagerwalk{i:03}.png")
                    for i in range(31, 45)
                ],
                "east": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "walk" / f"Villagerwalk{i:03}.png")
                    )
                    for i in range(31, 45)
                ],
                "northeast": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "walk" / f"Villagerwalk{i:03}.png")
                    )
                    for i in range(46, 60)
                ],
                "northwest": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "walk" / f"Villagerwalk{i:03}.png")
                    for i in range(46, 60) #fait
                ],
                "southwest": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "walk" / f"Villagerwalk{i:03}.png")
                    for i in range(16, 30) #fait
                ],
                "southeast": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "walk" / f"Villagerwalk{i:03}.png")
                    )
                    for i in range(16, 30)
                ],
            },
            "attacking": {
                "north": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "Attack" / f"Villagerattack{i:03}.png")
                    for i in range(61, 75)
                ],
                "east": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "Attack" / f"Villagerattack{i:03}.png")
                    )
                    for i in range(31, 45)
                ],
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "Attack" / f"Villagerattack{i:03}.png")
                    for i in range(1, 15)
                ],
                "west": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "Attack" / f"Villagerattack{i:03}.png")
                    for i in range(31, 45)
                ],
                "northeast": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "Attack" / f"Villagerattack{i:03}.png")
                    )
                    for i in range(46, 60)
                ],
                "northwest": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "Attack" / f"Villagerattack{i:03}.png")
                    for i in range(46, 60)
                ],
                "southeast": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "Attack" / f"Villagerattack{i:03}.png")
                    )
                    for i in range(16, 30)
                ],
                "southwest": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "Attack" / f"Villagerattack{i:03}.png")
                    for i in range(16, 30)
                ],
            },
            "dying": [
                self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "Die" / f"Villagerdie{i:03}.png")
                for i in range(1, 15)
            ],
            "gathering": {
                "north": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "FarmingVillager" / "Farm" / "Attack" / f"Villageract{i:03}.png")
                    for i in range(61, 75)
                ],
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "FarmingVillager" / "Farm" / "Attack" / f"Villageract{i:03}.png")
                    for i in range(1, 15)
                ],
                "west": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "FarmingVillager" / "Farm" / "Attack" / f"Villageract{i:03}.png")
                    for i in range(31, 45)
                ],
                "east": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "FarmingVillager" / "Farm" / "Attack" / f"Villageract{i:03}.png")
                    )
                    for i in range(31, 45)
                ],
                "northeast": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "FarmingVillager" / "Farm" / "Attack" / f"Villageract{i:03}.png")
                    )
                    for i in range(46, 60)
                ],
                "northwest": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "FarmingVillager" / "Farm" / "Attack" / f"Villageract{i:03}.png")
                    for i in range(46, 60)
                ],
                "southeast": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "FarmingVillager" / "Farm" / "Attack" / f"Villageract{i:03}.png")
                    )
                    for i in range(16, 30)
                ],
                "southwest": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "FarmingVillager" / "Farm" / "Attack" / f"Villageract{i:03}.png")
                    for i in range(16, 30) #fait
                ],
            },
            "idle": {
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "Stand" / f"Villagerstand{i:03}.png")
                    for i in range(17, 30)
                ],
            },
        }


        
        
        self.swordman_images = {
           "walking": {
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" / "walk" / f"Halbadierwalk{i:03}.png")
                    for i in range(1, 10)
                ],
                "north": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" / "walk" / f"Axethrowerwalk{i:03}.png")
                    for i in range(61, 75)
                ],
                "west": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" / "walk" / f"Axethrowerwalk{i:03}.png")
                    for i in range(31, 45)
                ],
                "east": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" / "walk" / f"Axethrowerwalk{i:03}.png")
                    )
                    for i in range(31, 45)
                ],
                "northeast": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" / "walk" / f"Axethrowerwalk{i:03}.png")
                    )
                    for i in range(46, 60)
                ],
                "northwest": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" / "walk" / f"Axethrowerwalk{i:03}.png")
                    for i in range(46, 60) #fait
                ],
                "southwest": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" / "walk" / f"Axethrowerwalk{i:03}.png")
                    for i in range(16, 30) #fait
                ],
                "southeast": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" / "walk" / f"Axethrowerwalk{i:03}.png")
                    )
                    for i in range(16, 30)
                ],
            },
            "attacking": {
                "north": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Swordman" / "Attack" / f"Axethrowerattack{i:03}.png")
                    for i in range(1, 6)
                ],
                "east": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Swordman" / "Attack" / f"Axethrowerattack{i:03}.png")
                    for i in range(6, 9)
                ],
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Swordman" / "Attack" / f"Axethrowerattack{i:03}.png")
                    for i in range(9, 13)
                ],
                "west": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Swordman" / "Attack" / f"Axethrowerattack{i:03}.png")
                    for i in range(13, 16)
                ],
            },
            "dying": {
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Swordman" / "Die" / f"Axethrowerdie{i:03}.png")
                    for i in range(9, 13)
                ],
            },
            "idle": {
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Swordman" / "Stand" / f"Axethrowerstand{i:03}.png")
                    for i in range(9, 13)  
                ],
            },
        }


        self.archer_images = {
            "walking": {
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Archer" / "walk" / f"Archerwalk{i:03}.png")
                    for i in range(1, 10)
                ],
                "north": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Archer" / "walk" / f"Archerwalk{i:03}.png")
                    for i in range(41, 50)
                ],
                "west": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Archer" / "walk" / f"Archerwalk{i:03}.png")
                    for i in range(21, 30)
                ],
                "east": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Archer" / "walk" / f"Archerwalk{i:03}.png")
                    )
                    for i in range(21, 30)
                ],
                "northeast": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Archer" / "walk" / f"Archerwalk{i:03}.png")
                    )
                    for i in range(31, 40)
                ],
                "northwest": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Archer" / "walk" / f"Archerwalk{i:03}.png")
                    for i in range(31, 40) #fait
                ],
                "southwest": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Archer" / "walk" / f"Archerwalk{i:03}.png")
                    for i in range(11, 20) #fait
                ],
                "southeast": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Archer" / "walk" / f"Archerwalk{i:03}.png")
                    )
                    for i in range(11, 20)
                ],
            },
            "attacking": {
                "north": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Archer" / "Attack" / f"Archerattack{i:03}.png")
                    for i in range(1, 6)
                ],
                "east": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Archer" / "Attack" / f"Archerattack{i:03}.png")
                    for i in range(6, 9)
                ],
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Archer" / "Attack" / f"Archerattack{i:03}.png")
                    for i in range(9, 13)
                ],
                "west": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Archer" / "Attack" / f"Archerattack{i:03}.png")
                    for i in range(13, 16)
                ],
            },
            "dying": {
                
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Archer" / "Die" / f"Archerdie{i:03}.png")
                    for i in range(9, 13)
                ],
            },
            "idle": {
               
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Archer" / "Stand" / f"Archerstand{i:03}.png")
                    for i in range(9, 13)
                ],
            },
        }

        '''
        self.horseman_images = {
            "walking": {
                "north": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Walk" / f"Horsemanwalk{i:03}.png")
                    for i in range(1, 6)
                ],
                "east": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Walk" / f"Horsemanwalk{i:03}.png")
                    for i in range(6, 9)
                ],
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Walk" / f"Horsemanwalk{i:03}.png")
                    for i in range(9, 13)
                ],
                "west": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Walk" / f"Horsemanwalk{i:03}.png")
                    for i in range(13, 16)
                ],
            },
            "attacking": {
                "north": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Attack" / f"Horsemanattack{i:03}.png")
                    for i in range(1, 6)
                ],
                "east": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Attack" / f"Horsemanattack{i:03}.png")
                    for i in range(6, 9)
                ],
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Attack" / f"Horsemanattack{i:03}.png")
                    for i in range(9, 13)
                ],
                "west": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Attack" / f"Horsemanattack{i:03}.png")
                    for i in range(13, 16)
                ],
            },
            "dying": {
                "north": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Die" / f"Horsemandie{i:03}.png")
                    for i in range(1, 6)
                ],
                "east": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Die" / f"Horsemandie{i:03}.png")
                    for i in range(6, 9)
                ],
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Die" / f"Horsemandie{i:03}.png")
                    for i in range(9, 13)
                ],
                "west": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Die" / f"Horsemandie{i:03}.png")
                    for i in range(13, 16)
                ],
            },
            "idle": {
                "north": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Stand" / f"Horsemanstand{i:03}.png")
                    for i in range(1, 6)
                ],
                "east": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Stand" / f"Horsemanstand{i:03}.png")
                    for i in range(6, 9)
                ],
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Stand" / f"Horsemanstand{i:03}.png")
                    for i in range(9, 13)
                ],
                "west": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Stand" / f"Horsemanstand{i:03}.png")
                    for i in range(13, 16)
                ],
            },
        }
        '''
        self.iconwod = self.load_image(self.RESOURCES_PATH / "iconwood.png")
        self.icongold = self.load_image(self.RESOURCES_PATH / "icongold.png")

        self.IMAGES["Gold"] = pygame.transform.scale(self.IMAGES["Gold"], (self.TILE_WIDTH, self.TILE_HEIGHT))
        self.IMAGES["Wood"] = pygame.transform.scale(self.IMAGES["Wood"], (self.TILE_WIDTH, self.TILE_HEIGHT))

    def cart_to_iso(self, cart_x, cart_y):
        iso_x = (cart_x - cart_y) * (self.TILE_WIDTH // 2)
        iso_y = (cart_x + cart_y) * (self.TILE_HEIGHT // 2)
        return iso_x, iso_y

    def handle_events(self):
        """Handle all pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F12:
                    self.running = False
                elif event.key == pygame.K_F2:
                    self.show_resources = not self.show_resources
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mini_map_click(event)


    def handle_keyboard_input(self):
        keys = pygame.key.get_pressed()
        move_speed = 10

        if keys[pygame.K_LEFT]:
            self.camera.move(-move_speed, 0, self.game_data.map.width * self.TILE_WIDTH, self.game_data.map.height * self.TILE_HEIGHT)
        if keys[pygame.K_RIGHT]:
            self.camera.move(move_speed, 0, self.game_data.map.width * self.TILE_WIDTH, self.game_data.map.height * self.TILE_HEIGHT)
        if keys[pygame.K_UP]:
            self.camera.move(0, -move_speed, self.game_data.map.width * self.TILE_WIDTH, self.game_data.map.height * self.TILE_HEIGHT)
        if keys[pygame.K_DOWN]:
            self.camera.move(0, move_speed, self.game_data.map.width * self.TILE_WIDTH, self.game_data.map.height * self.TILE_HEIGHT)

    def display_fps(self):
        current_time = time.time()
        if current_time - self.last_fps_update >= self.fps_refresh_interval:
            fps = int(self.clock.get_fps())
            self.fps_text = self.font.render(f'FPS: {fps}', True, (255, 255, 255))
            self.last_fps_update = current_time

        if self.fps_text:
            fps_rect = self.fps_text.get_rect(topright=(self.WINDOW_WIDTH - 10, 10))
            self.screen.blit(self.fps_text, fps_rect)

    def pre_render_map(self):
        map_width_px = (self.game_data.map.width + 1) * self.TILE_WIDTH
        map_height_px = (self.game_data.map.height + 1) * self.TILE_HEIGHT
        self.pre_rendered_map = pygame.Surface((map_width_px, map_height_px), pygame.SRCALPHA)
        self.trees_drawn = {}

        for y in range(self.game_data.map.height):
            for x in range(self.game_data.map.width):
                # Convertir en coordonnées isométriques
                iso_x, iso_y = self.cart_to_iso(x, y)
                tile_x = iso_x + (self.game_data.map.width * self.TILE_WIDTH // 2)
                tile_y = iso_y

                # Dessiner les tuiles
                transformed_polygon = [
                    (tile_x + point[0], tile_y + point[1]) for point in self.tile_polygon
                ]
                pygame.draw.polygon(self.pre_rendered_map, (0, 124, 0), transformed_polygon)
                pygame.draw.lines(self.pre_rendered_map, (200, 200, 200), True, transformed_polygon, 1)

                # Récupérer les informations de la tuile
                tile = self.game_data.map.grid[y][x]
                if tile and tile.resource:
                    # Ajuster les coordonnées pour placer les ressources
                    screen_x = tile_x - self.TILE_WIDTH // 2  # Ajustement pour centrer horizontalement
                    screen_y = tile_y - self.TILE_HEIGHT // 2  # Ajustement pour l'altitude

                    if tile.resource.type == "Wood":
                        image = self.IMAGES["Wood"]
                        self.pre_rendered_map.blit(image, (screen_x, screen_y))

                    elif tile.resource.type == "Gold":
                        image = self.IMAGES["Gold"]
                        self.pre_rendered_map.blit(image, (screen_x, screen_y))


    def render_isometric_map(self):
        if not self.pre_rendered_map:
            self.pre_render_map()

        visible_rect = pygame.Rect(
            self.camera.offset_x, self.camera.offset_y,
            self.WINDOW_WIDTH, self.WINDOW_HEIGHT
        )

        self.screen.blit(self.pre_rendered_map, (0, 0), visible_rect)

        entities = []

        # Collect player units and buildings
        for player in self.game_data.players:
            for unit in player.units:
                iso_x, iso_y = self.cart_to_iso(unit.position[0], unit.position[1])
                unit_x = iso_x + (self.game_data.map.width * self.TILE_WIDTH // 2)
                unit_y = iso_y
                if visible_rect.collidepoint(unit_x, unit_y):
                    entities.append((unit_x, unit_y, "unit", unit))

            for building in player.buildings:
                bottom_right_x = building.position[0] + building.size - 2
                bottom_right_y = building.position[1] + building.size

                iso_x, iso_y = self.cart_to_iso(bottom_right_x, bottom_right_y)
                building_x = iso_x + (self.game_data.map.width * self.TILE_WIDTH // 2)
                building_y = iso_y

                if visible_rect.collidepoint(building_x, building_y):
                    entities.append((building_x, building_y, "building", building))

        # Sort entities by their depth (y + x for isometric rendering)
        entities.sort(key=lambda e: e[0] + e[1])

        # Render all entities
# Render all entities
        for x, y, entity_type, obj in entities:
            screen_x = x - self.camera.offset_x
            screen_y = y - self.camera.offset_y
            image = None

            if entity_type == "unit":
                # Assurez-vous que chaque unité a un attribut `sprite`, `state`, et `direction`
                unit_type = obj.sprite  # Le type d'unité (ex. "villager", "swordman", "archer")
                state = obj.task  # Par exemple, "idle" comme état par défaut
                direction = obj.direction  # La direction de l'unité (ex. "north", "south", "west", "east")
                if obj.is_moving == True:
                    state = "walking"  
                else :
                    if state is None:
                        obj.direction = "south"
                        state = "idle"
                    if state == "marching" or  state == "going_to_battle" or  state == "going_to_construction_site" or obj.is_moving == True:
                        state = "walking"   

                # Ralentir l'animation (par exemple, changer de frame tous les 5 rendus)
                animation_speed = 100  # Ajustez cette valeur pour contrôler la vitesse
                obj.frame_counter += 1
                if obj.frame_counter >= animation_speed:
                    obj.current_frame += 1  # Passe à la frame suivante
                    obj.frame_counter = 0  # Réinitialise le compteur

                # Attribution du sprite correspondant à chaque type d'unité
                if unit_type == "villager":
                    if state in self.villager_images and direction in self.villager_images[state]:
                        images = self.villager_images[state][direction]
                        image = images[obj.current_frame % len(images)]
                        
                        # Affiche l'image du villageois (ou tout autre sprite lié)
                        #self.screen.blit(image, (screen_x, screen_y))

                        # Dessiner une flèche indiquant la direction
                        arrow_color = (255, 0, 0)  # Rouge pour la flèche
                        arrow_size = 2  # Taille de la flèche
                        dx, dy = 0, 0

                        # Détermine les décalages pour chaque direction
                        if direction == "north":
                            dx, dy = 0, -arrow_size
                        elif direction == "south":
                            dx, dy = 0, arrow_size
                        elif direction == "east":
                            dx, dy = arrow_size, 0
                        elif direction == "west":
                            dx, dy = -arrow_size, 0
                        elif direction == "northeast":
                            dx, dy = arrow_size, -arrow_size
                        elif direction == "northwest":
                            dx, dy = -arrow_size, -arrow_size
                        elif direction == "southeast":
                            dx, dy = arrow_size, arrow_size
                        elif direction == "southwest":
                            dx, dy = -arrow_size, arrow_size

                        # Définir les points du triangle pour la flèche
                        arrow_tip = (screen_x + dx, screen_y + dy)
                        arrow_left = (screen_x - dy // 2, screen_y + dx // 2)
                        arrow_right = (screen_x + dy // 2, screen_y - dx // 2)

                        # Dessiner le triangle représentant la flèche
                        pygame.draw.polygon(self.screen, arrow_color, [arrow_tip, arrow_left, arrow_right])

                elif unit_type == "swordman":
                    if state in self.swordman_images and direction in self.swordman_images[state]:
                        images = self.swordman_images[state][direction]
                        image = images[obj.current_frame % len(images)]
                        
                        # Affiche l'image du villageois (ou tout autre sprite lié)
                        #self.screen.blit(image, (screen_x, screen_y))

                        # Dessiner une flèche indiquant la direction
                        arrow_color = (255, 0, 0)  # Rouge pour la flèche
                        arrow_size = 2  # Taille de la flèche
                        dx, dy = 0, 0

                        # Détermine les décalages pour chaque direction
                        if direction == "north":
                            dx, dy = 0, -arrow_size
                        elif direction == "south":
                            dx, dy = 0, arrow_size
                        elif direction == "east":
                            dx, dy = arrow_size, 0
                        elif direction == "west":
                            dx, dy = -arrow_size, 0
                        elif direction == "northeast":
                            dx, dy = arrow_size, -arrow_size
                        elif direction == "northwest":
                            dx, dy = -arrow_size, -arrow_size
                        elif direction == "southeast":
                            dx, dy = arrow_size, arrow_size
                        elif direction == "southwest":
                            dx, dy = -arrow_size, arrow_size

                        # Définir les points du triangle pour la flèche
                        arrow_tip = (screen_x + dx, screen_y + dy)
                        arrow_left = (screen_x - dy // 2, screen_y + dx // 2)
                        arrow_right = (screen_x + dy // 2, screen_y - dx // 2)

                        # Dessiner le triangle représentant la flèche
                        pygame.draw.polygon(self.screen, arrow_color, [arrow_tip, arrow_left, arrow_right])

                elif unit_type == "Archer":
                    if state in self.archer_images and direction in self.archer_images[state]:
                        images = self.archer_images[state][direction]
                        image = images[obj.current_frame % len(images)]
                        
                        # Affiche l'image du villageois (ou tout autre sprite lié)
                        #self.screen.blit(image, (screen_x, screen_y))

                        # Dessiner une flèche indiquant la direction
                        arrow_color = (255, 0, 0)  # Rouge pour la flèche
                        arrow_size = 2  # Taille de la flèche
                        dx, dy = 0, 0

                        # Détermine les décalages pour chaque direction
                        if direction == "north":
                            dx, dy = 0, -arrow_size
                        elif direction == "south":
                            dx, dy = 0, arrow_size
                        elif direction == "east":
                            dx, dy = arrow_size, 0
                        elif direction == "west":
                            dx, dy = -arrow_size, 0
                        elif direction == "northeast":
                            dx, dy = arrow_size, -arrow_size
                        elif direction == "northwest":
                            dx, dy = -arrow_size, -arrow_size
                        elif direction == "southeast":
                            dx, dy = arrow_size, arrow_size
                        elif direction == "southwest":
                            dx, dy = -arrow_size, arrow_size

                        # Définir les points du triangle pour la flèche
                        arrow_tip = (screen_x + dx, screen_y + dy)
                        arrow_left = (screen_x - dy // 2, screen_y + dx // 2)
                        arrow_right = (screen_x + dy // 2, screen_y - dx // 2)

                        # Dessiner le triangle représentant la flèche
                        pygame.draw.polygon(self.screen, arrow_color, [arrow_tip, arrow_left, arrow_right])

                # Affichage du sprite sur l'écran
                if image:
                    self.screen.blit(image, (screen_x - 10, screen_y - 15))
          
            elif entity_type == "building":
                # Adjust sprite rendering based on building size
                building_type = obj.name.replace(" ", "")
                if building_type in self.building_images:
                    image = self.building_images[building_type]

                    # Adjust position for the sprite size
                    adjusted_y = screen_y - image.get_height()
                    adjusted_x = screen_x + self.TILE_WIDTH * (2 - obj.size) // 2

                    if obj.size == 3:
                        adjusted_y += (self.TILE_HEIGHT // 2)
                        adjusted_x -= (self.TILE_WIDTH // 2)

                    if obj.size == 2:
                        adjusted_y += (self.TILE_HEIGHT // 2)

                    self.screen.blit(image, (adjusted_x, adjusted_y))
                else:
                    pygame.draw.rect(
                        self.screen,
                        (150, 150, 150),
                        pygame.Rect(screen_x, screen_y, self.TILE_WIDTH, self.TILE_HEIGHT)
                    )

    def initialize_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.setup_paths()
        self.load_resources()
        self.tile_polygon = [
            (0, self.TILE_HEIGHT // 2),
            (self.TILE_WIDTH // 2, 0),
            (0, -self.TILE_HEIGHT // 2),
            (-self.TILE_WIDTH // 2, 0)
        ]

    def update_display(self):
        if not self.game_data:
            return

        self.screen.fill((0, 0, 0))
        self.render_isometric_map()
        self.update_and_draw_mini_map()
            # Draw resources if enabled
        if self.show_resources:
            self.display_player_resources()

        self.display_fps()
        pygame.display.flip()

    def run(self):
        try:
            self.initialize_pygame()
            self.running = True

            while self.running:
                try:
                    new_data = self.data_queue.get_nowait()
                    if new_data is not None:
                        self.game_data = new_data
                except Queue.Empty:
                    pass

                self.handle_events()
                self.handle_keyboard_input()
                self.update_display()
                self.clock.tick(1000)

        except Exception as e:
            print(f"Error in GUI thread: {e}")
            error_message = f"An error occurred in thread: {e}"
            detailed_traceback = traceback.format_exc()
            print(error_message)
            print(detailed_traceback)
        finally:
            self.cleanup()

    def cleanup(self):
        if pygame.get_init():
            pygame.quit()

    def stop(self):
        self.running = False
        self.join()



    def update_and_draw_mini_map(self):
        """
        Updates and draws the isometric mini-map. Resource rendering happens every 50 seconds,
        while other components are drawn every frame.
        """
        mini_map_width = 200
        mini_map_height = 150
        mini_map_x = self.WINDOW_WIDTH - mini_map_width - 10
        mini_map_y = self.WINDOW_HEIGHT - mini_map_height - 10
        tile_offset_x = mini_map_width // 2  # Centering adjustment for isometric projection

        # Check if it's time to update resource rendering
        current_time = time.time()
        if not self.mini_map_surface or current_time - self.last_mini_map_update >= self.mini_map_update_interval:
            self.update_mini_map_resources(mini_map_width, mini_map_height, tile_offset_x)
            self.last_mini_map_update = current_time

        # Calculate the source rect to only blit the visible portion of the mini-map
        source_rect = pygame.Rect(tile_offset_x, 0, mini_map_width, mini_map_height)
        
        # Draw the pre-rendered mini-map surface
        self.screen.blit(self.mini_map_surface, (mini_map_x, mini_map_y), source_rect)

        # Draw players, units, and buildings dynamically
        for player in self.game_data.players:
            player_color = self.PLAYER_COLORS.get(player.id, (255, 255, 255))

            # Draw player units
            for unit in player.units:
                iso_x, iso_y = self.cart_to_iso(unit.position[0], unit.position[1])
                tile_x = iso_x + (self.game_data.map.width * self.TILE_WIDTH // 2)
                tile_y = iso_y
                mini_map_iso_x = mini_map_x + (tile_x * (mini_map_width / (self.game_data.map.width * self.TILE_WIDTH)))
                mini_map_iso_y = mini_map_y + (tile_y * (mini_map_height / (self.game_data.map.height * self.TILE_HEIGHT)))
                pygame.draw.circle(self.screen, player_color, (int(mini_map_iso_x), int(mini_map_iso_y)), 2)

            # Draw player buildings
            for building in player.buildings:
                iso_x, iso_y = self.cart_to_iso(building.position[0], building.position[1])
                tile_x = iso_x + (self.game_data.map.width * self.TILE_WIDTH // 2)
                tile_y = iso_y
                mini_map_iso_x = mini_map_x + (tile_x * (mini_map_width / (self.game_data.map.width * self.TILE_WIDTH)))
                mini_map_iso_y = mini_map_y + (tile_y * (mini_map_height / (self.game_data.map.height * self.TILE_HEIGHT)))
                pygame.draw.rect(self.screen, player_color, (mini_map_iso_x - 1, mini_map_iso_y - 1, 3, 3))

        # Draw the viewing rectangle
        view_rect_width = (self.WINDOW_WIDTH / (self.game_data.map.width * self.TILE_WIDTH)) * mini_map_width
        view_rect_height = (self.WINDOW_HEIGHT / (self.game_data.map.height * self.TILE_HEIGHT)) * mini_map_height
        view_rect_x = mini_map_x + ((self.camera.offset_x / (self.game_data.map.width * self.TILE_WIDTH)) * mini_map_width)
        view_rect_y = mini_map_y + ((self.camera.offset_y / (self.game_data.map.height * self.TILE_HEIGHT)) * mini_map_height)
        pygame.draw.rect(self.screen, (255, 0, 0), (view_rect_x, view_rect_y, view_rect_width, view_rect_height), 2)

    def update_mini_map_resources(self, mini_map_width, mini_map_height, tile_offset_x):
        """
        Updates the pre-rendered resource layer of the mini-map with properly centered background.
        """
        # Create a surface with extra width to accommodate isometric offset
        total_width = mini_map_width + tile_offset_x * 2
        self.mini_map_surface = pygame.Surface((total_width, mini_map_height), pygame.SRCALPHA)
        
        # Fill the entire background
        self.mini_map_surface.fill((50, 40, 50))  # Mini-map background color

        # Render resources on the mini-map
        for y in range(self.game_data.map.height):
            for x in range(self.game_data.map.width):
                tile = self.game_data.map.grid[y][x]
                resource_type = tile.resource.type if tile.resource else "Soil"
                color = self.COLORS[resource_type]

                iso_x, iso_y = self.cart_to_iso(x, y)
                tile_x = iso_x + (self.game_data.map.width * self.TILE_WIDTH // 2)
                tile_y = iso_y
                
                # Calculate position on mini-map, including the offset
                mini_map_iso_x = (tile_x * (mini_map_width / (self.game_data.map.width * self.TILE_WIDTH))) + tile_offset_x
                mini_map_iso_y = (tile_y * (mini_map_height / (self.game_data.map.height * self.TILE_HEIGHT)))
                
                # Draw the resource tile
                pygame.draw.rect(self.mini_map_surface, color, (mini_map_iso_x, mini_map_iso_y, 2, 2))

    def handle_mini_map_click(self, event):
        """
        Handles user clicks on the mini-map by updating the camera position to center the view
        relative to the red rectangle.
        """
        mini_map_width = 200
        mini_map_height = 150
        mini_map_x = self.WINDOW_WIDTH - mini_map_width - 10
        mini_map_y = self.WINDOW_HEIGHT - mini_map_height - 10

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            # Check if click is within mini-map bounds
            if mini_map_x <= mouse_x <= mini_map_x + mini_map_width and \
            mini_map_y <= mouse_y <= mini_map_y + mini_map_height:
                
                # Calculate relative position within mini-map
                relative_x = (mouse_x - mini_map_x) / mini_map_width
                relative_y = (mouse_y - mini_map_y) / mini_map_height

                # Calculate the size of the red rectangle (view rectangle)
                view_rect_width = (self.WINDOW_WIDTH / (self.game_data.map.width * self.TILE_WIDTH)) * mini_map_width
                view_rect_height = (self.WINDOW_HEIGHT / (self.game_data.map.height * self.TILE_HEIGHT)) * mini_map_height

                # Adjust camera offsets to center the view on the click
                self.camera.offset_x = int(relative_x * self.game_data.map.width * self.TILE_WIDTH - (view_rect_width / 2) * (self.game_data.map.width * self.TILE_WIDTH) / mini_map_width)
                self.camera.offset_y = int(relative_y * self.game_data.map.height * self.TILE_HEIGHT - (view_rect_height / 2) * (self.game_data.map.height * self.TILE_HEIGHT) / mini_map_height)

    def display_player_resources(self):
        """
        Displays player resources in a compact HUD with icons for clarity and properly aligned text.
        """
        font = pygame.font.Font(None, 18)  # Smaller font for compact layout
        x_start = 10
        y_start = 10
        hud_width = 250
        hud_height = 90
        icon_size = 16
        padding = 8
        spacing = 5
        bar_height = 4
        text_color = (255, 255, 255)
        bar_colors = {
            "Wood": (34, 139, 34),   
            "Food": (255, 165, 0),   
            "Gold": (255, 215, 0),   
        }
        background_color = (30, 30, 30, 200)  

        resource_icons = {
            "Wood": pygame.transform.scale(self.iconwod, (icon_size, icon_size)),
            "Food": pygame.Surface((icon_size, icon_size)),  # Placeholder
            "Gold": pygame.transform.scale(self.icongold, (icon_size, icon_size)),
        }
        resource_icons["Food"].fill((255, 165, 0))  # Fill placeholder with orange

        for i, player in enumerate(self.game_data.players):
            y_position = y_start + i * (hud_height + spacing)
            box_surface = pygame.Surface((hud_width, hud_height), pygame.SRCALPHA)
            box_surface.fill(background_color)
            self.screen.blit(box_surface, (x_start, y_position))

            name_text = f"{player.name} (Player {player.id})"
            name_surface = font.render(name_text, True, text_color)
            self.screen.blit(name_surface, (x_start + padding, y_position + padding))

            resource_y = y_position + padding + font.get_height() + spacing
            for resource, value in player.owned_resources.items():
                icon_x = x_start + padding
                icon_y = resource_y
                if resource in resource_icons:
                    self.screen.blit(resource_icons[resource], (icon_x, icon_y))

                bar_x = icon_x + icon_size + spacing
                bar_width = hud_width - (icon_size + 3 * padding)
                bar_y = resource_y + (icon_size - bar_height) // 2
                pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height), border_radius=4)
                
                max_bar_width = min(bar_width, bar_width * (value / 100))
                pygame.draw.rect(self.screen, bar_colors.get(resource, text_color), (bar_x, bar_y, max_bar_width, bar_height), border_radius=4)

                resource_text = f"{value}"
                text_x = bar_x + max_bar_width + spacing
                resource_surface = font.render(resource_text, True, text_color)
                self.screen.blit(resource_surface, (text_x, bar_y))

                resource_y += icon_size + spacing

            buildings_text = f"Buildings: {len(player.buildings)}"
            buildings_surface = font.render(buildings_text, True, text_color)
            buildings_x = x_start + padding
            buildings_y = resource_y + spacing

            if buildings_y + font.get_height() + padding <= y_position + hud_height:
                self.screen.blit(buildings_surface, (buildings_x, buildings_y))


