import pygame
from backend.Starter_File import GUI_size
from backend.Building import TownCenter
from frontend.Terrain import Map

#branch testt
# Define isometric tile dimensions
TILE_WIDTH = 64
TILE_HEIGHT = 32

# Define colors for different players' town centers
PLAYER_COLORS = {
    1: (0, 0, 255),  # Blue for Player 1
    2: (255, 0, 0),  # Red for Player 2
    3: (128, 0, 128) # Purple for Player 3
}

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

# Draw the isometric map, taking camera offset into account
def draw_isometric_map(screen, game_map, offset_x, offset_y):
    for y in range(game_map.height):
        for x in range(game_map.width):
            tile = game_map.grid[y][x]  # Correctly refer to the `grid` of the `game_map` instance
            
            # Check if there is a building on the tile
            if isinstance(tile.building, TownCenter):  # Use `isinstance` to check for a TownCenter instance
                player = tile.building.player
                color = PLAYER_COLORS.get(player.id, (255, 255, 255))  # Default to white if no player color
            else:
                resource_type = tile.resource.type if tile.resource else "Soil"
                color = COLORS[resource_type]

            iso_x, iso_y = cart_to_iso(x, y)

            screen_x = (GUI_size.x // 2) + iso_x - offset_x
            screen_y = (GUI_size.y // 4) + iso_y - offset_y

            if -TILE_WIDTH < screen_x < GUI_size.x + TILE_WIDTH and -TILE_HEIGHT < screen_y < GUI_size.y + TILE_HEIGHT:
                pygame.draw.polygon(screen, color, [
                    (screen_x, screen_y),
                    (screen_x + TILE_WIDTH // 2, screen_y + TILE_HEIGHT // 2),
                    (screen_x, screen_y + TILE_HEIGHT),
                    (screen_x - TILE_WIDTH // 2, screen_y + TILE_HEIGHT // 2)
                ])



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