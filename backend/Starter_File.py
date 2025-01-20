#Config File
import pygame
import sys
import curses
import os
from Players import *


# Game Mode
GameMode = "Utopia" # "Utopia" or "Gold Rush"

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

    Player('Player 3', "Marines", "aggressive", player_id=3),
]

global_speedS = 50

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
        
        self.buttons = [
            {'text': 'Start Game', 'rect': pygame.Rect(300, 220, 200, 50)},
            {'text': 'Load Game', 'rect': pygame.Rect(300, 290, 200, 50)},
            {'text': 'Settings', 'rect': pygame.Rect(300, 360, 200, 50)},
            {'text': 'Exit', 'rect': pygame.Rect(300, 430, 200, 50)}
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

def start_menu(save_file=None):
    menu = StartMenu()
    action = menu.run()
    
    if action == 'Start Game':
        pygame.quit()
        from Game_Engine import GameEngine
        curses.wrapper(lambda stdscr: start_game(stdscr, None))
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
    elif action == 'Settings':
        print("Settings menu (Pas encore fait)")
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
