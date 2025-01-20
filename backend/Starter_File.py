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
    Player('Player 2', "Leans", "aggressive", player_id=2),
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

def start_menu(save_file=None):
    menu = StartMenu()
    action = menu.run()
    pygame.quit()
    
    if action == 'Start Game':
        from Game_Engine import GameEngine
        curses.wrapper(lambda stdscr: start_game(stdscr, None))
    elif action == 'Load Game' and menu.has_saves:
        from Game_Engine import GameEngine
        save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'annex')
        save_files = sorted([f for f in os.listdir(save_dir) if f.startswith('game_save') and f.endswith('.dat')])
        if save_files:
            save_path = os.path.join(save_dir, save_files[-1])
            curses.wrapper(lambda stdscr: start_game(stdscr, save_path))
    elif action == 'Settings':
        print("Settings menu (Pas encore fait)")
        sys.exit()
    elif action in ['Exit', 'quit']:
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