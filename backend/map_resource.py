import pygame as pg

class MapResource:
    def __init__(self, resource_type, amount):
        self.resource_type = resource_type
        self.the_rest = amount
        self.resource_cooldown = pg.time.get_ticks()
        self.available = True

    def mine(self, player):
        if self.the_rest > 0 and self.available:
            now = pg.time.get_ticks()
            if now - self.resource_cooldown > 2000:  #2 secondes entre chaque collecte
                self.the_rest -= 1
                self.resource_cooldown = now
                
                # Ajouter des ressources à l'equipe
                player.owned_resources[self.resource_type] += 1
            
                # Verifiez si les ressources sont epuisees
                if self.the_rest <= 0:
                    self.available = False
                return 1
        else:
            self.available = False  # Les ressource sont epuisees
            return 0

class Map_Tree(MapResource):
    def __init__(self):
        super().__init__("Wood", 100)

class Map_Gold(MapResource):
    def __init__(self):
        super().__init__("Gold", 800)

class Map_Farm(MapResource):
    def __init__(self):
        super().__init__("Food", 300)

    def gather_food(self,  player):
        return self.mine(player) 
