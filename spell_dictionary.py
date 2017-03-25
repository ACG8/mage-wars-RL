import spell_classes as spcl
import attack_dictionary as adic
import spell_functions as spfn
import definitions as defn
import gui
import libtcodpy as libtcod

def pushing_spell(parameters, source=None, target=None):
    if source==None:
        source=defn.player
        if parameters['target type']=='zone':
            spfn.target_tile(arg['name'])
            #placeholder for zone spells
        elif parameters['target type']=='none':
            pass
            #placeholder for untargetable spells, e.g. ring of fire
        elif parameters['target type']=='creature':
            #find target. currently geared to ranged attacks, though can easily be extended to melee
            target=spfn.target_monster(parameters['range'])
            if target:
                if parameters['direction'] == 'inward':
                    for i in range(parameters['distance']):
                        #I can add wall bash effects by giving the move_towards function an output of 'failed' if it fails, and breaking the loop then with an attack.
                        #clear the object from the console so it doesn't leave a preimage.
                        target.clear()
                        target.move_towards(source.x,source.y)
                    #add parameters for other directions. also, alter so that other sorts of objects can be pulled.
            else:
                return 'cancelled'

def healing_spell(parameters, source=None, target=None):
    if source==None:
        source=defn.player
        if parameters['target type']=='zone':
            spfn.target_tile(arg['name'])
            #placeholder for zone spells
        elif parameters['target type']=='none':
            pass
            #placeholder for untargetable spells, e.g. ring of fire
        elif parameters['target type']=='creature':
            #find target. currently geared to ranged attacks, though can easily be extended to melee
            target=spfn.target_monster(parameters['range'])
            if target:
                if parameters['amount healed']:
                    target.creature.heal(parameters['amount healed'])
                #if parameters['conditions removed']:
                    #condition removal function here
            else:
                return 'cancelled'
        

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
                attack = adic.Attack(arg['name'], arg['attack dice'], arg['range'], arg['traits'], arg['effects'])
                attack.declare_attack(source, target)
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
            gui.message('The ' + self.name + ' cannot be used.')
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

def get_spell(name):
    arg = spell_dict[name]
    spell = Spell(arg['name'], arg['base cost'], arg['function'], arg['parameters'])
    return spell

spell_dict = {}

#attack spells

spell_dict['lightning bolt'] = {
    'name' : 'lightning bolt',
    'level' : [['air', 2]],
    'base cost' : 8,
    'type' : ['lightning'],
    'function' : attack_spell,
    'parameters' : {
        'attack' : 'lightning bolt'},
    'description' :'blah,blah'}

spell_dict['minor heal'] = {
    'name' : 'minor heal',
    'level' : [['holy' ,1]],
    'base cost' : 5,
    'type' : ['healing'],
    'function' : healing_spell,
    'parameters' : {
        'range' : 5,
        'target type' : 'creature',
        'amount healed' : sum([libtcod.random_get_int(0,0,2) for i in range(5)]),
        'conditions removed' : None},
    'description' : '\"No scratch is insignificant to the Goddess\"\n -On Health and Blessings True'}

spell_dict['force pull'] = {
    'name' : 'force pull',
    'level' : [['mind', 1]],
    'base cost' : 1,
    'type' : ['force'],
    'function' : pushing_spell,
    'parameters' : {
        'range' : 8,
        'target type' : 'creature',
        'direction' : 'inward',
        'distance' : 3},
    'description' : '\"Come a little closer...\"'}

spell_dict['heal'] = {
    'name' : 'heal',
    'level' : [['holy', 2]],
    'base cost' : 9,
    'type' : ['healing'],
    'function' : healing_spell,
    'parameters' : {
        'range' : 5,
        'target type' : 'creature',
        'amount healed' : sum([libtcod.random_get_int(0,0,2) for i in range(8)]),
        'conditions removed' : None},
    'description' : 'blah blah'}
