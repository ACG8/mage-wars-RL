

#This contains everything pertaining to enchantments.

###FUNCTIONS###

class Enchantment:
    def __init__(self, name, function, parameters, trait_bonus):
        self.name = name
        self.function = function
        self.parameters = parameters
        self.trait_bonus = trait_bonus

def get_enchantment(dictionary):
    enchantment = Enchantment(
        dictionary['name'],
        dictionary['function'],
        dictionary['parameters'],
        dictionary['trait bonus'])

    return enchantment
