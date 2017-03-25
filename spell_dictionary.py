import spell_classes as spcl
import attack_dictionary as adic
import spell_functions as spfn
import definitions as defn
import gui

def attack_spell(parameters, source=None, target=None):
    if source==None:
        source=defn.player
        arg = adic.attk_dict[parameters['attack']]
        if arg['target type']=='zone':
            spfn.target_tile(arg['name'])
            #placeholder for zone spells
        elif arg['target type']=='none':
            pass
            #placeholder for untargetable spells, e.g. ring of fire
        elif arg['target type']=='creature':
            #find target. currently geared to ranged attacks, though can easily be extended to melee
            target=spfn.target_monster(arg['range'][1])
            if target:
            #use attack against target.
                attack = adic.Attack(arg['name'], arg['attack dice'], arg['traits'], arg['effects'])
                attack.target_creature(source, target)
            else:
                return 'cancelled'

class Spell:
    def __init__(self, name, base_cost, function, parameters):
        self.name = name
        self.base_cost = base_cost
        self.cost = 3 * base_cost
        #function indicates the general function to call. Parameters returns a dictionary used to define the parameters of the function.
        self.function = function
        self.parameters = parameters

    def cast(self, source):
        if self.function is None:
            gui.message('The ' + self.owner.name + ' cannot be used.')
            return 'cancelled'
        else:
            #use function must always have an argument of the name
            if source.creature.mana >= self.cost:
                if self.function(self.parameters) != 'cancelled':
                    source.creature.spend_mana(self.cost)
                else:
                    return 'cancelled'
            else:
                return 'cancelled'

    #reduce the price of the spell as you become more familiar with it
    def learn(self, amount):
        if self.cost > self.base_cost + amount:
            self.cost -= amount
        else:
            self.cost = self.base_cost

#a list of spells, their associated levels, their base costs, their associated use functions, and their descriptions.

spell_dict = {}

#attack spells

spell_dict['lightning bolt'] = {
    'name' : 'lightning bolt',
    'level' : 2,
    'base cost' : 8,
    'type' : 'lightning',
    'function' : attack_spell,
    'parameters' : {
        'attack' : 'lightning bolt'},
    'description' :'blah,blah'}
