#Config File

import pygame
import sys
import curses
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
    Player('Player 2', "Leans", "defensive", player_id=2),
    Player('Player 3', "Marines", "aggressive", player_id=3),
]

global_speedS = 1

class StartMenu:
    def __init__(self, screen_width=800, screen_height=600):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("AIge of Empire")
        
        self.colors = {
            'background': (50, 50, 50),
            'button': (100, 100, 100),
            'button_hover': (150, 150, 150),
            'text': (255, 255, 255)
        }
        
        self.buttons = [
            {'text': 'Start Game', 'rect': pygame.Rect(300, 250, 200, 50)},
            {'text': 'Settings', 'rect': pygame.Rect(300, 320, 200, 50)},
            {'text': 'Exit', 'rect': pygame.Rect(300, 390, 200, 50)}
        ]
        self.font = pygame.font.Font(None, 48)
    
    def draw(self):
        self.screen.fill(self.colors['background'])
        
        title = self.font.render("AIge of Yuki", True, self.colors['text'])
        title_rect = title.get_rect(center=(400, 150))
        self.screen.blit(title, title_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
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
        curses.wrapper(lambda stdscr: start_game(stdscr, save_file))
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