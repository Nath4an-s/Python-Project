import pygame
from pygame.locals import HIDDEN, FULLSCREEN, RESIZABLE, VIDEORESIZE
from backend.Starter_File import GUI_size
from backend.Building import TownCenter
from frontend.Terrain import Map
from backend.Units import Villager
from pathlib import Path
import os
import random
import threading
from queue import Queue
import time

class GUI(threading.Thread):
    def __init__(self, data_queue):
        super().__init__()
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
            3: (0, 255, 0),    # Green
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
        self.villager_image = None
        self.swordman_image = None
        
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
            "Farm": (self.TILE_WIDTH * 2, self.TILE_HEIGHT * 4),
            "keep": (64, 64)
        }

        self.building_images = {}
        for building_type, size in building_types.items():
            image = self.load_image(self.BUILDINGS_PATH / f"{building_type.lower()}.png")
            self.building_images[building_type] = pygame.transform.scale(image, size)

        # Load background
        self.background_texture = self.load_image(self.BACKGROUND_PATH / "background.png")
        
        # Load unit images
        self.villager_image = self.load_image(self.BASE_PATH / "assets" / "units" / "villager" / "Villager.png")
        self.swordman_image = self.load_image(self.BASE_PATH / "assets" / "units" / "swordman" / "Halbadierattack017.png")
        
        # Scale gold and tree images
        self.IMAGES["Gold"] = pygame.transform.scale(self.IMAGES["Gold"], (self.TILE_WIDTH, self.TILE_HEIGHT))
        for i in range(len(self.IMAGES["Wood"])):
            self.IMAGES["Wood"][i] = pygame.transform.scale(self.IMAGES["Wood"][i], (self.TILE_WIDTH, self.TILE_HEIGHT))

    def cart_to_iso(self, cart_x, cart_y):
        iso_x = (cart_x - cart_y) * (self.TILE_WIDTH // 2)
        iso_y = (cart_x + cart_y) * (self.TILE_HEIGHT // 2)
        return iso_x, iso_y

    def draw_isometric_map(self):
        if not self.game_data or not self.game_data.map:
            return

        self.screen.blit(self.background_texture, (0, 0))
        
        for y in range(self.game_data.map.height):
            for x in range(self.game_data.map.width):
                tile = self.game_data.map.grid[y][x]
                
                soil_image = self.IMAGES['Soil']
                iso_x, iso_y = self.cart_to_iso(x, y)
                screen_x = (GUI_size.x // 2) + iso_x - self.offset_x
                screen_y = (GUI_size.y // 4) + iso_y - self.offset_y - (soil_image.get_height() - self.TILE_HEIGHT)
                
                if 0 <= screen_x < self.WINDOW_WIDTH and 0 <= screen_y < self.WINDOW_HEIGHT:
                    self.screen.blit(soil_image, (screen_x, screen_y))
                    
                    if tile.resource:
                        if tile.resource.type == "Wood":
                            pos = (x, y)
                            if pos not in self.trees_drawn:
                                self.trees_drawn[pos] = random.randint(0, 5)
                            image = self.IMAGES["Wood"][self.trees_drawn[pos]]
                            screen_y_adjusted = screen_y - (image.get_height() - self.TILE_HEIGHT)
                            self.screen.blit(image, (screen_x + self.TILE_WIDTH//2, screen_y_adjusted))
                        else:
                            screen_y_adjusted = screen_y - (self.IMAGES["Gold"].get_height() - 2*self.TILE_HEIGHT)
                            self.screen.blit(self.IMAGES["Gold"], (screen_x + self.TILE_WIDTH//2, screen_y_adjusted))
                
                if tile.building and (x - tile.building.size + 1, y - tile.building.size + 1) == tile.building.position:
                    building_type = tile.building.name.replace(" ", "")
                    if building_type in self.building_images:
                        building_image = self.building_images[building_type]
                        building_adjusted_y = screen_y - (building_image.get_height() - self.TILE_HEIGHT)
                        self.screen.blit(building_image, (screen_x, building_adjusted_y))

    def draw_villagers(self, villagers, buildings):
        for villager in sorted(villagers, key=lambda v: v.position[1]):
            villager_x, villager_y = villager.position
            iso_villager_x, iso_villager_y = self.cart_to_iso(villager_x, villager_y)
            screen_x = (GUI_size.x // 2) + iso_villager_x - self.offset_x
            screen_y = (GUI_size.y // 4) + iso_villager_y - self.offset_y - self.villager_image.get_height()

            villager_visible = True
            for building in buildings:
                building_x, building_y = building.position
                building_end_y = building_y + building.size
                if building_y < villager_y < building_end_y:
                    villager_visible = False
                    break

            if villager_visible:
                self.screen.blit(self.villager_image, (screen_x, screen_y))

    def draw_swordman(self, swordmans):
        for swordman in swordmans:
            swordman_x, swordman_y = swordman.position
            iso_x, iso_y = self.cart_to_iso(swordman_x, swordman_y)
            screen_x = (GUI_size.x // 2) + iso_x - self.offset_x + self.TILE_WIDTH // 4 * 3
            screen_y = (GUI_size.y // 4) + iso_y - self.offset_y - (self.swordman_image.get_height())
            self.screen.blit(self.swordman_image, (screen_x, screen_y))

    def draw_mini_map(self):
        mini_map_width = 200
        mini_map_height = 150
        mini_map_x = self.screen.get_width() - mini_map_width - 10
        mini_map_y = self.screen.get_height() - mini_map_height - 10

        pygame.draw.rect(self.screen, (50, 50, 50), (mini_map_x, mini_map_y, mini_map_width, mini_map_height))
        
        tile_offset_x = 100

        for y in range(self.game_data.map.height):
            for x in range(self.game_data.map.width):
                tile = self.game_data.map.grid[y][x]

                if isinstance(tile.building, TownCenter):
                    player = tile.building.player
                    color = self.PLAYER_COLORS.get(player.id, (255, 255, 255))
                else:
                    resource_type = tile.resource.type if tile.resource else "Soil"
                    color = self.COLORS[resource_type]

                iso_x, iso_y = self.cart_to_iso(x, y)
                
                mini_map_iso_x = mini_map_x + (iso_x * (mini_map_width / (self.game_data.map.width * self.TILE_WIDTH))) + tile_offset_x
                mini_map_iso_y = mini_map_y + (iso_y * (mini_map_height / (self.game_data.map.height * self.TILE_HEIGHT)))
                
                pygame.draw.rect(self.screen, color, (mini_map_iso_x, mini_map_iso_y, 2, 2))

        view_rect_x = mini_map_x + ((self.offset_x / (self.game_data.map.width * self.TILE_WIDTH)) * mini_map_width) + (tile_offset_x - self.game_data.map.width // 12)
        view_rect_y = mini_map_y + ((self.offset_y / (self.game_data.map.height * self.TILE_HEIGHT)) * mini_map_height) - (self.game_data.map.height // 20)
        view_rect_width = (GUI_size.x / (self.game_data.map.width * self.TILE_WIDTH)) * mini_map_width
        view_rect_height = (GUI_size.y / (self.game_data.map.height * self.TILE_HEIGHT)) * mini_map_height
        
        pygame.draw.rect(self.screen, (255, 0, 0), (view_rect_x, view_rect_y, view_rect_width, view_rect_height), 2)

    def handle_mini_map_click(self, event):
        mini_map_width = 200
        mini_map_height = 150
        mini_map_x = GUI_size.x - mini_map_width - 10
        mini_map_y = GUI_size.y - mini_map_height - 10

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if (mini_map_x <= mouse_x <= mini_map_x + mini_map_width and 
                mini_map_y <= mouse_y <= mini_map_y + mini_map_height):
                relative_x = (mouse_x - mini_map_x) / mini_map_width
                relative_y = (mouse_y - mini_map_y) / mini_map_height
                
                self.offset_x = int(relative_x * self.game_data.map.width * self.TILE_WIDTH - (GUI_size.x / 2))
                self.offset_y = int(relative_y * self.game_data.map.height * self.TILE_HEIGHT - (GUI_size.y / 2))

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
            for player in self.game_data.players:
                self.draw_villagers(player.units, player.buildings)
                if hasattr(player, 'swordmans'):
                    self.draw_swordman(player.swordmans)
        
        # Draw mini-map
        self.draw_mini_map()
        
        # Draw resources if enabled
        if self.show_resources:
            self.display_player_resources()
        
        # Update display
        pygame.display.flip()

    def initialize_pygame(self):
        """Initialize pygame and create the display"""
        pygame.init()
        self.screen = pygame.display.set_mode((GUI_size.x, GUI_size.y), FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.load_resources()

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
                except Queue.Empty:
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