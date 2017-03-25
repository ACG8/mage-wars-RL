import spell_classes as spcl
import action_classes as accl
import attack_dictionary as adic
import spell_functions as spfn
import definitions as defn
import gui

class Spell:
    def __init__(self, name, base_cost, use_function):
        self.name = name
        self.base_cost = base_cost
        self.cost = 3 * base_cost
        self.use_function = use_function

    def attack_spell(self, source, target):
        attack_trait = adic.attk_dict[self.name]
        attack = accl.Attack(attack_trait[0], attack_trait[1], attack_trait[2], attack_trait[3])
        attack.target_creature(source, target)

    def cast(self, source):
        if self.use_function is None:
            gui.message('The ' + self.owner.name + ' cannot be used.')
        else:
            #use function must always have an argument of the name
            if source.creature.mana >= self.cost:
                if self.use_function(self.name) != 'cancelled':
                    source.creature.spend_mana(self.cost)

    #reduce the price of the spell as you become more familiar with it
    def learn(self, amount):
        if self.cost > self.base_cost + amount:
            self.cost -= amount
        else:
            self.cost = self.base_cost

def attack_spell(attack_name, source=None, target=None):
    if source==None:
        source=defn.player
        attack_trait = adic.attk_dict[attack_name]
        if attack_trait[4]=='zone':
            spfn.target_tile(attack_trait[4])
            #placeholder for zone spells
        elif attack_trait[4]=='none':
            pass
            #placeholder for untargetable spells, e.g. ring of fire
        elif attack_trait[4]=='creature':
            #find target
            target=spfn.target_monster(attack_trait[5])
            if target:
            #use attack against target.
                attack = accl.Attack(attack_trait[0], attack_trait[1], attack_trait[2], attack_trait[3])
                attack.target_creature(source, target)
            else:
                return 'cancelled'


#a list of spells, their associated levels, their base costs, their associated use functions, and their descriptions.

spell_dict = {}

#attack spells

spell_dict['lightning bolt'] = {
    'name' : 'lightning bolt',
    'level' : 2,
    'base cost' : 8,
    'type' : 'lightning',
    'use function' : attack_spell,
    'description' :'blah,blah'}
