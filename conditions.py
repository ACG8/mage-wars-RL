#This file contains the code for conditions that may be applied to objects in the game.

class Condition:
    def __init__(self, name, removal_cost, damage_type, description):
        self.name = name
        self.removal_cost = removal_cost
        self.damage_type = damage_type
        self.description = description
        #also should have an upkeep function

    #Function that returns True if the target is not immune to the damage type of this condition.

    def is_targetable(self, creature):
        for trait in creature.traits:
            if #trait is 'immunity to *damage type*:
                return False
        return True
