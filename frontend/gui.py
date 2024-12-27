import pygame
from backend.Starter_File import GUI_size
from backend.Building import TownCenter
from frontend.Terrain import Map
from pathlib import Path
import os

# Define isometric tile dimensions
TILE_WIDTH = 64
TILE_HEIGHT = 32

# Define colors for different players' town centers
PLAYER_COLORS = {
    1: (0, 0, 255),  # Blue for Player 1
    2: (255, 0, 0),  # Red for Player 2
    3: (128, 0, 128) # Purple for Player 3
}

# Initialize pygame
pygame.init()

# Initialize the display (required before using convert_alpha or convert)
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600 
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# Define paths using pathlib
BASE_PATH = Path(__file__).resolve().parent.parent  
RESOURCES_PATH = BASE_PATH / "assets" / "resources"
BUILDINGS_PATH = BASE_PATH / "assets" / "buildings"

assert RESOURCES_PATH.exists(), f"Resources directory {RESOURCES_PATH} does not exist."
assert BUILDINGS_PATH.exists(), f"Buildings directory {BUILDINGS_PATH} does not exist."

# Helper function to load images
def load_image(file_path):
    try:
        return pygame.image.load(file_path).convert_alpha()
    except pygame.error as e:
        print(f"Error loading image {file_path}: {e}")
        return pygame.Surface((TILE_WIDTH, TILE_HEIGHT))  # Return a placeholder surface

# Define resource images
IMAGES = {
    "Wood": load_image(RESOURCES_PATH / "tree_0.png"),
    "Gold": load_image(RESOURCES_PATH / "gold.png"),
    "Soil": load_image(RESOURCES_PATH / "soil.png"),
    # Add more resources as needed
}

# Define building images
building_images = {
    "TownCenter": load_image(BUILDINGS_PATH / "tower.png"),
    "Barracks": load_image(BUILDINGS_PATH / "barrack.png"),
    "House": load_image(BUILDINGS_PATH / "house.png"),
    "Rubble": load_image(BUILDINGS_PATH / "rubble.png"),
    "Stable": load_image(BUILDINGS_PATH / "stable.png"),
    "ArcheryRange": load_image(BUILDINGS_PATH / "archeryrange.png"),
    "Camp": load_image(BUILDINGS_PATH / "camp.png"),
    "Farm": load_image(BUILDINGS_PATH / "farm.png"),
    "keep": load_image(BUILDINGS_PATH / "keep.png"),
}

# Resize building images
for key, image in building_images.items():
    if 'TownCenter' == key:
        building_images[key] = pygame.transform.scale(image, (256, 256))  # Exemple pour TownCenter qui occupe 4x4 tuiles
    else:
        building_images[key] = pygame.transform.scale(image, (64, 64))  # Taille standard pour les autres bâtiments

# Define colors for different resources
COLORS = {
    "Wood": (34, 139, 34),  # Dark green for wood
    "Gold": (255, 215, 0),  # Gold color
    "Soil": (0, 255, 0)    # Green for soil
}

# Convert 2D grid coordinates to isometric coordinates
def cart_to_iso(cart_x, cart_y):
    iso_x = (cart_x - cart_y) * (TILE_WIDTH // 2)
    iso_y = (cart_x + cart_y) * (TILE_HEIGHT // 2)
    return iso_x, iso_y

# Calculate building dimensions
barracks_width = TILE_WIDTH * 3
barracks_height = TILE_HEIGHT * 3 * 2  # La hauteur est doublée pour maintenir l'aspect isométrique

# Resize and assign images for buildings
building_images['Barracks'] = pygame.transform.scale(
    load_image(BUILDINGS_PATH / "barrack.png"),
    (barracks_width, barracks_height)
)

TownCenter_width = TILE_WIDTH * 4
TownCenter_height = TILE_HEIGHT * 8  # La hauteur est doublée pour maintenir l'aspect isométrique

building_images['TownCenter'] = pygame.transform.scale(
     load_image(BUILDINGS_PATH / "towncenter.png"),
    (TownCenter_width, TownCenter_height)
)

House_width = TILE_WIDTH * 2
House_height = TILE_HEIGHT * 4

building_images['House'] = pygame.transform.scale(
    load_image(BUILDINGS_PATH / "house.png"),
    (House_width, House_height)
)

Stable_width = TILE_WIDTH * 3
Stable_height = TILE_HEIGHT * 6

building_images['Stable'] = pygame.transform.scale(
    load_image(BUILDINGS_PATH / "stable.png"),
    (Stable_width, Stable_height)  # Taille ajustée pour couvrir 3x3 tuiles
)

ArcheryRange_width = TILE_WIDTH * 2
ArcheryRange_height = TILE_HEIGHT * 4

building_images['ArcheryRange'] = pygame.transform.scale(
    load_image(BUILDINGS_PATH / "archeryrange.png"),
    (ArcheryRange_width, ArcheryRange_height)  # Taille ajustée pour couvrir 2x2 tuiles
)
'''
    "Camp": load_image(BUILDINGS_PATH / "camp.png"),
    "Farm": load_image(BUILDINGS_PATH / "farm.png"),
    "keep": load_image(BUILDINGS_PATH / "keep.png"),
'''

Camp_width = TILE_WIDTH * 2
Camp_height = TILE_HEIGHT * 4

building_images['Camp'] = pygame.transform.scale(
    load_image(BUILDINGS_PATH / "camp.png"),
    (Camp_width, Camp_height)  # Taille ajustée pour couvrir 2x2 tuiles
)

Farm_width = TILE_WIDTH * 2
Farm_height = TILE_HEIGHT * 4

building_images['Farm'] = pygame.transform.scale(
    load_image(BUILDINGS_PATH / "farm.png"),
    (Farm_width, Farm_height)  # Taille ajustée pour couvrir 2x2 tuiles
)

def draw_isometric_map(screen, game_map, offset_x, offset_y):
    for y in range(game_map.height):
        for x in range(game_map.width):
            tile = game_map.grid[y][x]

            # Blit de la texture de sol d'abord
            soil_image = IMAGES['Soil']
            iso_x, iso_y = cart_to_iso(x, y)
            screen_x = (GUI_size.x // 2) + iso_x - offset_x
            screen_y = (GUI_size.y // 4) + iso_y - offset_y - (soil_image.get_height() - TILE_HEIGHT)
            screen.blit(soil_image, (screen_x, screen_y))

            # Ensuite, blit de la ressource si présente
            if tile.resource:
                resource_type = tile.resource.type
                image = IMAGES[resource_type]
                # Ajuster le screen_y pour l'image de la ressource
                screen_y -= (image.get_height() - TILE_HEIGHT)  # Cette ligne peut être ajustée selon vos besoins
                screen.blit(image, (screen_x, screen_y))
            
            if tile.building and (x, y) == tile.building.position:  # Only draw the image of the construction at the original location to avoid duplicate drawings.
                building_type = tile.building.name.replace(" ", "")
                if building_type in building_images:
                    building_image = building_images[building_type]
                    # Adjust y coordinates for precise alignment
                    building_adjusted_y = screen_y - (building_image.get_height() - TILE_HEIGHT)
                    screen.blit(building_image, (screen_x, building_adjusted_y))
                else:
                    print(f"Building type {building_type} not found in building_images dictionary.")

def draw_mini_map(screen, game_map, offset_x, offset_y):
    mini_map_width = 200
    mini_map_height = 150
    mini_map_x = screen.get_width() - mini_map_width - 10
    mini_map_y = screen.get_height() - mini_map_height - 10

    # Draw mini-map background
    pygame.draw.rect(screen, (50, 50, 50), (mini_map_x, mini_map_y, mini_map_width, mini_map_height))

    # Define an additional offset to shift tiles further right
    tile_offset_x = 100  # Change this value to adjust how far right the tiles are displayed

    # Draw the entire game map scaled down
    for y in range(game_map.height):
        for x in range(game_map.width):
            tile = game_map.grid[y][x]  # Correctly access the tile from the grid

            # Check if the tile has a TownCenter
            if isinstance(tile.building, TownCenter):
                player = tile.building.player
                color = PLAYER_COLORS.get(player.id, (255, 255, 255))  # Default to white if no player color
            else:
                resource_type = tile.resource.type if tile.resource else "Soil"
                color = COLORS[resource_type]

            iso_x, iso_y = cart_to_iso(x, y)

            # Scale coordinates for mini-map with offset
            mini_map_iso_x = mini_map_x + (iso_x * (mini_map_width / (game_map.width * TILE_WIDTH))) + tile_offset_x
            mini_map_iso_y = mini_map_y + (iso_y * (mini_map_height / (game_map.height * TILE_HEIGHT)))

            # Draw the tile on the mini-map
            pygame.draw.rect(screen, color, (mini_map_iso_x, mini_map_iso_y, 2, 2))  # Draw a small rectangle

    # Calculate and draw the view rectangle on the mini-map
    view_rect_x = mini_map_x + ((offset_x / (game_map.width * TILE_WIDTH)) * mini_map_width) + (tile_offset_x - game_map.width // 12)
    view_rect_y = mini_map_y + ((offset_y / (game_map.height * TILE_HEIGHT)) * mini_map_height) - (game_map.height // 20)
    view_rect_width = (GUI_size.x / (game_map.width * TILE_WIDTH)) * mini_map_width
    view_rect_height = (GUI_size.y / (game_map.height * TILE_HEIGHT)) * mini_map_height

    pygame.draw.rect(screen, (255, 0, 0), (view_rect_x, view_rect_y, view_rect_width, view_rect_height), 2)  # Red outline



def run_gui_mode(game_engine):
    pygame.init()
    
    screen = pygame.display.set_mode((GUI_size.x, GUI_size.y))
    clock = pygame.time.Clock()

    offset_x, offset_y = 0, game_engine.map.height + TILE_HEIGHT

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F12:
                    running = False

        keys = pygame.key.get_pressed()
        scroll_speed = 20

        if keys[pygame.K_UP] and offset_y > game_engine.map.height + TILE_HEIGHT:
            offset_y -= scroll_speed
        if keys[pygame.K_DOWN] and offset_y < (game_engine.map.height * (TILE_HEIGHT+1) - GUI_size.y + TILE_HEIGHT):
            offset_y += scroll_speed
        if keys[pygame.K_LEFT] and offset_x > (-game_engine.map.width * TILE_WIDTH + GUI_size.x)//2:
            offset_x -= scroll_speed
        if keys[pygame.K_RIGHT] and offset_x < (game_engine.map.width * TILE_WIDTH - GUI_size.x)//2:
            offset_x += scroll_speed

        screen.fill((0, 0, 0))

        draw_isometric_map(screen, game_engine.map, offset_x, offset_y)
        draw_mini_map(screen, game_engine.map, offset_x, offset_y)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()   