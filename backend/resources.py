
STARTING_RESOURCES = [200, 50, 50]  # [Wood, Gold, Food]
STARTING_RESOURCES_AI = [200, 50, 50]

class Resource:
    def __init__(self):
        self.starting_resources = {
            "Wood": STARTING_RESOURCES[0],
            "Gold": STARTING_RESOURCES[1],
            "Food": STARTING_RESOURCES[2]
        }
        self.starting_resources_AI = {
            "Wood": STARTING_RESOURCES_AI[0],
            "Gold": STARTING_RESOURCES_AI[1],
            "Food": STARTING_RESOURCES_AI[2]
        }
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

    def is_affordable(self, entity, team="Blue"):
        current_resources = self.starting_resources if team == "Blue" else self.starting_resources_AI
        for resource, cost in self.costs[entity].items():
            if current_resources[resource] < cost:
                return False
        return True

    def buy(self, entity, team="Blue"):
        if self.is_affordable(entity, team):
            if team == "Blue":
                for resource, cost in self.costs[entity].items():
                    self.starting_resources[resource] -= cost
            elif team == "Red":
                for resource, cost in self.costs[entity].items():
                    self.starting_resources_AI[resource] -= cost
            return True
        return False
