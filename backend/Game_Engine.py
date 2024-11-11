import curses
import time

from Units import *
from Building import *
from frontend.Terrain import Map
try:
    from frontend import gui
    USE_PYCHARM = True
except ImportError:
    USE_PYCHARM = False
    print("Pycharm not installed; running without Pycharm features such as 2.5D map view.")

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
        Building.place_starting_buildings(self.map)  # Place town centers on the map
        Unit.place_starting_units(self.players, self.map)  # Pass players and map

    def run(self, stdscr):
        # Initialize the starting view position
        top_left_x, top_left_y = 0, 0
        viewport_width, viewport_height = 30, 30

        # Display the initial viewport
        stdscr.clear()  # Clear the screen
        self.map.display_viewport(stdscr, top_left_x, top_left_y, viewport_width, viewport_height)  # Display the initial viewport

        try:
            while not self.check_victory():
                current_time = time.time()

                # Handle input
                stdscr.nodelay(True)  # Make getch() non-blocking
                key = stdscr.getch()  # Get the key pressed by the user
                action = Action(self.map)
                if key == curses.KEY_UP:
                    top_left_y = max(0, top_left_y - 1)
                elif key == curses.KEY_DOWN:
                    top_left_y = min(self.map.height - viewport_height, top_left_y + 1)
                elif key == curses.KEY_LEFT:
                    top_left_x = max(0, top_left_x - 1)
                elif key == curses.KEY_RIGHT:
                    top_left_x = min(self.map.width - viewport_width, top_left_x + 1)
                elif key == curses.KEY_F12 and USE_PYCHARM != False:  # Switch to GUI mode
                    gui.run_gui_mode(self)
                    stdscr = curses.initscr()  # Reinitialize curses screen
                    curses.curs_set(0)  # Hide cursor
                    stdscr.clear()
                    self.map.display_viewport(stdscr, top_left_x, top_left_y, viewport_width, viewport_height)
                    continue  # Skip the rest of the loop to reinitialize game engine state
                elif key == ord('h'):  # When 'h' is pressed, test for the functions
                    #for unit in self.players[2].units:             #Takes time to calculates all paths but is perfectly smooth after that
                        #action.move_unit(unit, 50, 60, current_time)
                    action.move_unit(self.players[2].units[0], 2, 2, current_time) # Move the first unit to (0, 0)
                elif key == ord('g'):  # When 'g' is pressed, test for the functions
                    Unit.kill_unit(self.players[2], self.players[2].units[1], self.map)
                elif key == ord('\t'):  # TAB key
                    generate_html_report(self.players)
                elif key == ord('j'):
                    Building.spawn_building(self.players[2], 1, 1, Barracks, self.map)
                elif key == ord('k'):
                    action.gather_resources(self.players[2].units[2], "Gold", current_time)
                elif key == ord('o'):
                    print(self.map.grid[0][0].resource.amount)
                    print(f"Map has {len([tile for row in self.map.grid for tile in row if tile.resource and tile.resource.type == 'Gold'])} gold tiles")
                elif key == ord('p'):
                    print(self.map.grid[0][1].resource.amount)
                    print(f"Map has {len([tile for row in self.map.grid for tile in row if tile.resource and tile.resource.type == 'Gold'])} gold tiles")
                elif key == ord('l'):
                    print(self.map.grid[1][0].resource.amount)
                    print(f"Map has {len([tile for row in self.map.grid for tile in row if tile.resource and tile.resource.type == 'Gold'])} gold tiles")
                elif key == ord('m'):
                    print(self.map.grid[1][1].resource.amount)
                    print(f"Map has {len([tile for row in self.map.grid for tile in row if tile.resource and tile.resource.type == 'Gold'])} gold tiles")
                elif key == ord('r'):
                    print("Testing new PowerShell window for debug output.")
                elif key == ord('a'):
                    action.go_battle(self.players[2].units[0], self.players[1].units[1], current_time)
                elif key == ord('e'):
                    action.move_unit(self.players[1].units[1], self.players[1].units[1].position[0] - 1, self.players[1].units[1].position[1] - 1, current_time)
                


                # Move units toward their target position
                action = Action(self.map)
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

                # Clear the screen and display the new part of the map after moving
                stdscr.clear()
                self.map.display_viewport(stdscr, top_left_x, top_left_y, viewport_width, viewport_height)
                stdscr.refresh()

                self.turn += 1

        except KeyboardInterrupt:
            print("Game interrupted. Exiting...")

    def check_victory(self):
        active_players = [p for p in self.players if p.has_units()]
        return len(active_players) == 1 and self.is_paused

    def pause_game(self):
        self.is_paused = not self.is_paused

    def save_game(self, filename):
        game_state = GameState(self)
        game_state.save(filename)

    def load_game(self, filename):
        game_state = GameState(self)
        game_state.load(filename)

# GameState Class
class GameState:
    def __init__(self, game_engine):
        self.game_engine = game_engine

    def save(self, filename):
        pass

    def load(self, filename):
        pass
