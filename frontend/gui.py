import pygame
from pygame.locals import FULLSCREEN
from pygame.locals import HIDDEN
from backend.Building import Farm
import threading
import queue as Queue
from pathlib import Path
import time
import traceback
import random
from backend.Players import *

def get_unit_offsets(unit_type, state, direction):
    """
    Retourne les offsets pour une unité en fonction de son type, de son état et de sa direction.
    """
    # Offsets par défaut pour "villager"
    offsets_villager = {
        "idle": {
            "south": (-25, -37),
        },
        "walking": {
            "north": (-22, -43),
            "south": (-35, -52),
            "west": (-18, -38),
            "east": (-13, -41),
            "northwest": (-17, -41),
            "northeast": (-13, -38),
            "southwest": (-20, -38),
            "southeast": (-10, -40),
        },
        "attacking": {
            "north": (0, -20),
            "south": (0, 20),
            "west": (-20, 0),
            "east": (20, 0),
            "northwest": (-20, -20),
            "northeast": (20, -20),
            "southwest": (-20, 20),
            "southeast": (20, 20),
        },
        "gathering": {
            "north": (-63, -67),
            "south": (-62, -72),
            "west": (-61, -67),
            "east": (-22, -70),
            "northwest": (-59, -65),
            "northeast": (-26, -67),
            "southwest": (-62, -69),
            "southeast": (-19, -69),
        },
        "constructing": {
            "north": (-38, -28),
            "south": (-37, 37),
            "west": (-29, -40),
            "east": (-28, -40),
            "northwest": (-30, -33),
            "northeast": (-27, -34),
            "southwest": (-27, -40),
            "southeast": (-29, -43),
        },
        "dying": {
            "south": (0, 5),
        },
    }

    # Offsets spécifiques pour "swordman"
    offsets_swordman = {
        "idle": {
            "south": (-40, -56),
        },
        "walking": {
            "north": (-38, -54),
            "south": (-28, -40),
            "west": (-25, -42),
            "east": (-24, -40),
            "northwest": (-24, -42),
            "northeast": (-25, -42),
            "southwest": (-27, -40),
            "southeast": (-24, -43),
        },
        "attacking": {
            "north": (-22, -50),
            "south": (-21, -48), #1
            "west": (-22, -49),
            "east": (-27, -48),
            "northwest": (-21, -48),
            "northeast": (-29, -50),
            "southwest": (-23, -47), #fait
            "southeast": (-26, -47),
        },
        "dying": {
            "south": (0, 7),
        },
    }

    offsets_horsman = {
        "idle": {
            "south": (-40, -56),
        },
        "walking": {
            "north": (-41, -51),
            "south": (-35, -67),
            "west": (-40, -63),
            "east": (-41, -65),
            "northwest": (-42, -66),
            "northeast": (-45, -67),
            "southwest": (-44, -65),
            "southeast": (-43, -62),
        },
        "attacking": {
            "north": (-45, -65),
            "south": (-43, -75), #1
            "west": (-42, -71),
            "east": (-37, -70),
            "northwest": (-38, -70),
            "northeast": (-41, -67),
            "southwest": (-43, -70), #fait
            "southeast": (-38, -71),
        },
        "dying": {
            "south": (-36, -62),
        },
    }

    offsets_archer = {
        "idle": {
            "south": (-40, -56),
        },
        "walking": {
            "north": (-26, -44),
            "south": (-26, -45),
            "west": (-30, -41),
            "east": (-28, -39),
            "northwest": (-26, -38),
            "northeast": (-27, -42),
            "southwest": (-29, -40),
            "southeast": (-28, -43),
        },
        "attacking": {
            "north": (-33, -53),
            "south": (-29, -54), #1
            "west": (-34, -53),
            "east": (-26, -53),
            "northwest": (-34, -52),
            "northeast": (-23, -53),
            "southwest": (-34, -51), #fait
            "southeast": (-28, -51),
        },
        "dying": {
            "south": (-29, -53),
        },
    }


    # Associer les offsets en fonction du type d'unité
    offsets_by_unit_type = {
        "villager": offsets_villager,
        "swordman": offsets_swordman,
        "horseman" :offsets_horsman,
        "archer":offsets_archer,
    }

    # Récupérer les offsets pour le type d'unité donné
    offsets = offsets_by_unit_type.get(unit_type, offsets_villager)

    # Retourner l'offset pour l'état et la direction donnés
    return offsets.get(state, {}).get(direction, (0, 0))

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
        self.show_units = False

        self.mouse_held = None
           
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
            "Soil": (77, 164, 128)      # Green for soil
        }

        self.last_mini_map_update = time.time()
        self.mini_map_update_interval = 50
        self.mini_map_surface = None
        self.show_global_overlay = True

    def flip_image_horizontally(self, image):
        return pygame.transform.flip(image, True, False)

    def setup_paths(self):
        self.BASE_PATH = Path(__file__).resolve().parent.parent
        self.RESOURCES_PATH = self.BASE_PATH / "assets" / "resources"
        self.BUILDINGS_PATH = self.BASE_PATH / "assets" / "buildings" 
        self.IMG_PATH = self.BASE_PATH / "assets" / "img"
        self.IMG_HUD = self.BASE_PATH / "assets" / "HUD"

        assert self.RESOURCES_PATH.exists(), f"Resources directory {self.RESOURCES_PATH} does not exist."
        assert self.BUILDINGS_PATH.exists(), f"Buildings directory {self.BUILDINGS_PATH} does not exist."
        assert self.IMG_PATH.exists(), f"Buildings directory {self.IMG_PATH} does not exist."

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
            "Flower": self.load_image(self.RESOURCES_PATH / "Flower.png"),
            "Soil1": self.load_image(self.RESOURCES_PATH / "soil1.png"),
        }

        # Load and scale building images
        building_types = {
            "TownCenter": (256, 256),  # Taille : (256, 256)
            "Barracks": (self.TILE_WIDTH * 3, self.TILE_HEIGHT * 6 * 511 // 666),  # Taille : (666, 511)
            "House": (self.TILE_WIDTH * 2, self.TILE_HEIGHT * 4),  # Taille : (128, 128)
            "Rubble": (4*64, 4*32),  # Taille : (64, 64)
            "Stable": (self.TILE_WIDTH * 3, self.TILE_HEIGHT * 6 * 471 // 612),  # Taille : (612, 471)
            "ArcheryRange": (self.TILE_WIDTH * 3, self.TILE_HEIGHT * 6 * 595 // 648),  # Taille : (648, 595)
            "Camp": (self.TILE_WIDTH * 2, self.TILE_HEIGHT * 4),  # Taille : (128, 128)
            "Farm": (self.TILE_WIDTH * 2, self.TILE_HEIGHT * 2),  # Taille : (128, 64)
            "Keep": (64, 64*481//310),  # Taille : (64, 64)
            "Construct": (self.TILE_WIDTH * 2, self.TILE_HEIGHT * 2),  # Taille : (128, 64)
        }

        for building_type, size in building_types.items():
            image = self.load_image(self.BUILDINGS_PATH / f"{building_type.lower()}.png")
            self.building_images[building_type] = pygame.transform.scale(image, size)

        self.hud_image = self.load_image(self.IMG_HUD / "Hud.png")
        self.mini_map_back = self.load_image(self.IMG_HUD / "MiniMAP.png")
        self.back = self.load_image(self.IMG_HUD / "Hud2.png")
        self.background = self.load_image(self.IMG_HUD / "Overlay.png")
        self.victory_image = self.load_image(self.IMG_PATH / "victory.png")

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
            "constructing": {
                "north": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "FarmingVillager" / "Build & Repair" / "Act" / f"Villageract{i:03}.png")
                    for i in range(61, 75)
                ],
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "FarmingVillager" / "Build & Repair" / "Act" / f"Villageract{i:03}.png")
                    for i in range(1, 15)
                ],
                "west": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "FarmingVillager" / "Build & Repair" / "Act" / f"Villageract{i:03}.png")
                    for i in range(31, 45)
                ],
                "east": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "FarmingVillager" / "Build & Repair" / "Act" / f"Villageract{i:03}.png")
                    )
                    for i in range(31, 45)
                ],
                "northeast": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "FarmingVillager" / "Build & Repair" / "Act" / f"Villageract{i:03}.png")
                    )
                    for i in range(46, 60)
                ],
                "northwest": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "FarmingVillager" / "Build & Repair" / "Act" / f"Villageract{i:03}.png")
                    for i in range(46, 60)
                ],
                "southeast": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "FarmingVillager" / "Build & Repair" / "Act" / f"Villageract{i:03}.png")
                    )
                    for i in range(16, 30)
                ],
                "southwest": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "FarmingVillager" / "Build & Repair" / "Act" / f"Villageract{i:03}.png")
                    for i in range(16, 30) #fait
                ],
            },
            "idle": {
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Villager" / "Stand" /f"Villagerstand{i:03}.png") #nouveau
                    for i in range(17, 30)
                ],
            },
        }
                
        self.swordman_images = {
           "walking": {
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" / "walk" / f"Axethrowerwalk{i:03}.png")
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
                    for i in range(65, 80)
                ],
                "east": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Swordman" / "Attack" / f"Axethrowerattack{i:03}.png")
                    )
                    for i in range(33, 48)
                ],
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Swordman" / "Attack" / f"Axethrowerattack{i:03}.png")
                    for i in range(1, 16)
                ],
                "west": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Swordman" / "Attack" / f"Axethrowerattack{i:03}.png")
                    for i in range(33, 48)
                ],
                "northeast": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" / "Attack" / f"Axethrowerattack{i:03}.png")
                    )
                    for i in range(49, 64)
                ],
                "northwest": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" / "Attack" / f"Axethrowerattack{i:03}.png")
                    for i in range(49, 64) 
                ],
                "southwest": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" / "Attack" / f"Axethrowerattack{i:03}.png")
                    for i in range(17, 32) 
                ],
                "southeast": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" / "Attack" / f"Axethrowerattack{i:03}.png")
                    )
                    for i in range(17, 32)
                ],
            },
            "dying": {
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Swordman" / "Die" / f"Axethrowerdie{i:03}.png")
                    for i in range(1, 13)
                ],
            },
            "idle": {
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Swordman" / "Stand" / f"Axethrowerstand{i:03}.png")
                    for i in range(1, 10)  
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
                    for i in range(41, 50)
                ],
                "west": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Archer" / "Attack" / f"Archerattack{i:03}.png")
                    for i in range(21, 30)
                ],
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Archer" / "Attack" / f"Archerattack{i:03}.png")
                    for i in range(41, 40)
                ],
                "east": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Archer" / "Attack" / f"Archerattack{i:03}.png")
                    for i in range(21, 30)
                ],
                "northeast": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Archer" / "Attack" / f"Archerattack{i:03}.png")
                    )
                    for i in range(31, 40)
                ],
                "northwest": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Archer" / "Attack" / f"Archerattack{i:03}.png")
                    for i in range(31, 40)
                ],
                "southeast": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Archer" / "Attack" / f"Archerattack{i:03}.png")
                    )
                    for i in range(11, 20)
                ],
                "southwest": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Archer" / "Attack" / f"Archerattack{i:03}.png")
                    for i in range(11, 20)
                ],    
            },
            "dying": {
                
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Archer" / "Die" / f"Archerdie{i:03}.png")
                    for i in range(1, 13)
                ],
            },
            "idle": {
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Archer" / "Stand" / f"Archerstand{i:03}.png")
                    for i in range(11, 20)
                ],
            },
        }

        self.horseman_images = {
            "walking": {
                "north": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Walk" / f"Scoutwalk{i:03}.png")
                    for i in range(41, 50)
                ],
                "east": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Walk" / f"Scoutwalk{i:03}.png")
                    )
                    for i in range(21, 30)
                ],
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Walk" / f"Scoutwalk{i:03}.png")
                    for i in range(1, 10)
                ],
                "west": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Walk" / f"Scoutwalk{i:03}.png")
                    for i in range(21, 30)
                ],
                "northeast": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Walk" / f"Scoutwalk{i:03}.png")
                    )
                    for i in range(31, 40)
                ],
                "northwest": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Walk" / f"Scoutwalk{i:03}.png")
                    for i in range(31, 40)
                ],
                "southeast": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Walk" / f"Scoutwalk{i:03}.png")
                    )
                    for i in range(11, 20)
                ],
                "southwest": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Walk" / f"Scoutwalk{i:03}.png")
                    for i in range(11, 20)
                ],
            },
            "attacking": {
                "north": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Attack" / f"Scoutattack{i:03}.png")
                    for i in range(41, 50)
                ],
                "east": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Attack" / f"Scoutattack{i:03}.png")
                    )
                    for i in range(21, 30)
                ],
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Attack" / f"Scoutattack{i:03}.png")
                    for i in range(1, 10)
                ],
                "west": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Attack" / f"Scoutattack{i:03}.png")
                    for i in range(21, 30)
                ],
                "northeast": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Attack" / f"Scoutattack{i:03}.png")
                    )
                    for i in range(31, 40)
                ],
                "northwest": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Attack" / f"Scoutattack{i:03}.png")
                    for i in range(31, 40)
                ],
                "southeast": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Attack" / f"Scoutattack{i:03}.png")
                    )
                    for i in range(11, 20)
                ],
                "southwest": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Attack" / f"Scoutattack{i:03}.png")
                    for i in range(11, 20)
                ],
            },
            "dying": {
                "north": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Die" / f"Scoutdie{i:03}.png")
                    for i in range(41, 50)
                ],
                "east": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Die" / f"Scoutdie{i:03}.png")
                    )
                    for i in range(21, 30)
                ],
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Die" / f"Scoutdie{i:03}.png")
                    for i in range(1, 10)
                ],
                "west": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Die" / f"Scoutdie{i:03}.png")
                    for i in range(21, 30)
                ],
                "northeast": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Die" / f"Scoutdie{i:03}.png")
                    )
                    for i in range(31, 40)
                ],
                "northwest": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Die" / f"Scoutdie{i:03}.png")
                    for i in range(31, 40)
                ],
                "southeast": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Die" / f"Scoutdie{i:03}.png")
                    )
                    for i in range(11, 20)
                ],
                "southwest": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Die" / f"Scoutdie{i:03}.png")
                    for i in range(11, 20)
                ],
            },
            "idle": {
                "north": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Stand" / f"Scoutstand{i:03}.png")
                    for i in range(41, 50)
                ],
                "east": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Stand" / f"Scoutstand{i:03}.png")
                    )
                    for i in range(21, 30)
                ],
                "south": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Stand" / f"Scoutstand{i:03}.png")
                    for i in range(1, 10)
                ],
                "west": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Stand" / f"Scoutstand{i:03}.png")
                    for i in range(21, 30)
                ],
                "northeast": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Stand" / f"Scoutstand{i:03}.png")
                    )
                    for i in range(31, 40)
                ],
                "northwest": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Stand" / f"Scoutstand{i:03}.png")
                    for i in range(31, 40)
                ],
                "southeast": [
                    self.flip_image_horizontally(
                        self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Stand" / f"Scoutstand{i:03}.png")
                    )
                    for i in range(11, 20)
                ],
                "southwest": [
                    self.load_image(self.BASE_PATH / "assets" / "units" / "Horseman" / "Stand" / f"Scoutstand{i:03}.png")
                    for i in range(11, 20)
                ],
            },
        }

        self.iconwod = self.load_image(self.RESOURCES_PATH / "iconwood.png")
        self.icongold = self.load_image(self.RESOURCES_PATH / "icongold.png")

        self.IMAGES["Gold"] = pygame.transform.scale(self.IMAGES["Gold"], (self.TILE_WIDTH, self.TILE_HEIGHT))
        self.IMAGES["Wood"] = pygame.transform.scale(self.IMAGES["Wood"], (int(self.TILE_WIDTH * 2), int(self.TILE_HEIGHT * 2.5)))

    def calculate_damage_from_enemies(building, enemies):
        """Calcul des dégâts basés sur la distance des ennemis."""
        damage = 0
        for enemy in enemies:
            distance_x = abs(enemy.position[0] - building.position[0])
            distance_y = abs(enemy.position[1] - building.position[1])
            if distance_x < 100 and distance_y < 100:  # Supposons une portée de dégâts de 100 pixels
                damage += 10  # Chaque ennemi à portée ajoute 10 points de dégâts
        return damage

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
                if event.key == pygame.K_F9:
                    self.running = False
                elif event.key == pygame.K_F1:
                    self.show_resources = not self.show_resources
                elif event.key == pygame.K_F2:
                    self.show_units = not self.show_units

            # Gestion des événements de la souris
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Bouton gauche
                self.mouse_held = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Relâcher le clic gauche
                self.mouse_held = False

        # Appeler la fonction pour gérer le survol continu
        self.handle_mini_map_hover()

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

                # Dessiner les polygones pour observer les limites des tuiles
                transformed_polygon = [
                    (tile_x + point[0], tile_y + point[1]) for point in self.tile_polygon
                ]
                
                if "Soil" in self.IMAGES and "Soil1" in self.IMAGES:
                    # Alterner entre Soil et Soil1 en fonction de la parité de (x + y)
                    tile_type = "Soil1" if random.random() < 0.01 else "Soil"
                    tile_image = self.IMAGES[tile_type]
                    tile_rect = tile_image.get_rect(center=(tile_x, tile_y))
                    self.pre_rendered_map.blit(tile_image, tile_rect)

                pygame.draw.lines(self.pre_rendered_map, (200, 200, 200), True, transformed_polygon, 1)  # Bordures

                # Récupérer les informations de la tuile et placer les ressources
                tile = self.game_data.map.grid[y][x]

                if tile and random.random() < 0.01:
                        flower_image = self.IMAGES["Flower"]
                        self.pre_rendered_map.blit(flower_image, (
                            tile_x - (flower_image.get_width() // 2),
                            tile_y - flower_image.get_height() + (self.TILE_HEIGHT // 2)
                        ))

                if tile and tile.resource:
                    # Ajuster les coordonnées pour centrer la ressource
                    screen_x = tile_x
                    screen_y = tile_y - (self.TILE_HEIGHT // 2)

                    if tile.resource.type == "Wood":
                        image = self.IMAGES["Wood"]
                        self.pre_rendered_map.blit(image, (
                            tile_x - (image.get_width() // 2),
                            tile_y - image.get_height() + (self.TILE_HEIGHT // 2)
                        ))

                    elif tile.resource.type == "Gold":
                        image = self.IMAGES["Gold"]
                        self.pre_rendered_map.blit(image, (
                            tile_x - (image.get_width() // 2),
                            tile_y - image.get_height() + (self.TILE_HEIGHT // 2)
                        ))


    '''def render_dying_entities(self, game_data):
        """
        Render dying entities and remove them from the dictionary when animation completes.
        
        :param game_data: Game data containing pre_post_entities
        """
        # Define dying animation parameters
        dying_animation_frames = {
            'villager': 10,   # 10 frames for the villager's dying animation
            'swordsman': 12,
            'archer': 8,
            'horseman': 10
        }
        
        # Map entity types to their respective image dictionaries (dying animation by direction)
        entity_image_map = {
            'villager': self.villager_images.get("dying", []),  # Now directly a list
            'swordsman': self.swordman_images.get("dying", []),  # Now directly a list
            'archer': self.archer_images.get("dying", []),      # Now directly a list
            'horseman': self.horseman_images.get("dying", [])    # Now directly a list
        }        

        # Track entities to remove after animation completes
        entities_to_remove = []

        for entity_type, entities in game_data.map.pre_post_entities.items():
            if isinstance(entities, list):  # Ensure we have a list of entities
                for index, entity_data in enumerate(entities):
                    # If entity_data is just (x, y), initialize the dying_frame
                    if len(entity_data) == 2:  # Add frame counter if not present
                        entities[index] = (*entity_data, 0)  # Add dying_frame = 0

                    # Unpack position and current dying frame
                    x, y, current_frame = entities[index]
                    screen_x, screen_y = self.cart_to_iso(x, y)

                    # Get the correct images for the entity type
                    entity_images = entity_image_map.get(entity_type, [])
                    
                    # Ensure entity_images is a valid list
                    if isinstance(entity_images, list):
                        # Check if the current frame is within the valid range
                        if 0 <= current_frame < len(entity_images):
                            # Render the current frame of the animation
                            image = entity_images[current_frame]
                            self.screen.blit(image, (screen_x, screen_y))
                            
                            # Increment the animation frame only if it's not the last one
                            if current_frame < dying_animation_frames.get(entity_type, 10) - 1:
                                entities[index] = (x, y, current_frame + 1)
                            else:
                                # Stay at the last frame (don't increment anymore)
                                entities[index] = (x, y, current_frame)  
                    
                    # Check if the animation is complete (i.e., last frame)
                    if current_frame >= dying_animation_frames.get(entity_type, 10) - 1:
                        # Add to the removal list only after displaying the last frame
                        if current_frame == dying_animation_frames.get(entity_type, 10) - 1:
                            entities_to_remove.append((entity_type, index))

        # Remove completed dying entities after rendering
        for entity_type, entity_index in reversed(entities_to_remove):
            game_data.map.pre_post_entities[entity_type].pop(entity_index)
            print(f"Removing entity at index {entity_index} of type {entity_type}")'''

    def draw_health_bar(self, screen_x, screen_y, hp, max_hp, img_height, width=30, height=2):
        # Calcul du pourcentage de vie restant
        health_percentage = hp / max_hp
        health_width = int(width * health_percentage)
        # Couleur de la barre de vie
        color = (0, 255, 0) if health_percentage > 0.5 else (255, 165, 0) if health_percentage > 0.25 else (255, 0, 0)
        # Positionnement de la barre au-dessus de l'unité en tenant compte de la hauteur de l'image
        bar_x = screen_x - width // 2
        bar_y = screen_y - img_height   # 10 pixels au-dessus de l'unité
        # Dessiner le fond et la barre de vie
        pygame.draw.rect(self.screen, (255, 255, 255), [bar_x, bar_y, width, height])
        pygame.draw.rect(self.screen, color, [bar_x, bar_y, health_width, height])


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
                    entities.append((unit_x, unit_y, "unit", unit,unit.z))

            for building in player.buildings:
                bottom_right_x = building.position[0] + building.size - 2
                bottom_right_y = building.position[1] + building.size

                iso_x, iso_y = self.cart_to_iso(bottom_right_x, bottom_right_y)
                building_x = iso_x + (self.game_data.map.width * self.TILE_WIDTH // 2)
                building_y = iso_y

                if visible_rect.collidepoint(building_x, building_y):
                    entities.append((building_x, building_y, "building", building, building.z))

            for rubble in self.game_data.map.rubbles:
                iso_x, iso_y = self.cart_to_iso(rubble.position[0], rubble.position[1])
                rubble_x = iso_x + (self.game_data.map.width * self.TILE_WIDTH // 2)
                rubble_y = iso_y
                if visible_rect.collidepoint(rubble_x, rubble_y):
                    entities.append((rubble_x, rubble_y, "rubble", rubble, 0))


        entities.sort(key=lambda e: (
            0 if (e[2] == "building" and e[3].name == "Farm") or e[2] == "rubble" else 1,
            e[0] + e[1],  # Critère principal : somme des coordonnées pour l'ordre isométrique global
             -(e[1] - (e[4] if e[2] == 'building' else 0)),  # Critère secondaire : profondeur en tenant compte de la taille
            e[1],
            ))

    
        # Render all entities
        for x, y, entity_type, obj, z in entities:
            screen_x = x - self.camera.offset_x
            screen_y = y - self.camera.offset_y
            image = None
            #if entity_type in ["unit", "building"]:  # Supposons que `obj` a des attributs `hp` et `max_hp`
            #    self.draw_health_bar(screen_x, screen_y, obj.hp, obj.max_hp, image.get_height())

            if entity_type == "unit":
                unit_type = obj.sprite 
                state = obj.task
                direction = obj.direction

                # Déterminer l'état de l'unité
                if obj.is_moving == True:
                    state = "walking"  
                else :
                    if state is None:
                        obj.direction = "south"
                        state = "idle"
                    if state == "marching" or  state == "returning" or state == "going_to_battle" or  state == "going_to_construction_site" or obj.is_moving == True:
                        state = "walking"   
                    if state == "attacking" or state == "is_attacked":
                        state = "attacking"

                animation_speed = 40
                obj.frame_counter += 1
                if obj.frame_counter >= animation_speed:
                    if self.game_data.is_paused :
                        obj.current_frame = 0
                    else :
                        obj.current_frame += 1
                    obj.frame_counter = 0

                if unit_type == "villager":
                    if state in self.villager_images and direction in self.villager_images[state]:
                        images = self.villager_images[state][direction]
                        image = images[obj.current_frame % len(images)]

                elif unit_type == "swordman":
                   if state in self.swordman_images and direction in self.swordman_images[state]:
                    images = self.swordman_images[state][direction]
                    image = images[obj.current_frame % len(images)]

                elif unit_type == "archer":
                    if state in self.archer_images and direction in self.archer_images[state]:
                        images = self.archer_images[state][direction]
                        if images:
                            image = images[obj.current_frame % len(images)]

                elif unit_type == "horseman":
                    if state in self.horseman_images and direction in self.horseman_images[state]:
                        images = self.horseman_images[state][direction]
                        image = images[obj.current_frame % len(images)]
                        
                offset_x, offset_y = get_unit_offsets(unit_type,state, direction)
                screen_x = x - self.camera.offset_x + offset_x
                screen_y = y - self.camera.offset_y + offset_y
                if image:
                    self.screen.blit(image, (screen_x, screen_y))

                    if obj.is_attacked_by:
                        self.draw_health_bar(screen_x, screen_y, obj.hp, obj.max_hp, image.get_height())

          
            elif entity_type == "building":
                # Adjust sprite rendering based on building size
                building_type = obj.name.replace(" ", "")
                if building_type in self.building_images:
                    image = self.building_images[building_type]

                    # Adjust position for the sprite size
                    adjusted_y = screen_y - image.get_height() + (self.TILE_HEIGHT // 2)
                    adjusted_x = screen_x + self.TILE_WIDTH * (2 - obj.size) // 2

                    if obj.size == 4:
                        adjusted_x -= (self.TILE_WIDTH // 2)
                    if obj.size == 3 :
                        adjusted_y -= (self.TILE_HEIGHT // 6 ) 

                    self.screen.blit(image, (adjusted_x, adjusted_y))
                    if hasattr(obj, 'is_attacked_by') and obj.is_attacked_by:  # Afficher la barre de vie uniquement si l'unité est attaquée
                        self.draw_health_bar(screen_x, screen_y, obj.hp, obj.max_hp, image.get_height())
            
            elif entity_type == "rubble":
                image = self.building_images["Rubble"]
                new_size = (image.get_width() * obj.size // 4, image.get_height() * obj.size // 4)
                resized_image = pygame.transform.scale(image, new_size)
                adjusted_y = screen_y - resized_image.get_height() + (2*obj.size - 1) * self.TILE_HEIGHT // 2
                adjusted_x = screen_x - self.TILE_WIDTH * obj.size // 2 
                self.screen.blit(resized_image, (adjusted_x, adjusted_y))

        if self.show_global_overlay:
            overlay_surface = self.background
            self.screen.blit(overlay_surface, (0, 0))


    def initialize_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Age Of Empire")
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
        if self.show_units:
            self.display_player_units()

        if self.check_victory():
                return True
        
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
                
                if self.check_victory():
                    break
                
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
 
        mini_map_width = 200
        mini_map_height = 150
        mini_map_x = self.WINDOW_WIDTH - mini_map_width - 10
        mini_map_y = self.WINDOW_HEIGHT - mini_map_height - 10
        tile_offset_x = mini_map_width // 2  

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
        pygame.draw.rect(self.screen, (255, 255, 255), (view_rect_x, view_rect_y, view_rect_width, view_rect_height), 2)

    def update_mini_map_resources(self, mini_map_width, mini_map_height, tile_offset_x):
        """
        Updates the pre-rendered resource layer of the mini-map with properly centered background.
        """
        background_image = self.mini_map_back

        # Create a surface with extra width to accommodate isometric offset
        total_width = mini_map_width + tile_offset_x * 2
        self.mini_map_surface = pygame.Surface((total_width, mini_map_height), pygame.SRCALPHA)

        # Calculer les offsets pour centrer l'image sur la surface
        x_offset = (total_width - background_image.get_width()) // 2
        y_offset = (mini_map_height - background_image.get_height()) // 2

        # Dessiner l'image centrée sur la surface
        self.mini_map_surface.blit(background_image, (x_offset, y_offset))

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
    
    def handle_mini_map_hover(self):
        """
        Permet un survol continu de la mini-map tout en maintenant le clic gauche de la souris,
        en ajustant dynamiquement la position de la caméra.
        """
        mini_map_width = 200
        mini_map_height = 150
        mini_map_x = self.WINDOW_WIDTH - mini_map_width - 10
        mini_map_y = self.WINDOW_HEIGHT - mini_map_height - 10

        # Obtenir la position actuelle de la souris
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Vérifier si la souris est dans les limites de la mini-map
        if mini_map_x <= mouse_x <= mini_map_x + mini_map_width and \
        mini_map_y <= mouse_y <= mini_map_y + mini_map_height:
            
            # Si le bouton gauche est maintenu
            if self.mouse_held:
                # Calculer la position relative dans la mini-map
                relative_x = (mouse_x - mini_map_x) / mini_map_width
                relative_y = (mouse_y - mini_map_y) / mini_map_height

                # Calculer la taille du rectangle de vue (zone visible)
                view_rect_width = (self.WINDOW_WIDTH / (self.game_data.map.width * self.TILE_WIDTH)) * mini_map_width
                view_rect_height = (self.WINDOW_HEIGHT / (self.game_data.map.height * self.TILE_HEIGHT)) * mini_map_height

                # Ajuster dynamiquement les offsets de la caméra
                self.camera.offset_x = int(relative_x * self.game_data.map.width * self.TILE_WIDTH - (view_rect_width / 2) * (self.game_data.map.width * self.TILE_WIDTH) / mini_map_width)
                self.camera.offset_y = int(relative_y * self.game_data.map.height * self.TILE_HEIGHT - (view_rect_height / 2) * (self.game_data.map.height * self.TILE_HEIGHT) / mini_map_height)

    def display_player_resources(self):

        font = pygame.font.Font(None, 18)  # Police pour le texte
        x_start = 10  # Position horizontale de départ
        y_start = 10  # Position verticale de départ
        spacing = 10  # Espacement entre chaque joueur
        text_color = (255, 255, 255)  # Couleur du texte (blanc pour contraste)

        # Charger l'image HUD
        hud_image = self.hud_image
        hud_width, hud_height = hud_image.get_size()

        # Parcourir chaque joueur
        for i, player in enumerate(self.game_data.players[:len(self.game_data.players)]):
            y_position = y_start + i * (hud_height + spacing)  # Position verticale pour ce joueur
            x_position = x_start  # Position horizontale de départ pour ce joueur

            # Dessiner l'image HUD pour le joueur
            self.screen.blit(hud_image, (x_position, y_position))

            # Décalage initial pour commencer à écrire les données
            text_x = x_position + 50  # Début à l'intérieur de l'image
            text_y_centered = y_position + (hud_height // 2) - 5  # Centrer verticalement le texte

            # Afficher le nom du joueur (première ligne, centrée)
            name_text = f"{player.name}"
            name_surface = font.render(name_text, True, text_color)
            name_x = text_x - 40
            name_y = text_y_centered - 27
            self.screen.blit(name_surface, (name_x, name_y))

            # Afficher la ressource "Wood"
            wood_text = f"{player.owned_resources.get('Wood', 0)}"
            wood_surface = font.render(wood_text, True, text_color)
            self.screen.blit(wood_surface, (text_x, text_y_centered))
            text_x += 90  # Décaler pour afficher la ressource suivante

            # Afficher la ressource "Food"
            food_text = f"{player.owned_resources.get('Food', 0)}"
            food_surface = font.render(food_text, True, text_color)
            self.screen.blit(food_surface, (text_x, text_y_centered))
            text_x += 100  # Décaler pour afficher la ressource suivante

            # Afficher la ressource "Gold"
            gold_text = f"{player.owned_resources.get('Gold', 0)}"
            gold_surface = font.render(gold_text, True, text_color)
            self.screen.blit(gold_surface, (text_x, text_y_centered))
            text_x += 90  # Décaler pour afficher le nombre de bâtiments

            # Afficher le nombre de bâtiments
            buildings_text = f"{len(player.buildings)}"
            buildings_surface = font.render(buildings_text, True, text_color)
            self.screen.blit(buildings_surface, (text_x, text_y_centered))

    def display_player_units(self):
        font = pygame.font.Font(None, 18)  # Police pour le texte
        x_start = 40  # Position horizontale de départ
        y_start = 198 if self.show_resources else 18  # Ajuster la position verticale selon show_resources
        spacing = 5  # Espacement entre chaque joueur
        text_color = (255, 255, 255)  # Couleur du texte (blanc pour contraste)

        # Charger l'image de fond
        background_image = self.back

        # Dessiner l'image de fond
        if self.show_resources:
            self.screen.blit(background_image, (0, 175))
        else:
            self.screen.blit(background_image, (0, 0))

        # Parcourir chaque joueur
        for i, player in enumerate(self.game_data.players):
            y_position = y_start + i * (15 + spacing)
            x_position = x_start

            # Afficher le nom du joueur
            name_text = f"{player.name}"
            name_surface = font.render(name_text, True, text_color)
            self.screen.blit(name_surface, (x_position, y_position))

            # Décalage initial pour afficher les unités
            text_x = x_position + 80

            # Compter et afficher les unités par type
            unit_counts = {}
            for unit in player.units:
                # Vérifiez si `unit.sprite` est correct, sinon utilisez un autre attribut
                unit_type = unit.sprite  # Utilise 'sprite' ou un fallback "Unknown"
                if unit_type not in unit_counts:
                    unit_counts[unit_type] = 0
                unit_counts[unit_type] += 1

            # Afficher le type d'unité et leur nombre
            for unit_type, count in unit_counts.items():
                unit_text = f"{unit_type}: {count}"
                unit_surface = font.render(unit_text, True, text_color)
                self.screen.blit(unit_surface, (text_x, y_position))
                text_x += 100 

    def check_victory(self):
        active_players = [p for p in self.game_data.players if p.units or p.buildings]
        if len(active_players) == 1:
            self.display_victory_screen(active_players[0].name)
            return True
        return False
    
    def display_victory_screen(self, winner_name):
        victory_image = self.load_image(self.IMG_PATH / "victory.png")
        self.screen.blit(victory_image, (0, 0))
        font = pygame.font.Font(None, 72)
        text_surface = font.render(f"{winner_name} wins!", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2))
        self.screen.blit(text_surface, text_rect)
        pygame.display.flip()
        time.sleep(5)  # Wait for 5 seconds before closing
        self.running = False