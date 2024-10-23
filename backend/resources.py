
starting_resources = {
    "Means": {"Wood": 200, "Food": 50, "Gold": 50},
    "Leans": {"Wood": 2000, "Food": 2000, "Gold": 2000},
    "Marines": {"Wood": 20000, "Food": 20000, "Gold": 20000},
}

class Resource:
    def __init__(self, player):
        self.starting_resources = starting_resources.get(player.civilization, {})
        player.owned_resources = self.starting_resources.copy()
        self.costs = {
            "Villager": {"Wood": 0, "Gold": 0, "Food": 50},
            "Swordsman": {"Wood": 0, "Gold": 20, "Food": 50},
            "Horseman": {"Wood": 0, "Gold": 20, "Food": 80},
            "Archer": {"Wood": 25, "Gold": 45, "Food": 0},
            "TownCenter": {"Wood": 350, "Gold": 0, "Food": 0},
            "House": {"Wood": 25, "Gold": 0, "Food": 0},
            "Camp": {"Wood": 100, "Gold": 0, "Food": 0},
            "Farm": {"Wood": 60, "Gold": 0, "Food": 0},
            "Barracks": {"Wood": 175, "Gold": 0, "Food": 0},
            "Stable": {"Wood": 175, "Gold": 0, "Food": 0},
            "Archery": {"Wood": 175, "Gold": 0, "Food": 0},
            "Keep": {"Wood": 35, "Gold": 125, "Food": 0}
        }

    def is_affordable(self, entity, player):
        for resource, cost in self.costs[entity].items():
            if player.owned_resources[resource] < cost:
                return False
        return True

    def buy(self, entity, player):
        if self.is_affordable(entity, player):
            for resource, cost in self.costs[entity].items():
                player.owned_resources[resource] -= cost
            return True
        return False
