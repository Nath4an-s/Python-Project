import curses
import time
import subprocess
import os
import threading
import pickle

from logger import debug_print
from Units import *
from Building import *
from frontend.Terrain import Map
try:
    from frontend import gui
    USE_PYGAME = True
except ImportError:
    USE_PYGAME = False
    debug_print("Pygame not installed; running without Pygame features such as 2.5D map view.")

from html_report import generate_html_report
from Actions import Action
from Building import Building

# GameEngine Class
class GameEngine:
    def __init__(self, players, map_size=(120, 120)):
        self.players = players  # List of Player objects
        self.map = Map(*map_size)  # Create a map object
        self.turn = 0
        self.is_paused = False  # Flag to track if the game is paused
        self.changed_tiles = set()  # Set to track changed tiles
        Building.place_starting_buildings(self.map)  # Place starting town centers on the map
        Unit.place_starting_units(self.players, self.map)  # Place starting units on the map
        self.debug_print = debug_print

    def run(self, stdscr):
        # Initialize the starting view position
        top_left_x, top_left_y = 0, 0
        viewport_width, viewport_height = 30, 30

        # Display the initial viewport
        stdscr.clear()  # Clear the screen
        self.map.display_viewport(stdscr, top_left_x, top_left_y, viewport_width, viewport_height, Map_is_paused=self.is_paused)  # Display the initial viewport

        try:
            while not self.check_victory():
                if not self.is_paused:
                    current_time = time.time()

                # Handle input
                curses.curs_set(0)  # Hide cursor
                stdscr.nodelay(True)  # Make getch() non-blocking
                key = stdscr.getch()  # Get the key pressed by the user
                action = Action(self.map)
                if key == curses.KEY_UP or key == ord('z'):
                    top_left_y = max(0, top_left_y - 1)
                elif key == curses.KEY_DOWN or key == ord('s'):
                    top_left_y = min(self.map.height - viewport_height, top_left_y + 1)
                elif key == curses.KEY_LEFT or key == ord('q'):
                    top_left_x = max(0, top_left_x - 1)
                elif key == curses.KEY_RIGHT or key == ord('d'):
                    top_left_x = min(self.map.width - viewport_width, top_left_x + 1)
                elif key == curses.KEY_F12 and USE_PYGAME != False:  # Switch to GUI mode
                    gui.run_gui_mode(self)
                    continue  # Skip the rest of the loop to reinitialize game engine state
                elif key == ord('h'):  # When 'h' is pressed, test for the functions
                    #for unit in self.players[2].units:             #Takes time to calculates all paths but is perfectly smooth after that
                        #action.move_unit(unit, 50, 60, current_time)
                    action.move_unit(self.players[2].units[0], 2, 2, current_time) # Move the first unit to (0, 0)
                elif key == ord('g'):  # When 'g' is pressed, test for the functions
                    Unit.kill_unit(self.players[2], self.players[2].units[1], self.map)
                elif key == ord('\t'):  # TAB key
                    generate_html_report(self.players)
                    self.debug_print(f"HTML report generated at turn {self.turn}")
                    if self.is_paused == False:
                        self.is_paused = True
                        self.debug_print("Game paused.")
                elif key == ord('j'):
                    Building.spawn_building(self.players[2], 1, 1, Farm, self.map)
                elif key == ord('k'):
                    action.gather_resources(self.players[2].units[2], "Gold", current_time)
                elif key == ord('o'):
                    self.debug_print(self.map.grid[0][0].resource.amount)
                    self.debug_print(f"Map has {len([tile for row in self.map.grid for tile in row if tile.resource and tile.resource.type == 'Gold'])} gold tiles")
                elif key == ord('l'):
                    self.debug_print(self.map.grid[1][0].resource.amount)
                    self.debug_print(f"Map has {len([tile for row in self.map.grid for tile in row if tile.resource and tile.resource.type == 'Gold'])} gold tiles")
                elif key == ord('m'):
                    self.debug_print(self.map.grid[1][1].resource.amount)
                    self.debug_print(f"Map has {len([tile for row in self.map.grid for tile in row if tile.resource and tile.resource.type == 'Gold'])} gold tiles")
                elif key == ord('r'):
                    self.debug_print("Testing new PowerShell window for debug output.")
                elif key == ord('a'):
                    action.go_battle(self.players[2].units[0], self.players[1].units[1], current_time)
                elif key == ord('b'):
                    action.go_battle(self.players[1].units[1], self.players[2].units[0], current_time)
                elif key == ord('e'):
                    action.move_unit(self.players[1].units[1],2,2, current_time)
                elif key == ord('f'):
                    Building.kill_building(self.players[2], self.players[2].buildings[-1], self.map)
                elif key == ord('p'):
                    self.is_paused = not self.is_paused
                    if self.is_paused:
                        self.debug_print("Game paused.")
                    else:
                        self.debug_print("Game resumed.")
                elif key == ord('c'):
                    Unit.train_unit(Swordsman, 2, 2, self.players[2], self.map, current_time) #coordinates should be next to the right building
                elif key == ord('u'):
                    self.players[2].owned_resources["Food"] -= 19950
                elif key == ord('v'):  
                    self.save_game("../assets/annex/game_save.dat")
                elif key == ord('x'):  
                    self.load_game("../assets/annex/game_save.dat")
                

                if not self.is_paused:
                    # Move units toward their target position
                    for player in self.players:
                        for unit in player.units:
                            if unit.target_position:
                                target_x, target_y = unit.target_position
                                action.move_unit(unit, target_x, target_y, current_time)
                            if unit.task == "gathering" or unit.task == "returning":
                                action._gather(unit, unit.last_gathered, current_time)
                            if unit.task == "marching":
                                action.gather_resources(unit, unit.last_gathered, current_time)
                            if unit.task == "attacking":
                                action._attack(unit, unit.target_attack, current_time)
                            if unit.task == "going_to_battle":
                                action.go_battle(unit, unit.target_attack, current_time)
                            if unit.task == "is_attacked":
                                action._attack(unit, unit.is_attacked_by, current_time)
                        if player.training_queue != []:
                            unit = player.training_queue[0]
                            Unit.train_unit(unit, 2, 2, player, self.map, current_time)
                

                # Clear the screen and display the new part of the map after moving
                stdscr.clear()
                self.map.display_viewport(stdscr, top_left_x, top_left_y, viewport_width, viewport_height, Map_is_paused=self.is_paused)
                stdscr.refresh()

                self.turn += 1

        except KeyboardInterrupt:
            self.debug_print("Game interrupted. Exiting...")

    def check_victory(self):
        active_players = [p for p in self.players if p.has_units()]
        return len(active_players) == 1 # Check if there is only one player left

    def pause_game(self):
        self.is_paused = not self.is_paused

    def save_game(self, filename):
        if self.is_paused == False:
            self.is_paused = True
            self.debug_print("Game paused.")
        """
        Saves the current game state to a file using pickle.
        """
        try:
            with open(filename, 'wb') as f:
                game_state = {
                    'players': self.players,
                    'map': self.map,
                    'turn': self.turn,
                    'is_paused': self.is_paused,
                    'changed_tiles': self.changed_tiles,
                }
                pickle.dump(game_state, f)
            self.debug_print(f"Game saved to {filename}.")
        except Exception as e:
            self.debug_print(f"Error saving game: {e}")

    def load_game(self, filename):
        if self.is_paused == False:
            self.is_paused = True
            self.debug_print("Game paused.")
        """
        Loads a saved game state from a file.
        """
        try:
            with open(filename, 'rb') as f:
                game_state = pickle.load(f)
                self.players = game_state['players']
                self.map = game_state['map']
                self.turn = game_state['turn']
                self.is_paused = game_state['is_paused']
                self.changed_tiles = game_state['changed_tiles']
            self.debug_print(f"Game loaded from {filename}.")
        except Exception as e:
            self.debug_print(f"Error loading game: {e}")
