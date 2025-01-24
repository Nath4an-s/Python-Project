#Config File
import pygame
import sys
import curses
import os
from Players import *


# Game Mode
GameMode = None # "Utopia" or "Gold Rush"

# Set up map size
map_size = (120, 120) #minimum 120x120

# Set up GUI size
GUI_size = type('GUI_size', (object,), {})()
GUI_size.x = 800
GUI_size.y = 600

# Initialize players with both name and AI profile
#Civilizations are either Leans, Means or Marines
players = [
    Player('Player 1', "Means", "aggressive", player_id=1),
    Player('Player 2', "Leans", "aggressive", player_id=2),
    Player('Player 3', "Marines", "aggressive", player_id=3),
]

global_speedS = 3

class StartMenu:
    def __init__(self, screen_width=800, screen_height=600):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("AIge of Empire")
        
        self.colors = {
            'background': (50, 50, 50),
            'button': (100, 100, 100),
            'button_hover': (150, 150, 150),
            'text': (255, 255, 255),
            'disabled': (80, 80, 80)  # Color for disabled buttons
        }
        
        # Adjusted button positions for 3 buttons
        self.buttons = [
            {'text': 'Start Game', 'rect': pygame.Rect(300, 250, 200, 50)},
            {'text': 'Load Game', 'rect': pygame.Rect(300, 320, 200, 50)},
            {'text': 'Exit', 'rect': pygame.Rect(300, 390, 200, 50)}
        ]
        self.font = pygame.font.Font(None, 48)
        
        # Check for save files
        self.has_saves = self.check_save_files()
    
    def check_save_files(self):
        save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'annex')
        save_files = [f for f in os.listdir(save_dir) if f.startswith('game_save') and f.endswith('.dat')]
        return len(save_files) > 0
    
    def draw(self):
        self.screen.fill(self.colors['background'])
        
        title = self.font.render("AIge of Empire", True, self.colors['text'])
        title_rect = title.get_rect(center=(400, 150))
        self.screen.blit(title, title_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            # Disable Load Game button if no saves exist
            if button['text'] == 'Load Game' and not self.has_saves:
                color = self.colors['disabled']
            else:
                color = self.colors['button_hover'] if button['rect'].collidepoint(mouse_pos) else self.colors['button']
            
            pygame.draw.rect(self.screen, color, button['rect'], border_radius=5)
            
            text = self.font.render(button['text'], True, self.colors['text'])
            text_rect = text.get_rect(center=button['rect'].center)
            self.screen.blit(text, text_rect)
    
    def run(self):
        running = True
        while running:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit'
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    for button in self.buttons:
                        if button['rect'].collidepoint(mouse_pos):
                            return button['text']
            
            pygame.display.flip()

class LoadGameMenu:
    def __init__(self, screen_width=800, screen_height=600):
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("AIge of Empire - Charger une partie")
        
        self.colors = {
            'background': (50, 50, 50),
            'button': (100, 100, 100),
            'button_hover': (150, 150, 150),
            'text': (255, 255, 255),
            'selected': (120, 160, 120),
            'disabled': (80, 80, 80),
            'scrollbar': (70, 70, 70),
            'scrollbar_hover': (90, 90, 90)
        }
        
        # Get save files
        self.save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'annex')
        self.save_files = sorted([f for f in os.listdir(self.save_dir) if f.startswith('game_save') and f.endswith('.dat')])
        
        # Scroll settings
        self.scroll_y = 0
        self.visible_saves = 6  # Number of saves visible at once
        self.button_height = 60
        self.button_spacing = 0
        self.scroll_area_height = self.visible_saves * (self.button_height + self.button_spacing)
        self.total_height = len(self.save_files) * (self.button_height + self.button_spacing)
        
        # Scrollbar
        self.scrollbar_width = 20
        self.scrollbar_height = (self.scroll_area_height / self.total_height) * self.scroll_area_height if self.total_height > self.scroll_area_height else 0
        self.scrollbar_rect = pygame.Rect(620, 150, self.scrollbar_width, self.scrollbar_height)
        self.scrolling = False
        
        # Create buttons for save files
        self.save_buttons = []
        for i, save_file in enumerate(self.save_files):
            y_pos = 150 + i * self.button_height
            self.save_buttons.append({
                'text': save_file,
                'rect': pygame.Rect(200, y_pos, 400, 50),
                'path': os.path.join(self.save_dir, save_file)
            })
        
        # Navigation buttons
        self.back_button = {'text': 'Retour', 'rect': pygame.Rect(50, 500, 120, 50)}
        self.load_button = {'text': 'Charger', 'rect': pygame.Rect(630, 500, 120, 50)}
        
        self.selected_save = None
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)

    def handle_scroll(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Mouse wheel up
                self.scroll_y = max(0, self.scroll_y - 30)
                self._update_scrollbar_position()
            elif event.button == 5:  # Mouse wheel down
                max_scroll = max(0, self.total_height - self.scroll_area_height)
                self.scroll_y = min(max_scroll, self.scroll_y + 30)
                self._update_scrollbar_position()
            elif self.scrollbar_rect.collidepoint(event.pos):  # Click on scrollbar
                self.scrolling = True
                self.scroll_start_y = event.pos[1]  # Save initial click position
                self.initial_scroll_y = self.scroll_y  # Save initial scroll position
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.scrolling = False
        
        elif event.type == pygame.MOUSEMOTION and self.scrolling:
            # Calculate movement delta
            delta_y = event.pos[1] - self.scroll_start_y
            scroll_range = self.scroll_area_height - self.scrollbar_height
            
            # Convert pixel movement to scroll movement
            scroll_delta = (delta_y / scroll_range) * (self.total_height - self.scroll_area_height)
            new_scroll = self.initial_scroll_y + scroll_delta
            
            # Apply bounds
            self.scroll_y = max(0, min(new_scroll, self.total_height - self.scroll_area_height))
            self._update_scrollbar_position()

    def _update_scrollbar_position(self):
        """Update scrollbar position based on current scroll_y"""
        if self.total_height > self.scroll_area_height:
            scroll_ratio = self.scroll_y / (self.total_height - self.scroll_area_height)
            scroll_range = self.scroll_area_height - self.scrollbar_height
            self.scrollbar_rect.y = 150 + scroll_ratio * scroll_range

    def draw(self):
        # Draw background
        self.screen.fill(self.colors['background'])
        
        # Draw title
        title = self.title_font.render("Charger une partie", True, self.colors['text'])
        title_rect = title.get_rect(center=(400, 80))
        self.screen.blit(title, title_rect)
        
        # Create a surface for the save list area
        save_list_surface = pygame.Surface((400, self.scroll_area_height))
        save_list_surface.fill(self.colors['background'])
        
        # Draw save file buttons
        mouse_pos = pygame.mouse.get_pos()
        visible_area = pygame.Rect(200, 150, 400, self.scroll_area_height)
        
        for i, button in enumerate(self.save_buttons):
            button_y = i * self.button_height - self.scroll_y
            if -self.button_height <= button_y <= self.scroll_area_height:
                # Update button rect position
                button['rect'].y = button_y + 150
                
                # Determine button color based on state
                color = self.colors['selected'] if button == self.selected_save else \
                       self.colors['button_hover'] if button['rect'].collidepoint(mouse_pos) else \
                       self.colors['button']
                
                # Draw button if it's in the visible area
                if visible_area.colliderect(button['rect']):
                    pygame.draw.rect(self.screen, color, button['rect'], border_radius=5)
                    text = self.font.render(button['text'], True, self.colors['text'])
                    text_rect = text.get_rect(center=button['rect'].center)
                    self.screen.blit(text, text_rect)
        
        # Draw scrollbar background
        if self.total_height > self.scroll_area_height:
            pygame.draw.rect(self.screen, self.colors['scrollbar'], 
                           (620, 150, self.scrollbar_width, self.scroll_area_height))
            
            # Draw scrollbar
            scrollbar_color = self.colors['scrollbar_hover'] if self.scrollbar_rect.collidepoint(mouse_pos) else self.colors['button']
            pygame.draw.rect(self.screen, scrollbar_color, self.scrollbar_rect)
        
        # Draw navigation buttons
        back_color = self.colors['button_hover'] if self.back_button['rect'].collidepoint(mouse_pos) else self.colors['button']
        pygame.draw.rect(self.screen, back_color, self.back_button['rect'], border_radius=5)
        back_text = self.font.render(self.back_button['text'], True, self.colors['text'])
        back_rect = back_text.get_rect(center=self.back_button['rect'].center)
        self.screen.blit(back_text, back_rect)
        
        load_color = self.colors['disabled'] if not self.selected_save else \
                    self.colors['button_hover'] if self.load_button['rect'].collidepoint(mouse_pos) else \
                    self.colors['button']
        pygame.draw.rect(self.screen, load_color, self.load_button['rect'], border_radius=5)
        load_text = self.font.render(self.load_button['text'], True, self.colors['text'])
        load_rect = load_text.get_rect(center=self.load_button['rect'].center)
        self.screen.blit(load_text, load_rect)

    def run(self):
        running = True
        while running:
            self.draw()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = event.pos
                        
                        # Handle save file selection
                        for button in self.save_buttons:
                            if button['rect'].collidepoint(mouse_pos):
                                self.selected_save = button
                        
                        # Handle back button
                        if self.back_button['rect'].collidepoint(mouse_pos):
                            return 'back'
                        
                        # Handle load button
                        if self.load_button['rect'].collidepoint(mouse_pos) and self.selected_save:
                            return self.selected_save['path']
                    
                    # Handle scrolling
                    self.handle_scroll(event)
                
                elif event.type == pygame.MOUSEMOTION and self.scrolling:
                    self.handle_scroll(event)
            
            pygame.display.flip()

class GameSettingsMenu:
    def __init__(self, screen_width=800, screen_height=600):
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("AIge of Empire - Paramètres de la partie")
        
        # Store screen dimensions and center position
        self.screen_width = screen_width
        self.center_x = screen_width // 2
        
        self.colors = {
            'background': (50, 50, 50),
            'button': (100, 100, 100),
            'button_hover': (150, 150, 150),
            'text': (255, 255, 255),
            'selected': (120, 160, 120),
            'input_bg': (70, 70, 70)
        }
        
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        
        # Game settings
        self.game_modes = ["Utopia", "Gold Rush"]
        self.current_mode = 0
        global GameMode
        GameMode = self.game_modes[self.current_mode]
        self.map_width = 120
        self.map_height = 120
        self.num_players = 3
        
        # Popup settings
        self.show_mode_popup = False
        button_width = 200
        button_height = 50
        
        # Mode button
        self.mode_button = {
            'text': self.game_modes[self.current_mode], 
            'rect': pygame.Rect(self.center_x - button_width//2, 150, button_width, button_height)
        }
        
        # Create mode selection buttons for popup
        popup_x = self.mode_button['rect'].right + 10  # Position popup to the right of the mode button
        self.mode_options = []
        for i, mode in enumerate(self.game_modes):
            self.mode_options.append({
                'text': mode,
                'rect': pygame.Rect(popup_x, 150 + i * 50, button_width, button_height)
            })
        
        # Update popup background rect
        self.popup_rect = pygame.Rect(popup_x, 150, 
                                    button_width, len(self.game_modes) * 50)
        
        # Map size controls as buttons
        self.width_button = {
            'text': f"{self.map_width}",
            'rect': pygame.Rect(self.center_x - 100, 250, 80, 50),
            'active': False
        }
        
        self.height_button = {
            'text': f"{self.map_height}",
            'rect': pygame.Rect(self.center_x + 20, 250, 80, 50),
            'active': False
        }
        
        # Player count controls
        self.player_decrease = {'text': '-', 'rect': pygame.Rect(self.center_x - 140, 350, 50, button_height)}
        self.player_display = {'text': str(self.num_players), 
                             'rect': pygame.Rect(self.center_x - 60, 350, 120, button_height)}
        self.player_increase = {'text': '+', 'rect': pygame.Rect(self.center_x + 90, 350, 50, button_height)}
        
        # Navigation buttons
        self.start_button = {'text': 'Commencer', 'rect': pygame.Rect(self.center_x + 20, 500, 150, button_height)}
        self.back_button = {'text': 'Retour', 'rect': pygame.Rect(self.center_x - 170, 500, 150, button_height)}

    def draw(self):
        # Draw main menu
        self.screen.fill(self.colors['background'])
        
        # Draw title
        title = self.title_font.render("Paramètres de la partie", True, self.colors['text'])
        title_rect = title.get_rect(center=(400, 80))
        self.screen.blit(title, title_rect)
        
        # Draw labels
        mode_label = self.font.render("Mode de jeu:", True, self.colors['text'])
        self.screen.blit(mode_label, (200, 160))
        
        players_label = self.font.render("Nombre de joueurs:", True, self.colors['text'])
        self.screen.blit(players_label, (200, 360))
        
        # Draw map size label
        map_size_label = self.font.render("Taille de la carte:", True, self.colors['text'])
        self.screen.blit(map_size_label, (200, 250))
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw mode button
        color = self.colors['button_hover'] if self.mode_button['rect'].collidepoint(mouse_pos) else self.colors['button']
        pygame.draw.rect(self.screen, color, self.mode_button['rect'], border_radius=5)
        text = self.font.render(self.mode_button['text'], True, self.colors['text'])
        text_rect = text.get_rect(center=self.mode_button['rect'].center)
        self.screen.blit(text, text_rect)
        
        # Draw mode selection popup if active
        if self.show_mode_popup:
            pygame.draw.rect(self.screen, self.colors['background'], self.popup_rect)
            pygame.draw.rect(self.screen, self.colors['button'], self.popup_rect, 2)
            for option in self.mode_options:
                color = self.colors['button_hover'] if option['rect'].collidepoint(mouse_pos) else self.colors['button']
                pygame.draw.rect(self.screen, color, option['rect'], border_radius=5)
                text = self.font.render(option['text'], True, self.colors['text'])
                text_rect = text.get_rect(center=option['rect'].center)
                self.screen.blit(text, text_rect)
        
        # Draw width and height buttons
        for button in [self.width_button, self.height_button]:
            color = self.colors['button_hover'] if button['rect'].collidepoint(mouse_pos) else self.colors['button']
            pygame.draw.rect(self.screen, color, button['rect'], border_radius=5)
            text = self.font.render(button['text'], True, self.colors['text'])
            text_rect = text.get_rect(center=button['rect'].center)
            self.screen.blit(text, text_rect)
        
        # Draw player count controls
        for button in [self.player_decrease, self.player_display, self.player_increase]:
            color = self.colors['button_hover'] if button['rect'].collidepoint(mouse_pos) else self.colors['button']
            pygame.draw.rect(self.screen, color, button['rect'], border_radius=5)
            text = self.font.render(button['text'], True, self.colors['text'])
            text_rect = text.get_rect(center=button['rect'].center)
            self.screen.blit(text, text_rect)
        
        # Draw navigation buttons
        for button in [self.start_button, self.back_button]:
            color = self.colors['button_hover'] if button['rect'].collidepoint(mouse_pos) else self.colors['button']
            pygame.draw.rect(self.screen, color, button['rect'], border_radius=5)
            text = self.font.render(button['text'], True, self.colors['text'])
            text_rect = text.get_rect(center=button['rect'].center)
            self.screen.blit(text, text_rect)

    def run(self):
        running = True
        while running:
            self.draw()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    
                    # Handle game mode selection
                    if self.mode_button['rect'].collidepoint(mouse_pos):
                        self.show_mode_popup = not self.show_mode_popup
                    elif self.show_mode_popup:
                        for i, option in enumerate(self.mode_options):
                            if option['rect'].collidepoint(mouse_pos):
                                self.current_mode = i
                                self.mode_button['text'] = self.game_modes[i]
                                global GameMode
                                GameMode = self.game_modes[i]
                                self.show_mode_popup = False
                                break
                        # Close popup if clicked outside
                        if not self.popup_rect.collidepoint(mouse_pos):
                            self.show_mode_popup = False
                    
                    # Handle width button click
                    if self.width_button['rect'].collidepoint(mouse_pos):
                        self.width_input['text'] = str(self.map_width)  # Keep the current width value
                        self.width_input['active'] = True
                    
                    # Handle height button click
                    if self.height_button['rect'].collidepoint(mouse_pos):
                        self.height_input['text'] = str(self.map_height)  # Keep the current height value
                        self.height_input['active'] = True
                    
                    # Handle player count
                    elif self.player_decrease['rect'].collidepoint(mouse_pos):
                        self.num_players = max(2, self.num_players - 1)
                        self.player_display['text'] = str(self.num_players)
                    elif self.player_increase['rect'].collidepoint(mouse_pos):
                        self.num_players = min(8, self.num_players + 1)
                        self.player_display['text'] = str(self.num_players)
                    
                    # Handle navigation
                    elif self.back_button['rect'].collidepoint(mouse_pos):
                        return 'back'
                    elif self.start_button['rect'].collidepoint(mouse_pos):
                        return {
                            'mode': self.game_modes[self.current_mode],
                            'map_size': (self.map_width, self.map_height),
                            'num_players': self.num_players
                        }
                    
                elif event.type == pygame.KEYDOWN:
                    # Handle text input for map size
                    if self.width_input['active']:
                        if event.key == pygame.K_BACKSPACE:
                            self.width_input['text'] = self.width_input['text'][:-1]
                        elif event.unicode.isnumeric():
                            self.width_input['text'] += event.unicode
                        elif event.key == pygame.K_RETURN:
                            self.map_width = int(self.width_input['text']) if self.width_input['text'] else 120
                            self.width_input['active'] = False
                    
                    if self.height_input['active']:
                        if event.key == pygame.K_BACKSPACE:
                            self.height_input['text'] = self.height_input['text'][:-1]
                        elif event.unicode.isnumeric():
                            self.height_input['text'] += event.unicode
                        elif event.key == pygame.K_RETURN:
                            self.map_height = int(self.height_input['text']) if self.height_input['text'] else 120
                            self.height_input['active'] = False
            
            pygame.display.flip()

def start_menu(save_file=None):
    menu = StartMenu()
    action = menu.run()
    
    if action == 'Start Game':
        settings_menu = GameSettingsMenu()
        settings = settings_menu.run()
        
        if settings == 'back':
            return start_menu(save_file)
        elif settings:
            pygame.quit()
            from Game_Engine import GameEngine
            # Update global settings
            global GameMode, map_size, players
            GameMode = settings['mode']
            map_size = settings['map_size']
            # Adjust number of players
            players = players[:settings['num_players']]
            while len(players) < settings['num_players']:
                new_id = len(players) + 1
                players.append(Player(f'Player {new_id}', "Means", "aggressive", player_id=new_id))
            
            # Pass the selected game mode to the GameEngine
            curses.wrapper(lambda stdscr: GameEngine(GameMode, map_size, players, sauvegarde=False).run(stdscr))
        else:
            pygame.quit()
            sys.exit()
    elif action == 'Load Game' and menu.has_saves:
        load_menu = LoadGameMenu()
        selected_save = load_menu.run()
        
        if selected_save == 'back':
            return start_menu(save_file)  # Return to main menu
        elif selected_save:  # If a save file was selected
            pygame.quit()
            from Game_Engine import GameEngine
            curses.wrapper(lambda stdscr: start_game(stdscr, selected_save))
        else:  # If window was closed
            pygame.quit()
            sys.exit()
    elif action in ['Exit', 'quit']:
        pygame.quit()
        print("Exiting game")
        sys.exit()

def start_game(stdscr, save_file=None):
    from Game_Engine import GameEngine
    curses.curs_set(0)
    stdscr.clear()
    
    if save_file:
        game_engine = GameEngine(players, map_size, True)
        game_engine.load_game(save_file)
    else:
        game_engine = GameEngine(players, map_size, False)
        print("Starting new game...")

    game_engine.run(stdscr)
