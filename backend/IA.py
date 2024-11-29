#IA
from Actions import *
from Starter_File import players
from frontend.Terrain import Map
from logger import debug_print

class IA:
    def __init__(self, player, mode, game_map, current_time_called): #only one player --> IA class will be called for each player in GameEngine
        self.player = player
        self.mode = mode
        self.game_map = game_map
        self.debug_print = debug_print
        self.current_time_called = current_time_called

    def run(self):
        #gathering resources plan
        for unit in self.player.units:
            if unit.task == None: #TODO: maybe too much units going gathering there, leave some idle or we'll just pick them in the gathering ones
                if self.player.owned_resources[0] < self.player.owned_resources[1] < self.player.owned_resources[2]:
                    resource_type = self.player.owned_resources[0]
                elif self.player.owned_resources[1] < self.player.owned_resources[0] < self.player.owned_resources[2]:
                    resource_type = self.player.owned_resources[1]
                else:
                    resource_type = self.player.owned_resources[2]
                Action(self.game_map).gather_resources(unit, resource_type, self.current_time_called)

        #building plan

        #attacking plan