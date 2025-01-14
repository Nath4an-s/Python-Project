import pygame
from pygame.locals import HIDDEN, FULLSCREEN, RESIZABLE, VIDEORESIZE
from backend.Starter_File import GUI_size
from backend.Building import TownCenter
from frontend.Terrain import Map
from backend.Units import Villager, Horseman, Archer, Swordsman
from pathlib import Path
import os
import random
import threading
from queue import Queue
import time
import queue
from PIL import Image

class GUI(threading.Thread):
    def __init__(self, data_queue):
        super().__init__()
        self.clock = pygame.time.Clock()
        self.fps = 60  # Set the desired frame rate
        self.data_queue = data_queue
        self.running = False
        self.game_data = None
        
        # Constants
        self.TILE_WIDTH = 64
        self.TILE_HEIGHT = 32
        self.WINDOW_WIDTH = 800
        self.WINDOW_HEIGHT = 600
        
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
        
        # Initialize view parameters
        self.offset_x = 0
        self.offset_y = 0
        self.show_resources = False
        self.trees_drawn = {}
        
        # Initialize pygame components to None (will be set up in run)
        self.screen = None
        self.clock = None
        self.IMAGES = {}
        self.building_images = {}
        self.background_texture = None
        self.villager_image_1 = None
        self.swordman_image = None
        self.font = None  # Ajout de l'attribut font
        
        # Setup paths
        self.setup_paths()
        
    def setup_paths(self):
        self.BASE_PATH = Path(__file__).resolve().parent.parent
        self.RESOURCES_PATH = self.BASE_PATH / "assets" / "resources"
        self.BUILDINGS_PATH = self.BASE_PATH / "assets" / "buildings"
        self.BACKGROUND_PATH = self.BASE_PATH / "assets" / "background"
        
        assert self.RESOURCES_PATH.exists(), f"Resources directory {self.RESOURCES_PATH} does not exist."
        assert self.BUILDINGS_PATH.exists(), f"Buildings directory {self.BUILDINGS_PATH} does not exist."
        assert self.BACKGROUND_PATH.exists(), f"Background directory {self.BACKGROUND_PATH} does not exist."

    def load_image(self, file_path):
        assert os.path.exists(file_path), f"File {file_path} does not exist."
        try:
            return pygame.image.load(file_path).convert_alpha()
        except pygame.error as e:
            print(f"Error loading image {file_path}: {e}")
            return pygame.Surface((self.TILE_WIDTH, self.TILE_HEIGHT))

    def load_resources(self):
        # Load basic images
        self.IMAGES = {
            "Wood": [self.load_image(self.RESOURCES_PATH / f"tree_{i}.png") for i in range(6)],
            "Gold": self.load_image(self.RESOURCES_PATH / "gold.png"),
            "Soil": self.load_image(self.RESOURCES_PATH / "soil.png"),
        }

        # Load and scale building images
        building_types = {
            "TownCenter": (256, 256),
            "Barracks": (self.TILE_WIDTH * 3, self.TILE_HEIGHT * 6),
            "House": (self.TILE_WIDTH * 2, self.TILE_HEIGHT * 4),
            "Rubble": (64, 64),
            "Stable": (self.TILE_WIDTH * 3, self.TILE_HEIGHT * 6),
            "ArcheryRange": (self.TILE_WIDTH * 2, self.TILE_HEIGHT * 4),
            "Camp": (self.TILE_WIDTH * 2, self.TILE_HEIGHT * 4),
            "Farm": (self.TILE_WIDTH * 2, self.TILE_HEIGHT * 2),
            "Keep": (64,64)
        }

        self.building_images = {}
        for building_type, size in building_types.items():
            image = self.load_image(self.BUILDINGS_PATH / f"{building_type.lower()}.png")
            self.building_images[building_type] = pygame.transform.scale(image, size)
            

        # Load background
        self.background_texture = self.load_image(self.BACKGROUND_PATH / "background.png")
        self.load_resources()
        self.load_villager_animations()
        # Load unit images

#############################################################################################################################
        self.villager_image_immobile = self.load_image(self.BASE_PATH / "assets" / "units" / "villager" / "Villager.png")
        self.liste_villager_immobile_animation = [self.villager_image_immobile]

########################################################################################################################
        #Bouger en haut 
      
    

    def load_villager_animations(self):
            # Load walking animations


            self.liste_villager_walking_en_bas_animation = [
               self.load_image(f"C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_bas/walking_en_bas/Villagerwalk0{i:02d}.png")
                 for i in range(1, 16)
            ]



            self.liste_villager_walking_en_bas_a_gauche_animation = [
                self.load_image(f"C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_bas/walking_en_bas_à_gauche/Villagerwalk0{i:02d}.png")
                for i in range(16, 31)]
            # Invert images for walking right

            self.liste_villager_walking_en_bas_a_droite_animation = [
                pygame.image.fromstring(
                    Image.open(f"C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_bas/walking_en_bas_à_gauche/Villagerwalk0{i:02d}.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                )
                for i in range(16, 31)
            ]



            self.liste_villager_walking_en_haut_animation = [
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut/Villagerwalk061.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut/Villagerwalk062.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut/Villagerwalk063.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut/Villagerwalk064.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut/Villagerwalk065.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut/Villagerwalk066.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut/Villagerwalk067.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut/Villagerwalk068.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut/Villagerwalk069.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut/Villagerwalk070.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut/Villagerwalk071.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut/Villagerwalk072.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut/Villagerwalk073.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut/Villagerwalk074.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut/Villagerwalk075.png"),
            ]
            self.liste_villager_walking_en_haut_a_gauche_animation = [
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk046.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk047.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk048.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk049.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk050.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk051.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk052.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk053.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk054.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk055.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk056.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk057.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk058.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk059.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk060.png"),
            ]
            # Invert images for walking right
            self.liste_villager_walking_en_haut_a_droite_animation = [
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk046.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk047.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk048.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk049.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk050.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk051.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk052.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk053.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk054.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk055.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk056.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk057.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk058.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk059.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_haut/walking_en_haut_à_gauche/Villagerwalk060.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                )
            ]
            self.liste_villager_walking_a_gauche_animation = [
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk031.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk032.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk033.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk034.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk035.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk036.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk037.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk038.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk039.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk040.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk041.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk042.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk043.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk044.png"),
                self.load_image("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk045.png"),
            ]
            self.liste_villager_walking_a_droite_animation = [
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk031.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk032.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk033.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk034.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk035.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk036.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk037.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk038.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk039.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk040.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk041.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk042.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk043.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk044.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                ),
                pygame.image.fromstring(
                    Image.open("C:/Users/Asus/Desktop/Python-Project/assets/units/villager/walk/walk_gauche/walking_a_gauche/Villagerwalk045.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                    (self.TILE_WIDTH, self.TILE_HEIGHT),
                    'RGBA'
                )
            ]
            self.liste_villager_dying_animation = [
                self.load_image(f"C:/Users/Asus/Desktop/Python-Project/assets/units/villager/die/Villagerdie0{i:02d}.png")
                for i in range(1, 75)
            ] 
            self.liste_villager_miner_animation = [
                self.load_image(f"C:/Users/Asus/Desktop/Python-Project/assets/units/villager/mine/Villagermine0{i:02d}.png")
                for i in range(1, 15)
            ]
            self.liste_villager_attack_en_bas_animation = [
                self.load_image(f"C:/Users/Asus/Desktop/Python-Project/assets/units/villager/attack/attack_bas/attacking_en_bas/Villagerattack0{i:02d}.png")
                for i in range(1, 15)               
            ]

            self.liste_villager_attack_en_bas_a_gauche_animation = [
                self.load_image(f"C:/Users/Asus/Desktop/Python-Project/assets/units/villager/attack/attack_bas/attacking_en_bas_à_gauche/Villagerattack0{i:02d}.png")
                for i in range(16, 32) 
            ]
            self.liste_villager_attack_en_bas_a_droite_animation = [
              pygame.image.fromstring(Image.open(f"C:/Users/Asus/Desktop/Python-Project/assets/units/villager/attack/attack_bas/attacking_en_bas_à_gauche/Villagerattack0{i:02d}.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                (self.TILE_WIDTH, self.TILE_HEIGHT),
                'RGBA'
            )
            for i in range(16, 32)
            ]
            self.liste_villager_attack_en_haut_animation = [
                self.load_image(f"C:/Users/Asus/Desktop/Python-Project/assets/units/villager/attack/attack_haut/attacking_en_haut/Villagerattack0{i:02d}.png")
                for i in range(61, 75)
            ]
            self.liste_villager_attack_en_haut_a_gauche_animation = [
                self.load_image(f"C:/Users/Asus/Desktop/Python-Project/assets/units/villager/attack/attack_haut/attacking_en_haut_à_gauche/Villagerattack0{i:02d}.png")
                for i in range(47, 60) 
            ] 
            self.liste_villager_attack_en_haut_a_droite_animation = [
                pygame.image.fromstring(Image.open(f"C:/Users/Asus/Desktop/Python-Project/assets/units/villager/attack/attack_haut/attacking_en_haut_à_gauche/Villagerattack0{i:02d}.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                (self.TILE_WIDTH, self.TILE_HEIGHT),
                'RGBA'
                )
                for i in range(47, 60)
            ]   
            self.liste_villager_attack_a_gauche_animation = [
                self.load_image(f"C:/Users/Asus/Desktop/Python-Project/assets/units/villager/attack/attack_gauche/attacking_a_gauche/Villagerattack0{i:02d}.png")
                for i in range(32, 46)
            ]
            self.liste_villager_attack_a_droite_animation = [
                pygame.image.fromstring(
                Image.open(f"C:/Users/Asus/Desktop/Python-Project/assets/units/villager/attack/attack_gauche/attacking_a_gauche/Villagerattack0{i:02d}.png").transpose(Image.FLIP_LEFT_RIGHT).tobytes(),
                (self.TILE_WIDTH, self.TILE_HEIGHT),
                'RGBA'
                )
                for i in range(32, 46)
            ]



            self.swordman_image_1 = self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" /"walkswordman" / "Halbadierwalk001.png")
            self.swordman_image_2 = self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" / "walkswordman" / "Halbadierwalk002.png")
            self.swordman_image_3 = self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" / "walkswordman" /  "Halbadierwalk003.png")
            self.swordman_image_4 = self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" /"walkswordman" /  "Halbadierwalk004.png")
            self.swordman_image_5 = self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" /"walkswordman" /  "Halbadierwalk005.png")
            self.swordman_image_6 = self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" / "walkswordman" / "Halbadierwalk006.png")
            self.swordman_image_7 = self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" / "walkswordman" / "Halbadierwalk007.png")
            self.swordman_image_8 = self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" /"walkswordman" /  "Halbadierwalk008.png")
            self.swordman_image_9 = self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" / "walkswordman" / "Halbadierwalk009.png")
            self.swordman_image_10 = self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" /"walkswordman" /  "Halbadierwalk010.png")
            self.swordman_image_11 = self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" / "walkswordman" / "Halbadierwalk011.png")
            self.swordman_image_12 = self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" / "walkswordman" / "Halbadierwalk012.png")
            self.swordman_image_13 = self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" / "walkswordman" /  "Halbadierwalk013.png")
            self.swordman_image_14 = self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" / "walkswordman" / "Halbadierwalk014.png")
            self.swordman_image_15 = self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" / "walkswordman" /  "Halbadierwalk015.png")

            self.liste_swordman_walking_animation = [self.swordman_image_1,self.swordman_image_2,self.swordman_image_3, self.swordman_image_4,self.swordman_image_5,
                                                    self.swordman_image_6,self.swordman_image_7,self.swordman_image_8,self.swordman_image_9,self.swordman_image_10,self.swordman_image_11,
                                                    self.swordman_image_12,self.swordman_image_13,self.swordman_image_14,self.swordman_image_15]
            
            self.swordman_image_act1 = self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" / "attack_bas" /"attacking_en_bas"/ "Halbadierattack001.png")
            self.swordman_image_act2 = self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" / "attack_bas" /"attacking_en_bas"/ "Halbadierattack002.png")
            self.liste_swordman_attacking_animation = [
                self.swordman_image_act1,self.swordman_image_act2
                ]



            self.archer_image = self.load_image(self.BASE_PATH / "assets" / "units" / "archer" /"walkarcher"/ "Archerwalk001.png")
                
            
            self.horseman_image_walk1 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "walkhorseman"/ "Cavalierwalk001.png")
            self.horseman_image_walk2 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "walkhorseman"/ "Cavalierwalk002.png")
            self.horseman_image_walk3 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "walkhorseman"/ "Cavalierwalk003.png")
            self.horseman_image_walk4 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "walkhorseman"/ "Cavalierwalk004.png")
            self.horseman_image_walk5 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "walkhorseman"/ "Cavalierwalk005.png")
            self.horseman_image_wakl6 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "walkhorseman"/ "Cavalierwalk006.png")
            self.horseman_image_walk7 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "walkhorseman"/ "Cavalierwalk007.png")
            self.horseman_image_walk8 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "walkhorseman"/ "Cavalierwalk008.png")
            self.horseman_image_walk9 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "walkhorseman"/ "Cavalierwalk009.png")
            self.horseman_image_wakk10 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "walkhorseman"/"Cavalierwalk010.png")

            

            self.liste_horseman_walking_animation = [
                self.horseman_image_walk1, self.horseman_image_walk2, self.horseman_image_walk3, self.horseman_image_walk4, self.horseman_image_walk5,
                self.horseman_image_wakl6, self.horseman_image_walk7, self.horseman_image_walk8, self.horseman_image_walk9, self.horseman_image_wakk10,
            ]

            self.horseman_image_die1 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "diehorseman"/ "Cavalierdie001.png")
            self.horseman_image_die2 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "diehorseman"/ "Cavalierdie002.png")
            self.horseman_image_die3 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "diehorseman"/ "Cavalierdie003.png")
            self.horseman_image_die4 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "diehorseman"/ "Cavalierdie004.png")
            self.horseman_image_die5 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "diehorseman"/ "Cavalierdie005.png")
            self.horseman_image_die6 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "diehorseman"/ "Cavalierdie006.png")
            self.horseman_image_die7 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "diehorseman"/ "Cavalierdie007.png")
            self.horseman_image_die8 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "diehorseman"/ "Cavalierdie008.png")
            self.horseman_image_die9 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "diehorseman"/ "Cavalierdie009.png")
            self.horseman_image_die10 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "diehorseman"/"Cavalierdie010.png")

            self.liste_horseman_dying_animation = [
                self.horseman_image_die1, self.horseman_image_die2, self.horseman_image_die3, self.horseman_image_die4, self.horseman_image_die5,
                self.horseman_image_die6, self.horseman_image_die7, self.horseman_image_die8, self.horseman_image_die9, self.horseman_image_die10,
            ]
            self.horseman_image_attacking_en_bas1 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas" / "Cavalierattack001.png")
            self.horseman_image_attacking_en_bas2 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas" / "Cavalierattack002.png")
            self.horseman_image_attacking_en_bas3 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas" / "Cavalierattack003.png")
            self.horseman_image_attacking_en_bas4 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas" / "Cavalierattack004.png")
            self.horseman_image_attacking_en_bas5 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas" / "Cavalierattack005.png")
            self.horseman_image_attacking_en_bas6 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas" / "Cavalierattack006.png")
            self.horseman_image_attacking_en_bas7 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas" / "Cavalierattack007.png")
            self.horseman_image_attacking_en_bas8 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas" / "Cavalierattack008.png")
            self.horseman_image_attacking_en_bas9 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas" / "Cavalierattack009.png")
            self.horseman_image_attacking_en_bas10 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas" / "Cavalierattack010.png")
        


            self.liste_horseman_attacking_en_bas_animation = [
                self.horseman_image_attacking_en_bas1, self.horseman_image_attacking_en_bas2, self.horseman_image_attacking_en_bas3, self.horseman_image_attacking_en_bas4, self.horseman_image_attacking_en_bas5,
                self.horseman_image_attacking_en_bas6, self.horseman_image_attacking_en_bas7, self.horseman_image_attacking_en_bas8, self.horseman_image_attacking_en_bas9, self.horseman_image_attacking_en_bas10,

            ]

            self.horseman_image_attacking_en_bas_droite_1 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas_à_droite"/ "Cavalierattack020r.png")
            self.horseman_image_attacking_en_bas_droite_2 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas_à_droite"/ "Cavalierattack020r (2).png")
            self.horseman_image_attacking_en_bas_droite_3 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas_à_droite"/ "Cavalierattack020r (3).png")
            self.horseman_image_attacking_en_bas_droite_4 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas_à_droite"/ "Cavalierattack020r (4).png")
            self.horseman_image_attacking_en_bas_droite_5 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas_à_droite"/ "Cavalierattack020r (5).png")
            self.horseman_image_attacking_en_bas_droite_6 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas_à_droite"/ "Cavalierattack020r (6).png")
            self.horseman_image_attacking_en_bas_droite_7 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas_à_droite"/ "Cavalierattack020r (7).png")
            self.horseman_image_attacking_en_bas_droite_8 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas_à_droite"/ "Cavalierattack020r (8).png")
            self.horseman_image_attacking_en_bas_droite_9 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas_à_droite"/ "Cavalierattack020r (9).png")
            self.horseman_image_attacking_en_bas_droite_10 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas_à_droite"/ "Cavalierattack020r (10).png")

            self.liste_horseman_attacking_en_bas_a_droite_animation = [
                self.horseman_image_attacking_en_bas_droite_1, self.horseman_image_attacking_en_bas_droite_2, self.horseman_image_attacking_en_bas_droite_3, self.horseman_image_attacking_en_bas_droite_4, self.horseman_image_attacking_en_bas_droite_5,
                self.horseman_image_attacking_en_bas_droite_6, self.horseman_image_attacking_en_bas_droite_7, self.horseman_image_attacking_en_bas_droite_8, self.horseman_image_attacking_en_bas_droite_9, self.horseman_image_attacking_en_bas_droite_10,
            ]
            
            self.horseman_image_attacking_en_bas_gauche_1 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas_à_gauche"/ "Cavalierattack011.png")
            self.horseman_image_attacking_en_bas_gauche_2 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" /"attack_bas"/ "attacking_en_bas_à_gauche"/ "Cavalierattack012.png")
            self.horseman_image_attacking_en_bas_gauche_3 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas_à_gauche"/ "Cavalierattack013.png")
            self.horseman_image_attacking_en_bas_gauche_4 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas_à_gauche"/ "Cavalierattack014.png")
            self.horseman_image_attacking_en_bas_gauche_5 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas_à_gauche"/ "Cavalierattack015.png")
            self.horseman_image_attacking_en_bas_gauche_6 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/  "attacking_en_bas_à_gauche"/ "Cavalierattack016.png")
            self.horseman_image_attacking_en_bas_gauche_7 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas_à_gauche"/ "Cavalierattack017.png")
            self.horseman_image_attacking_en_bas_gauche_8 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas_à_gauche"/ "Cavalierattack018.png")
            self.horseman_image_attacking_en_bas_gauche_9 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas_à_gauche"/ "Cavalierattack019.png")
            self.horseman_image_attacking_en_bas_gauche_10 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_bas"/ "attacking_en_bas_à_gauche"/ "Cavalierattack020.png")
        
            self.liste_horseman_attacking_en_bas_a_gauche_animation = [
                self.horseman_image_attacking_en_bas_gauche_1, self.horseman_image_attacking_en_bas_gauche_2, self.horseman_image_attacking_en_bas_gauche_3, self.horseman_image_attacking_en_bas_gauche_4, self.horseman_image_attacking_en_bas_gauche_5,
                self.horseman_image_attacking_en_bas_gauche_6, self.horseman_image_attacking_en_bas_gauche_7, self.horseman_image_attacking_en_bas_gauche_8, self.horseman_image_attacking_en_bas_gauche_9, self.horseman_image_attacking_en_bas_gauche_10,
            ]

        
            self.horseman_image_attacking_en_haut1 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut"/ "Cavalierattack041.png")
            self.horseman_image_attacking_en_haut2 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut"/ "Cavalierattack042.png")
            self.horseman_image_attacking_en_haut3 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut"/ "Cavalierattack043.png")
            self.horseman_image_attacking_en_haut4 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut"/ "Cavalierattack044.png")
            self.horseman_image_attacking_en_haut5 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut"/ "Cavalierattack045.png")
            self.horseman_image_attacking_en_haut6 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut"/ "Cavalierattack046.png")
            self.horseman_image_attacking_en_haut7 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut"/ "Cavalierattack047.png")
            self.horseman_image_attacking_en_haut8 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut"/ "Cavalierattack048.png")
            self.horseman_image_attacking_en_haut9 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut"/ "Cavalierattack049.png")
            self.horseman_image_attacking_en_haut10 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut"/"Cavalierattack050.png")

            self.liste_horseman_attacking_en_haut_animation = [
                self.horseman_image_attacking_en_haut1, self.horseman_image_attacking_en_haut2, self.horseman_image_attacking_en_haut3, self.horseman_image_attacking_en_haut4, self.horseman_image_attacking_en_haut5,
                self.horseman_image_attacking_en_haut6, self.horseman_image_attacking_en_haut7, self.horseman_image_attacking_en_haut8, self.horseman_image_attacking_en_haut9, self.horseman_image_attacking_en_haut10,
            ]

            self.horseman_image_attacking_en_haut_droite_1 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut_à_droite"/ "Cavalierattack031r (1).png")
            self.horseman_image_attacking_en_haut_droite_2 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut_à_droite"/ "Cavalierattack031r (2).png")
            self.horseman_image_attacking_en_haut_droite_3 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut_à_droite"/ "Cavalierattack031r (3).png")
            self.horseman_image_attacking_en_haut_droite_4 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut_à_droite"/ "Cavalierattack031r (4).png")
            self.horseman_image_attacking_en_haut_droite_5 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut_à_droite"/ "Cavalierattack031r (5).png")
            self.horseman_image_attacking_en_haut_droite_6 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut_à_droite"/ "Cavalierattack031r (6).png")
            self.horseman_image_attacking_en_haut_droite_7 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut_à_droite"/ "Cavalierattack031r (7).png")
            self.horseman_image_attacking_en_haut_droite_8 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut_à_droite"/ "Cavalierattack031r (8).png")
            self.horseman_image_attacking_en_haut_droite_9 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/  "attacking_en_haut_à_droite"/ "Cavalierattack031r (9).png")
            self.horseman_image_attacking_en_haut_droite_10 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut_à_droite"/ "Cavalierattack031r (10).png")

            self.liste_horseman_attacking_en_haut_a_droite_animation = [
                self.horseman_image_attacking_en_haut_droite_1, self.horseman_image_attacking_en_haut_droite_2, self.horseman_image_attacking_en_haut_droite_3, self.horseman_image_attacking_en_haut_droite_4, self.horseman_image_attacking_en_haut_droite_5,
                self.horseman_image_attacking_en_haut_droite_6, self.horseman_image_attacking_en_haut_droite_7, self.horseman_image_attacking_en_haut_droite_8, self.horseman_image_attacking_en_haut_droite_9, self.horseman_image_attacking_en_haut_droite_10,
            ]

            self.horseman_image_attacking_en_haut_gauche_1 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut_à_gauche"/ "Cavalierattack031.png")
            self.horseman_image_attacking_en_haut_gauche_2 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut_à_gauche"/ "Cavalierattack032.png")
            self.horseman_image_attacking_en_haut_gauche_3 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut_à_gauche"/ "Cavalierattack033.png")
            self.horseman_image_attacking_en_haut_gauche_4 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut_à_gauche"/ "Cavalierattack034.png")
            self.horseman_image_attacking_en_haut_gauche_5 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut_à_gauche"/ "Cavalierattack035.png")
            self.horseman_image_attacking_en_haut_gauche_6 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut_à_gauche"/ "Cavalierattack036.png")
            self.horseman_image_attacking_en_haut_gauche_7 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut_à_gauche"/ "Cavalierattack037.png")
            self.horseman_image_attacking_en_haut_gauche_8 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/  "attacking_en_haut_à_gauche"/ "Cavalierattack038.png")
            self.horseman_image_attacking_en_haut_gauche_9 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut_à_gauche"/ "Cavalierattack039.png")
            self.horseman_image_attacking_en_haut_gauche_10 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attack_haut"/ "attacking_en_haut_à_gauche"/ "Cavalierattack040.png")

            self.liste_horseman_attacking_en_haut_a_gauche_animation = [
                self.horseman_image_attacking_en_haut_gauche_1, self.horseman_image_attacking_en_haut_gauche_2, self.horseman_image_attacking_en_haut_gauche_3, self.horseman_image_attacking_en_haut_gauche_4, self.horseman_image_attacking_en_haut_gauche_5,
                self.horseman_image_attacking_en_haut_gauche_6, self.horseman_image_attacking_en_haut_gauche_7, self.horseman_image_attacking_en_haut_gauche_8, self.horseman_image_attacking_en_haut_gauche_9, self.horseman_image_attacking_en_haut_gauche_10,
            ]

            self.horseman_image_attacking_a_droit_1 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attacking_droit_gauche"/ "attacking_à_droit" / "Cavalierattack030r (1).png")
            self.horseman_image_attacking_a_droit_2 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attacking_droit_gauche"/ "attacking_à_droit" / "Cavalierattack030r (2).png")
            self.horseman_image_attacking_a_droit_3 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attacking_droit_gauche"/ "attacking_à_droit" / "Cavalierattack030r (3).png")
            self.horseman_image_attacking_a_droit_4 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attacking_droit_gauche"/ "attacking_à_droit" / "Cavalierattack030r (4).png")
            self.horseman_image_attacking_a_droit_5 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attacking_droit_gauche"/ "attacking_à_droit" / "Cavalierattack030r (5).png")
            self.horseman_image_attacking_a_droit_6 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attacking_droit_gauche"/ "attacking_à_droit" / "Cavalierattack030r (6).png")
            self.horseman_image_attacking_a_droit_7 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attacking_droit_gauche"/ "attacking_à_droit" / "Cavalierattack030r (7).png")
            self.horseman_image_attacking_a_droit_8 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attacking_droit_gauche"/ "attacking_à_droit" / "Cavalierattack030r (8).png")
            self.horseman_image_attacking_a_droit_9 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attacking_droit_gauche"/ "attacking_à_droit" / "Cavalierattack030r (9).png")
            self.horseman_image_attacking_a_droit_10 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attacking_droit_gauche"/ "attacking_à_droit" / "Cavalierattack030r (10).png")

            self.liste_horseman_attacking_a_droit_animation = [
                self.horseman_image_attacking_a_droit_1, self.horseman_image_attacking_a_droit_2, self.horseman_image_attacking_a_droit_3, self.horseman_image_attacking_a_droit_4, self.horseman_image_attacking_a_droit_5,
                self.horseman_image_attacking_a_droit_6, self.horseman_image_attacking_a_droit_7, self.horseman_image_attacking_a_droit_8, self.horseman_image_attacking_a_droit_9, self.horseman_image_attacking_a_droit_10,
            ]
            
            self.horseman_image_attacking_a_gauche_1 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attacking_droit_gauche"/ "attacking_à_gauche" / "Cavalierattack021.png")
            self.horseman_image_attacking_a_gauche_2 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attacking_droit_gauche"/ "attacking_à_gauche" / "Cavalierattack022.png")
            self.horseman_image_attacking_a_gauche_3 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attacking_droit_gauche"/ "attacking_à_gauche" / "Cavalierattack023.png")
            self.horseman_image_attacking_a_gauche_4 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attacking_droit_gauche"/ "attacking_à_gauche" / "Cavalierattack024.png")
            self.horseman_image_attacking_a_gauche_5 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attacking_droit_gauche"/ "attacking_à_gauche" / "Cavalierattack025.png")
            self.horseman_image_attacking_a_gauche_6 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attacking_droit_gauche"/ "attacking_à_gauche" / "Cavalierattack026.png")
            self.horseman_image_attacking_a_gauche_7 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attacking_droit_gauche"/ "attacking_à_gauche" / "Cavalierattack027.png")
            self.horseman_image_attacking_a_gauche_8 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attacking_droit_gauche"/ "attacking_à_gauche" / "Cavalierattack028.png")
            self.horseman_image_attacking_a_gauche_9 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attacking_droit_gauche"/ "attacking_à_gauche" / "Cavalierattack029.png")
            self.horseman_image_attacking_a_gauche_10 = self.load_image(self.BASE_PATH / "assets" / "units" / "horseman" / "attacking_droit_gauche"/ "attacking_à_gauche" / "Cavalierattack030.png")

            self.liste_horseman_attacking_a_gauche_animation = [
                self.horseman_image_attacking_a_gauche_1, self.horseman_image_attacking_a_gauche_2, self.horseman_image_attacking_a_gauche_3, self.horseman_image_attacking_a_gauche_4, self.horseman_image_attacking_a_gauche_5,
                self.horseman_image_attacking_a_gauche_6, self.horseman_image_attacking_a_gauche_7, self.horseman_image_attacking_a_gauche_8, self.horseman_image_attacking_a_gauche_9, self.horseman_image_attacking_a_gauche_10,
            ]

            # Scale gold and tree images
            self.IMAGES["Gold"] = pygame.transform.scale(self.IMAGES["Gold"], (self.TILE_WIDTH, self.TILE_HEIGHT))
            for i in range(len(self.IMAGES["Wood"])):
                scaled_width = int(self.TILE_WIDTH * 1.5)  # Augmenter la largeur de 50%
                scaled_height = int(self.TILE_HEIGHT * 1.5)  # Augmenter la hauteur de 50%
                self.IMAGES["Wood"][i] = pygame.transform.scale(self.IMAGES["Wood"][i], (scaled_width, scaled_height))

    def cart_to_iso(self, cart_x, cart_y):
        iso_x = (cart_x - cart_y) * (self.TILE_WIDTH // 2)
        iso_y = (cart_x + cart_y) * (self.TILE_HEIGHT // 2)
        return iso_x, iso_y

    def draw_isometric_map(self):
        if not self.game_data or not self.game_data.map:
            return

        #self.screen.blit(self.background_texture, (0, 0))
        
        for y in range(self.game_data.map.height):
            for x in range(self.game_data.map.width):
                
                soil_image = self.IMAGES['Soil']
                iso_x, iso_y = self.cart_to_iso(x, y)
                screen_x = (GUI_size.x // 2) + iso_x - self.offset_x
                screen_y = (GUI_size.y // 4) + iso_y - self.offset_y - (soil_image.get_height() - self.TILE_HEIGHT)
                
                if 0 <= screen_x < self.WINDOW_WIDTH and 0 <= screen_y < self.WINDOW_HEIGHT:
                    self.screen.blit(soil_image, (screen_x, screen_y))

    def draw_buildings(self, buildings):
        for building in sorted(buildings, key=lambda b: (b.position[1] + b.size - 1, b.position[0])):
            bottom_right_x = building.position[0] + building.size - 1
            bottom_right_y = building.position[1] + building.size - 1
            iso_x, iso_y = self.cart_to_iso(bottom_right_x, bottom_right_y)

            screen_x = (GUI_size.x // 2) + iso_x - self.offset_x
            screen_y = (GUI_size.y // 4) + iso_y - self.offset_y

            building_type = building.name.replace(" ", "")
            if building_type in self.building_images:
                building_image = self.building_images[building_type]
                building_adjusted_y = screen_y - building_image.get_height()
                screen_x += self.TILE_WIDTH * (2 - building.size) // 2
                if building.size == 3:
                    building_adjusted_y += (self.TILE_HEIGHT // 2)

                # Apply tint based on player color with transparency
                player_color = self.PLAYER_COLORS[building.player.id]
                tinted_image = self.tint_image(building_image, player_color, alpha=128)

                if 0 <= screen_x < self.WINDOW_WIDTH and 0 <= screen_y < self.WINDOW_HEIGHT:
                    self.screen.blit(tinted_image, (screen_x, building_adjusted_y))

    def draw_resources(self):
        for y in range(self.game_data.map.height):
            for x in range(self.game_data.map.width):
                tile = self.game_data.map.grid[y][x]
                soil_image = self.IMAGES['Soil']
                iso_x, iso_y = self.cart_to_iso(x, y)
                screen_x = (GUI_size.x // 2) + iso_x - self.offset_x
                screen_y = (GUI_size.y // 4) + iso_y - self.offset_y - (soil_image.get_height() - self.TILE_HEIGHT)
                    
                if tile.resource:
                    if tile.resource:
                        if tile.resource.type == "Wood":
                            pos = (x, y)
                            if pos not in self.trees_drawn:
                                self.trees_drawn[pos] = random.randint(0, 5)
                            image = self.IMAGES["Wood"][self.trees_drawn[pos]]
                            screen_y_adjusted = screen_y - (image.get_height() - self.TILE_HEIGHT)
                            if 0 <= screen_x < self.WINDOW_WIDTH and 0 <= screen_y < self.WINDOW_HEIGHT:
                                self.screen.blit(image, (screen_x + self.TILE_WIDTH//4, screen_y_adjusted))
                        else:
                            screen_y_adjusted = screen_y - (self.IMAGES["Gold"].get_height() - self.TILE_HEIGHT)
                            if 0 <= screen_x < self.WINDOW_WIDTH and 0 <= screen_y < self.WINDOW_HEIGHT:
                                self.screen.blit(self.IMAGES["Gold"], (screen_x + self.TILE_WIDTH//2, screen_y_adjusted))

    def draw_villagers(self, villagers, buildings):
        animation_speed = 5 
        position_count = {}
        for villager in villagers:
            pos = (villager.position[0], villager.position[1])
            if pos not in position_count:
                position_count[pos] = []
            position_count[pos].append(villager)

        for pos, villagers_at_pos in position_count.items():
            for index, villager in enumerate(villagers_at_pos):
                villager_x, villager_y = villager.position
                iso_villager_x, iso_villager_y = self.cart_to_iso(villager_x, villager_y)
                screen_x, screen_y = self.adjust_villager_position(
                    (GUI_size.x // 2) + iso_villager_x - self.offset_x + 3 * self.TILE_WIDTH // 4,
                    (GUI_size.y // 4) + iso_villager_y - self.offset_y - self.villager_image_1.get_height() if self.villager_image_1 else 0,
                    len(villagers_at_pos), index)

                current_time = pygame.time.get_ticks() // (1000 // animation_speed)
                if villager.task == "gathering":
                    animation_frames = self.liste_villager_miner_animation
                elif villager.task == "attacking":
                    if villager.direction == "en_bas":
                        animation_frames = self.liste_villager_attack_en_bas_animation
                    elif villager.direction == "en_bas_a_gauche":
                        animation_frames = self.liste_villager_attack_en_bas_a_gauche_animation
                    elif villager.direction == "en_bas_a_droite":
                        animation_frames = self.liste_villager_attack_en_bas_a_droite_animation
                    elif villager.direction == "en_haut":
                        animation_frames = self.liste_villager_attack_en_haut_animation
                    elif villager.direction == "en_haut_a_gauche":
                        animation_frames = self.liste_villager_attack_en_haut_a_gauche_animation
                    elif villager.direction == "en_haut_a_droite":
                        animation_frames = self.liste_villager_attack_en_haut_a_droite_animation
                elif villager.task == "dying":
                    animation_frames = self.liste_villager_dying_animation
                elif villager.task == "walking":
                    if villager.direction == "en_bas":
                        animation_frames = self.liste_villager_walking_en_bas_animation
                    elif villager.direction == "en_bas_a_gauche":
                        animation_frames = self.liste_villager_walking_en_bas_a_gauche_animation
                    elif villager.direction == "en_bas_a_droite":
                        animation_frames = self.liste_villager_walking_en_bas_a_droite_animation
                    elif villager.direction == "en_haut":
                        animation_frames = self.liste_villager_walking_en_haut_animation
                    elif villager.direction == "en_haut_a_gauche":
                        animation_frames = self.liste_villager_walking_en_haut_a_gauche_animation
                    elif villager.direction == "en_haut_a_droite":
                        animation_frames = self.liste_villager_walking_en_haut_a_droite_animation
                else:
                    animation_frames = self.liste_villager_immobile_animation

                current_frame = current_time % len(animation_frames)
                villager_image = animation_frames[current_frame]

                # Apply tint based on player color with transparency
                player_color = self.PLAYER_COLORS[villager.player.id]
                tinted_image = self.tint_image(villager_image, player_color, alpha=128)

                if 0 <= screen_x < self.WINDOW_WIDTH and 0 <= screen_y < self.WINDOW_HEIGHT:
                    self.screen.blit(tinted_image, (screen_x, screen_y))

    def adjust_villager_position(self, screen_x, screen_y, count, index):
        offset = 10  # Décalage en pixels entre chaque villageois
        # Calculer le décalage pour chaque villageois pour éviter la superposition
        offset_x = (index % 2) * offset - (offset * (count - 1) / 2)
        offset_y = (index // 2) * offset - (offset * (count - 1) / 2)
        return screen_x + offset_x, screen_y + offset_y


    def is_position_free(self, x, y, buildings):
        for building in buildings:
            building_x, building_y = building.position
            # Assumer que la taille du bâtiment s'étend de sa position initiale à sa taille en largeur et hauteur
            if building_x <= x < building_x + building.size and building_y <= y < building_y + building.size:
                return False
        return True

    def is_behind_building(self, object, building):
        object_x, object_y = object.position
        building_x, building_y = building.position
        building_end_x = building_x + building.width
        building_end_y = building_y + building.height

        # Assumer une simple vérification basée sur la coordonnée Y pour simplification
        return object_y > building_y and object_y < building_end_y

    def draw_swordman(self, swordmans):
        animation_speed = 10  # Vitesse de l'animation
        position_count = {}
        for swordman in swordmans:
            pos = (swordman.position[0], swordman.position[1])
            if pos not in position_count:
                position_count[pos] = []
                position_count[pos].append(swordman)

        for pos, swordmans_at_pos in position_count.items():
            for index, swordman in enumerate(swordmans_at_pos):
                swordman_x, swordman_y = swordman.position
                iso_swordman_x, iso_swordman_y = self.cart_to_iso(swordman_x, swordman_y)
                screen_x, screen_y = self.adjust_villager_position(
                (GUI_size.x // 2) + iso_swordman_x - self.offset_x + 3*self.TILE_WIDTH//4,
                (GUI_size.y // 4) + iso_swordman_y - self.offset_y - self.swordman_image_1.get_height(),
                len(swordmans_at_pos), index)

                current_time = pygame.time.get_ticks() // (1000 // animation_speed)
                if swordman.task == "attacking":
                    animation_frames = self.liste_swordman_attacking_animation
                else:
                    animation_frames = self.liste_swordman_walking_animation
                current_frame = current_time % len(animation_frames)
                swordman_image = animation_frames[current_frame]
                if 0 <= screen_x < self.WINDOW_WIDTH and 0 <= screen_y < self.WINDOW_HEIGHT:
                    self.screen.blit(swordman_image, (screen_x, screen_y))

    def draw_archer(self, archers):
        for archer in archers:
            iso_x, iso_y = self.cart_to_iso(archer.position[0], archer.position[1])
            screen_x = iso_x - self.offset_x
            screen_y = iso_y - self.offset_y - self.archer_image.get_height()
            if 0 <= screen_x < self.WINDOW_WIDTH and 0 <= screen_y < self.WINDOW_HEIGHT:
                self.screen.blit(self.archer_image, (screen_x, screen_y))



    def tint_image(self, image, color, alpha=128):
        """Apply a transparent tint to an image."""
        tinted_image = image.copy()
        tint = pygame.Surface(tinted_image.get_size(), pygame.SRCALPHA)
        tint.fill((*color, alpha))
        tinted_image.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return tinted_image
    

    def draw_horseman(self, horsemans):
        animation_speed = 2  # 2 frames per second (0.5 seconds per frame)
        for horseman in horsemans:
            iso_x, iso_y = self.cart_to_iso(horseman.position[0], horseman.position[1])
            screen_x = iso_x - self.offset_x
            screen_y = iso_y - self.offset_y - self.horseman_image_die1.get_height()

            current_time = pygame.time.get_ticks() // (1000 // animation_speed)
            if horseman.task == "dying":
                animation_frames = self.liste_horseman_dying_animation
            elif horseman.task == "attacking":
                if horseman.direction == "en_bas":
                    animation_frames = self.liste_horseman_attacking_en_bas_animation
                elif horseman.direction == "en_haut":
                    animation_frames = self.liste_horseman_attacking_en_haut_animation
                elif horseman.direction == "bas_droit":
                    animation_frames = self.liste_horseman_attacking_en_bas_a_droite_animation
                elif horseman.direction == "bas_gauche":
                    animation_frames = self.liste_horseman_attacking_en_bas_a_gauche_animation
                elif horseman.direction == "haut_gauche":
                    animation_frames = self.liste_horseman_attacking_en_haut_a_gauche_animation
                elif horseman.direction == "haut_droite":
                    animation_frames = self.liste_horseman_attacking_en_haut_a_droite_animation
                elif horseman.direction == "droit":
                    animation_frames = self.liste_horseman_attacking_a_droit_animation
                elif horseman.direction == "gauche":
                    animation_frames = self.liste_horseman_attacking_a_gauche_animation
            else:
                if horseman.direction == "en_bas" :
                    animation_frames = self.liste_horseman_walking_animation
                
                
                #elif horseman.direction == "en_haut":
                #    animation_frames = self.liste_horseman_walking_en_haut_animation
                #elif horseman.direction == "droit":
                #    animation_frames = self.liste_horseman_walking_droit_animation
                #elif horseman.direction == "gauche":
                #    animation_frames = self.liste_horseman_walking_gauche_animation

            current_frame = current_time % len(animation_frames)
            horseman_image = animation_frames[current_frame]

            # Apply tint based on player color with transparency
            player_color = self.PLAYER_COLORS[horseman.player.id]
            tinted_image = self.tint_image(horseman_image, player_color, alpha=128)

            if 0 <= screen_x < self.WINDOW_WIDTH and 0 <= screen_y < self.WINDOW_HEIGHT:
                self.screen.blit(tinted_image, (screen_x, screen_y))

    def draw_mini_map(self):
        mini_map_width = 200
        mini_map_height = 150
        mini_map_x = self.screen.get_width() - mini_map_width - 10
        mini_map_y = self.screen.get_height() - mini_map_height - 10

        pygame.draw.rect(self.screen, (50, 40, 50), (mini_map_x, mini_map_y, mini_map_width, mini_map_height))
        
        tile_offset_x = 100

        # Draw terrain and resources
        for y in range(self.game_data.map.height):
            for x in range(self.game_data.map.width):
                tile = self.game_data.map.grid[y][x]

                resource_type = tile.resource.type if tile.resource else "Soil"
                color = self.COLORS[resource_type]

                iso_x, iso_y = self.cart_to_iso(x, y)
                
                mini_map_iso_x = mini_map_x + (iso_x * (mini_map_width / (self.game_data.map.width * self.TILE_WIDTH))) + tile_offset_x
                mini_map_iso_y = mini_map_y + (iso_y * (mini_map_height / (self.game_data.map.height * self.TILE_HEIGHT)))
                
                pygame.draw.rect(self.screen, color, (mini_map_iso_x, mini_map_iso_y, 2, 2))

        # Draw players and their units
        for player in self.game_data.players:
            player_color = self.PLAYER_COLORS.get(player.id, (255, 255, 255))
            # Draw player units
            for unit in player.units:
                iso_x, iso_y = self.cart_to_iso(unit.position[0], unit.position[1])
                mini_map_iso_x = mini_map_x + (iso_x * (mini_map_width / (self.game_data.map.width * self.TILE_WIDTH))) + tile_offset_x
                mini_map_iso_y = mini_map_y + (iso_y * (mini_map_height / (self.game_data.map.height * self.TILE_HEIGHT)))
                pygame.draw.circle(self.screen, player_color, (int(mini_map_iso_x), int(mini_map_iso_y)), 2)

            # Draw player buildings
            for building in player.buildings:
                iso_x, iso_y = self.cart_to_iso(building.position[0], building.position[1])
                mini_map_iso_x = mini_map_x + (iso_x * (mini_map_width / (self.game_data.map.width * self.TILE_WIDTH))) + tile_offset_x
                mini_map_iso_y = mini_map_y + (iso_y * (mini_map_height / (self.game_data.map.height * self.TILE_HEIGHT)))
                pygame.draw.rect(self.screen, player_color, (mini_map_iso_x, mini_map_iso_y, 3, 3))

        # Calculate viewing rectangle dimensions
        view_rect_width = (GUI_size.x / (self.game_data.map.width * self.TILE_WIDTH)) * mini_map_width
        view_rect_height = (GUI_size.y / (self.game_data.map.height * self.TILE_HEIGHT)) * mini_map_height
        
        # Center the rect on the offset position
        view_rect_x = mini_map_x + ((self.offset_x / (self.game_data.map.width * self.TILE_WIDTH)) * mini_map_width) + (tile_offset_x - view_rect_width/2)
        view_rect_y = mini_map_y + ((self.offset_y / (self.game_data.map.height * self.TILE_HEIGHT)) * mini_map_height) - view_rect_height/2
        
        pygame.draw.rect(self.screen, (255, 0, 0), (view_rect_x, view_rect_y, view_rect_width, view_rect_height), 2)

    def handle_mini_map_click(self, event):
        mini_map_width = 200
        mini_map_height = 150
        mini_map_x = GUI_size.x - mini_map_width - 10
        mini_map_y = GUI_size.y - mini_map_height - 10
        tile_offset_x = 100

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if (mini_map_x <= mouse_x <= mini_map_x + mini_map_width and 
                mini_map_y <= mouse_y <= mini_map_y + mini_map_height):
                
                # Calculate relative position within mini-map, centering the view rectangle
                relative_x = (mouse_x - mini_map_x - tile_offset_x) / mini_map_width 
                relative_y = (mouse_y - mini_map_y) / mini_map_height

                # Calculate offset to center the view on clicked position
                self.offset_x = int(relative_x * self.game_data.map.width * self.TILE_WIDTH)
                self.offset_y = int(relative_y * self.game_data.map.height * self.TILE_HEIGHT)

    def display_player_resources(self):
        font = pygame.font.Font(None, 32)
        x_start = 10
        y_start = 10
        line_height = 20
        box_padding = 10
        box_color = (30, 30, 30, 100)
        text_color = (255, 255, 255)

        for i, player in enumerate(self.game_data.players):
            y_position = y_start + i * (line_height * 6)
            
            resources_text = f"Player {player.id} ({player.name})"
            resources_surface = font.render(resources_text, True, text_color)
            
            resource_lines = [
                f"Wood: {player.owned_resources['Wood']}",
                f"Food: {player.owned_resources['Food']}",
                f"Gold: {player.owned_resources['Gold']}",
                f"Buildings: {len(player.buildings)}",
            ]
            resource_surfaces = [font.render(line, True, text_color) for line in resource_lines]
            
            max_text_width = max([surface.get_width() for surface in resource_surfaces])
            box_width = max_text_width + 2 * box_padding
            box_height = (len(resource_lines) + 1) * line_height + box_padding
            
            box_rect = pygame.Rect(x_start, y_position, box_width, box_height)
            box_surface = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
            box_surface.fill(box_color)
            self.screen.blit(box_surface, box_rect.topleft)
            
            self.screen.blit(resources_surface, (x_start + box_padding, y_position + box_padding))
            for j, resource_surface in enumerate(resource_surfaces):
                self.screen.blit(resource_surface, 
                    (x_start + box_padding, y_position + box_padding + (j + 1) * line_height))
                
    def is_behind_building(villager, building):
        villager_x, villager_y = villager.position
        building_x, building_y = building.position
        building_name = building.name  # Utilisez l'attribut name pour identifier le type de bâtiment

        # Définir les types de bâtiments qui bloquent la vue
        blocking_buildings = {'Town Center', 'Barracks', 'Stables'}  # Assurez-vous que les noms correspondent à ceux définis dans les instances de Building

        # Vérifiez si le villageois est directement derrière le bâtiment en coordonnée y
        if building_name in blocking_buildings and villager_y > building_y:
            return True

        return False
    def handle_keyboard_input(self):
        """Handle keyboard input for map scrolling"""
        keys = pygame.key.get_pressed()
        scroll_speed = 20
    
        if self.game_data and self.game_data.map:
            if keys[pygame.K_UP] and self.offset_y > self.game_data.map.height - self.TILE_HEIGHT:
                self.offset_y -= scroll_speed
            if keys[pygame.K_DOWN] and self.offset_y < ((self.game_data.map.height + 1) * (self.TILE_HEIGHT + 1) - GUI_size.y):
                self.offset_y += scroll_speed
            if keys[pygame.K_LEFT] and self.offset_x > (-(self.game_data.map.width + 1) * self.TILE_WIDTH + GUI_size.x) // 2:
                self.offset_x -= scroll_speed
            if keys[pygame.K_RIGHT] and self.offset_x < ((self.game_data.map.width - 1) * self.TILE_WIDTH) // 2:
                self.offset_x += scroll_speed

    def handle_events(self):
        """Handle all pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F12:
                    print("F12 pressed, stopping the application.")
                    self.running = False
                elif event.key == pygame.K_F2:
                    self.show_resources = not self.show_resources
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mini_map_click(event)

        self.handle_keyboard_input()

    def update_display(self):
        """Update the complete display"""
        if not self.game_data:
            return
            
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Draw all elements
        self.draw_isometric_map()
        
        # Draw units for all players
        if hasattr(self.game_data, 'players'):
            self.draw_resources()
            for player in self.game_data.players:
                self.draw_buildings(player.buildings)
                for unit in player.units:
                    unit_type = type(unit).__name__
                    if unit_type == "Villager":
                        self.draw_villagers([unit],player.buildings)
                    elif unit_type == "Swordsman":
                        self.draw_swordman([unit])
                    elif unit_type == "Archer":
                        self.draw_archer([unit])
                    elif unit_type == "Horseman":
                        self.draw_horseman([unit])
                
    
        
        # Draw mini-map
        self.draw_mini_map()
        
        # Draw resources if enabled
        if self.show_resources:
            self.display_player_resources()
        
        # Ajouter l'affichage des FPS juste avant le flip
        self.display_fps()
        pygame.display.flip()

    def initialize_pygame(self):
        """Initialize pygame and create the display"""
        pygame.init()
        self.screen = pygame.display.set_mode((GUI_size.x, GUI_size.y), FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)  # Initialisation de la police
        self.load_resources()

    def display_fps(self):
        """Affiche les FPS dans le coin supérieur droit"""
        fps = int(self.clock.get_fps())
        fps_text = self.font.render(f'FPS: {fps}', True, (255, 255, 255))
        fps_rect = fps_text.get_rect(topright=(self.screen.get_width() - 10, 10))
        self.screen.blit(fps_text, fps_rect)

    def run(self):
        """Main thread loop"""
        try:
            self.initialize_pygame()
            self.running = True
            
            while self.running:
                # Check for new game data without blocking
                try:
                    new_data = self.data_queue.get_nowait()
                    if new_data is not None:
                        self.game_data = new_data
                except queue.Empty:
                    pass
                
                # Handle events and update display
                self.handle_events()
                self.update_display()
                
                # Maintain frame rate
                self.clock.tick(60)
                
        except Exception as e:
            print(f"Error in GUI thread: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up pygame resources"""
        if pygame.get_init():
            pygame.quit()

    def stop(self):
        """Stop the GUI thread safely"""
        self.running = False
        self.join()  # Wait for the thread to finish