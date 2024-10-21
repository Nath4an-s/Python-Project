import pygame as pg

class MapResource:
    def __init__(self, resource_manager, resource_type, amount):
        self.resource_manager = resource_manager
        self.resource_type = resource_type
        self.the_rest = amount
        self.resource_cooldown = pg.time.get_ticks()
        self.available = True

    def mine(self, team=""):
        if self.the_rest > 0 and self.available:
            now = pg.time.get_ticks()
            if now - self.resource_cooldown > 2000:  #2 secondes entre chaque collecte
                self.the_rest -= 1
                self.resource_cooldown = now

                # Ajouter des ressources à l'equipe
                if team == "Blue":
                    self.resource_manager.starting_resources[self.resource_type] += 1
                elif team == "Red":
                    self.resource_manager.starting_resources_AI[self.resource_type] += 1
                
                # Verifiez si les ressources sont epuisees
                if self.the_rest <= 0:
                    self.available = False
                return 1
        else:
            self.available = False  # Les ressource sont epuisees
            return 0

class Map_Tree(MapResource):
    def __init__(self, resource_manager):
        super().__init__(resource_manager, "Wood", 100)

class Map_Gold(MapResource):
    def __init__(self, resource_manager):
        super().__init__(resource_manager, "Gold", 800)

class Map_Farm(MapResource):
    def __init__(self, resource_manager):
        super().__init__(resource_manager, "Food", 300)

    def gather_food(self, team=""):
        return self.mine(team) 
