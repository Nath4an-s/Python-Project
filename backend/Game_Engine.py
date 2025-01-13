import curses
import time
import pickle
import os

from queue import Queue
from frontend.gui import GUI

from pynput.keyboard import Key, Listener
from logger import debug_print
from Units import *
from Building import *
from Actions import *
from frontend.Terrain import Map
try:
    from frontend import gui
    USE_PYGAME = True
except ImportError:
    USE_PYGAME = False
    debug_print("Pygame not installed; running without Pygame features such as 2.5D map view.")

from html_report import generate_html_report

from IA import IA

#Partie Gestion de Touche en Simultanée

allowedKeys = [
    Key.up,
    Key.down,
    Key.left,
    Key.right
]

key_buffer = []

def press(key):
    global key_buffer
    if key in allowedKeys and key not in key_buffer and len(key_buffer) < 3:
        key_buffer.append(key)

def release(key):
    global key_buffer
    if key in key_buffer:
        key_buffer.remove(key)

def check_diagonal_movement():
    up = Key.up in key_buffer
    down = Key.down in key_buffer
    left = Key.left in key_buffer
    right = Key.right in key_buffer
    
    if up and left:
        return -1, -1
    elif up and right:
        return 1, -1
    elif down and left:
        return -1, 1
    elif down and right:
        return 1, 1
    return 0, 0


# GameEngine Class
class GameEngine:
    def __init__(self, players, map_size=(120, 120),sauvegarde=False):
        self.players = players  # List of Player objects
        self.map = Map(*map_size)  # Create a map object
        self.turn = 0
        self.is_paused = False  # Flag to track if the game is paused
        self.changed_tiles = set()  # Set to track changed tiles
        if not sauvegarde :
            Building.place_starting_buildings(self.map)   # Place starting town centers on the map
        if not sauvegarde : 
            Unit.place_starting_units(self.players, self.map)  # Place starting units on the map
        self.debug_print = debug_print
        self.ias = [IA(player, player.ai_profile, self.map, time.time()) for player in self.players]  # Instantiate IA for each player
        #self.ias = [IA(players[0], players[0].ai_profile, self.map, time.time())]
        self.IA_used = False
        self.current_time = time.time()

        # GUI thread related attributes
        self.gui_running = False
        self.data_queue = Queue()
        self.gui_thread = None

    def start_gui_thread(self):
        """Initialize and start the GUI thread"""
        if not self.gui_thread:
            self.data_queue = Queue()
            self.gui_thread = GUI(self.data_queue)
            self.gui_thread.start()
            self.gui_running = True

    def stop_gui_thread(self):
        """Stop the GUI thread safely"""
        if self.gui_thread:
            #self.gui_thread.stop()
            self.gui_thread = None
            self.gui_running = False

    def update_gui(self):
        """Send current game state to GUI thread"""
        if self.gui_running and not self.data_queue.full():
            self.data_queue.put(self)

    def get_current_time(self):
        """Retourne le temps actuel si le jeu n'est pas en pause"""
        if not self.is_paused:
            return time.time()
        return self.current_time

    def run(self, stdscr):
        # Initialize the starting view position
        top_left_x, top_left_y = 0, 0
        viewport_width, viewport_height = 30, 30
        # Display the initial viewport
        stdscr.clear()  # Clear the screen
        self.map.display_viewport(stdscr, top_left_x, top_left_y, viewport_width, viewport_height, Map_is_paused=self.is_paused)  # Display the initial viewport
        
        #Thread pour la gestion de touche
        listener = Listener(on_press=press, on_release=release)
        listener.start()

        try:
            while not self.check_victory():
                # Mettre à jour current_time au début de chaque itération si le jeu n'est pas en pause
                if not self.is_paused:
                    self.current_time = time.time()

                # Handle input
                curses.curs_set(0)  # Hide cursor
                stdscr.nodelay(True)  # Make getch() non-blocking
                key = stdscr.getch()  # Get the key pressed by the user
                action = Action(self.map)

                dx, dy = check_diagonal_movement()

                if dx == 0 and dy == 0:
                    if key == curses.KEY_UP or key == ord('z'):
                        top_left_y = max(0, top_left_y - 1)
                    elif key == curses.KEY_DOWN or key == ord('s'):
                        top_left_y = min(self.map.height - viewport_height, top_left_y + 1)
                    elif key == curses.KEY_LEFT or key == ord('q'):
                        top_left_x = max(0, top_left_x - 1)
                    elif key == curses.KEY_RIGHT or key == ord('d'):
                        top_left_x = min(self.map.width - viewport_width, top_left_x + 1)
                    elif key == ord('Z'):
                        top_left_y = max(0, top_left_y - 5)
                    elif key == ord('S'):
                        top_left_y = min(self.map.height - viewport_height, top_left_y + 5)
                    elif key == ord('Q'):
                        top_left_x = max(0, top_left_x - 5)
                    elif key == ord('D'):   
                        top_left_x = min(self.map.width - viewport_width, top_left_x + 5)
                    
                else :
                    # Apply diagonal movement
                    top_left_x = max(0, min(self.map.width - viewport_width, top_left_x + dx))
                    top_left_y = max(0, min(self.map.height - viewport_height, top_left_y + dy))
                
                if key == curses.KEY_F12:
                    if not self.gui_running:
                        self.start_gui_thread()
                    else:
                        self.stop_gui_thread()
                        stdscr.clear()
                        stdscr.refresh()
                        continue
                elif key == ord('h'):  # When 'h' is pressed, test for the functions
                    #for unit in self.players[2].units:             #Takes time to calculates all paths but is perfectly smooth after that
                        #action.move_unit(unit, 50, 60, current_time)
                    action.move_unit(self.players[2].units[0], 2, 2, self.get_current_time()) # Move the first unit to (0, 0)
                elif key == ord('g'):  # When 'g' is pressed, test for the functions
                    Unit.kill_unit(self.players[2], self.players[2].units[0], self.map)
                elif key == ord('b'):  # When 'b' is pressed, test for the functions
                    Building.spawn_building(self.players[2], 4, 4, House, self.map)
                    Building.spawn_building(self.players[2], 6, 6, House, self.map)
                    Unit.spawn_unit(Swordsman, 2, 2, self.players[2], self.map)
                    
                    Unit.spawn_unit(Swordsman, 2, 2, self.players[2], self.map)

                    Unit.spawn_unit(Swordsman, 2, 2, self.players[2], self.map)

                    Unit.spawn_unit(Swordsman, 2, 2, self.players[2], self.map)

                    Unit.spawn_unit(Swordsman, 2, 2, self.players[2], self.map)

                    Unit.spawn_unit(Swordsman, 2, 2, self.players[2], self.map)

                    Unit.spawn_unit(Swordsman, 2, 2, self.players[2], self.map)

                    Unit.spawn_unit(Swordsman, 2, 2, self.players[2], self.map)


                elif key == ord('\t'):  # TAB key
                    generate_html_report(self.players)
                    self.debug_print(f"HTML report generated at turn {self.turn}")
                    if self.is_paused == False:
                        self.is_paused = True
                        self.debug_print("Game paused.")
                elif key == ord('j'):
                    action.construct_building(self.players[2].units[2], Farm, 10, 10, self.players[2], self.get_current_time())
                    #action.construct_building(self.players[2].units[1], Farm, 10, 10, self.players[2], current_time)
                    #action.construct_building(self.players[2].units[3], Barracks, 1, 1, self.players[2], current_time)
                    #action.construct_building(self.players[2].units[4], Barracks, 1, 1, self.players[2], current_time)
                elif key == ord('t'):
                    action.move_unit(self.players[2].units[0], 4, 8, self.get_current_time())
                    action.move_unit(self.players[2].units[2], 3, 6, self.get_current_time())
                    action.construct_building(self.players[2].units[1], TownCenter, 4, 4, self.players[2], self.get_current_time())
                elif key == ord('k'):
                    action.gather_resources(self.players[2].units[1], "Food", self.get_current_time())
                    action.gather_resources(self.players[2].units[2], "Wood", self.get_current_time())
                    action.gather_resources(self.players[2].units[3], "Gold", self.get_current_time())
                elif key == ord('o'):
                    self.debug_print(self.map.grid[0][0].resource.amount)
                elif key == ord('l'):
                    if self.map.grid[1][0].resource is not None:
                        self.debug_print(self.map.grid[1][0].resource.amount)
                    else:
                        self.debug_print("No resource at this location")
                elif key == ord('m'):
                    self.debug_print(self.map.grid[1][1].resource.amount)
                elif key == ord('r'):
                    for ia in self.ias:
                        self.debug_print(self.players)
                        self.debug_print(self.players)
                elif key == ord('a'):
                    action.go_battle(self.players[2].units[0], self.players[1].units[1], self.get_current_time())
                elif key == ord('b'):
                    action.go_battle(self.players[1].units[1], self.players[2].units[0], self.get_current_time())
                elif key == ord('e'):
                    action.move_unit(self.players[1].units[1],2,2, self.get_current_time())
                elif key == ord('f'):
                    Building.kill_building(self.players[2], self.players[2].buildings[-1], self.map)
                elif key == ord('y'):
                    Building.spawn_building(self.players[0], 60, 60, Barracks, self.map)
                    Building.spawn_building(self.players[0], 63, 63, House, self.map)
                    Unit.spawn_unit(Swordsman, 59, 59, self.players[0], self.map)
                    Unit.spawn_unit(Swordsman, 59, 59, self.players[0], self.map)
                    Unit.spawn_unit(Swordsman, 59, 59, self.players[0], self.map)
                    Unit.spawn_unit(Swordsman, 59, 59, self.players[0], self.map)
                    Unit.spawn_unit(Swordsman, 59, 59, self.players[0], self.map)
                    self.players[0].owned_resources["Food"] = 1000
                    self.players[0].owned_resources["Wood"] = 1000
                    self.players[0].owned_resources["Gold"] = 1000
                elif key == ord('p'):
                    self.is_paused = not self.is_paused
                    if self.is_paused:
                        self.debug_print("Game paused.")
                    else:
                        self.debug_print("Game resumed.")
                elif key == ord('c'):
                    Unit.train_unit(Villager, 2, 2, self.players[2], self.players[2].buildings[0], self.map, self.get_current_time()) #TODO:coordinates should be next to the right building (hardcoded)
                    Unit.train_unit(Villager, 3, 2, self.players[2], self.players[2].buildings[0], self.map, self.get_current_time()) #same building so after first one
                    Unit.train_unit(Swordsman, 2, 3, self.players[2], self.players[2].buildings[1], self.map, self.get_current_time()) #other buidling so same time as first one
                elif key == ord('u'):
                    self.players[2].owned_resources["Food"] -= 19950
                elif key == ord('v'):  
                    self.save_game()
                elif key == ord('i'):
                    for unit in self.players[2].units:
                        action.go_battle(unit, self.players[1].units[1], self.get_current_time())
                elif key == ord('n'):
                    self.IA_used = not self.IA_used
                    self.debug_print(f"IA used: {self.IA_used}")
                elif key == ord('x'): #Attaquer un batiment
                    for unit in self.players[2].units:
                        action.go_battle(unit, self.players[1].buildings[-1], self.get_current_time())
                #call the IA
                if not self.is_paused and self.turn % 10 == 0 and self.IA_used == True: # Call the IA every 5 turns: change 0, 5, 10, 15, ... depending on lag
                    for ia in self.ias:
                        ia.current_time_called = self.get_current_time()  # Update the current time for each IA
                        ia.run()  # Run the AI logic for each player
                    
                if not self.is_paused:
                    # Move units toward their target position
                    for player in self.players:
                        for unit in player.units:
                            if unit.target_position:
                                target_x, target_y = unit.target_position
                                action.move_unit(unit, target_x, target_y, self.get_current_time())
                            if unit.task == "gathering" or unit.task == "returning":
                                action._gather(unit, unit.last_gathered, self.get_current_time())
                            if unit.task == "marching":
                                action.gather_resources(unit, unit.last_gathered, self.get_current_time())
                            if unit.task == "attacking":
                                action._attack(unit, unit.target_attack, self.get_current_time())
                            if unit.task == "going_to_battle":
                                action.go_battle(unit, unit.target_attack, self.get_current_time())
                            if unit.task == "is_attacked":
                                action._attack(unit, unit.is_attacked_by, self.get_current_time())
                            if unit.task == "going_to_construction_site":
                                action.construct_building(unit, unit.construction_type, unit.target_building[0], unit.target_building[1], player, self.get_current_time())
                            if unit.task == "constructing":
                                action._construct(unit, unit.construction_type, unit.target_building[0], unit.target_building[1], player, self.get_current_time())
                        for building in player.buildings:
                            if hasattr(building, 'training_queue') and building.training_queue != []:
                                unit = building.training_queue[0]
                                Unit.train_unit(unit, unit.spawn_position[0], unit.spawn_position[1], player, unit.spawn_building, self.map, self.get_current_time())

                # Clear the screen and display the new part of the map after moving
                stdscr.clear()
                self.map.display_viewport(stdscr, top_left_x, top_left_y, viewport_width, viewport_height, Map_is_paused=self.is_paused)
                stdscr.refresh()

                if self.gui_running:
                    self.update_gui()
                else:
                    # Clear the screen and display the new part of the map after moving
                    stdscr.clear()
                    self.map.display_viewport(stdscr, top_left_x, top_left_y, viewport_width, viewport_height, Map_is_paused=self.is_paused)
                    stdscr.refresh()

                self.turn += 1

            active_players = [p for p in self.players if p.units or p.buildings]
            self.debug_print(f"Player {active_players[0].name} wins the game!")
            input("Press Enter to exit...")

        except KeyboardInterrupt:
            self.debug_print("Game interrupted. Exiting...")
        finally:
            if self.gui_running:
                self.stop_gui_thread()

    def check_victory(self):
        active_players = [p for p in self.players if p.units or p.buildings] # Check if the player has units and buildings
        return len(active_players) == 1 # Check if there is only one player left

    def pause_game(self):
        self.is_paused = not self.is_paused

    def save_game(self, filename=None):
        if not self.is_paused:
            self.is_paused = True
            self.debug_print("Game paused.")
        
        # Générer un nom de fichier si aucun n'est fourni
        if filename is None:
            for i in range(10):  # Limite à 10 sauvegardes automatiques
                filename = f"../assets/annex/game_save{i}.dat"
                if not os.path.exists(filename):  # Vérifie si le fichier existe
                    break
            else:
                self.debug_print("No available slots to save the game.")
                return
        else:
            # Si un nom est fourni, ajoute un suffixe unique si nécessaire
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(filename):
                filename = f"{base}_{counter}{ext}"
                counter += 1

        # Sauvegarde de l'état du jeu
        try:
            with open(filename, 'wb') as f:
                game_state = {
                    'players': self.players,
                    'map': self.map,
                    'turn': self.turn,
                    'is_paused': self.is_paused,
                    'changed_tiles': self.changed_tiles
                }
                pickle.dump(game_state, f)
            self.debug_print(f"Game saved to {filename}.")
        except Exception as e:
            self.debug_print(f"Error saving game: {e}")


    def load_game(self, filename):
        if self.is_paused == False:
            self.is_paused = True
            self.debug_print("Game paused.")
        try:
            with open(filename, 'rb') as f:
                game_state = pickle.load(f)
                self.players = game_state['players']
                self.map = game_state['map']
                self.turn = game_state['turn']
                self.is_paused = game_state['is_paused']
                self.changed_tiles = game_state['changed_tiles']
                self.current_time = time.time()
            self.debug_print(f"Game loaded from {filename}.")
        except Exception as e:
            self.debug_print(f"Error loading game: {e}")