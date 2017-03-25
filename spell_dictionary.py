import spell_classes as spcl
import attack_dictionary as adic
import spell_functions as spfn
import definitions as defn
import gui
import libtcodpy as libtcod
import map_functions as mpfn
import time
import game

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
    attack = adic.Attack(
                    parameters['name'],
                    parameters['attack dice'],
                    parameters['range'],
                    parameters['traits'],
                    parameters['effects'],
                    parameters['speed'])
    if source==None:
        source=defn.player
        if parameters['target type']=='zone':
            target_list = []
            (x,y) = spfn.target_location(parameters['range']['distance'])
            for obj in defn.objects:
                if obj.creature and obj.distance(x,y) <= 3:
                    target_list.append(obj)
            for target in target_list:
                attack.declare_attack(source, target, 0, 0)

        elif parameters['target type']=='circle':
            #attack everything within range
            target_list = []
            for obj in defn.objects:
                #AOE is hardcoded at 3, to simulate a zone.
                if obj.creature and not obj == source and source.distance_to(obj) <= 3:
                    target_list.append(obj)
            for target in target_list:
                attack.declare_attack(source, target, 0, 0)

        elif parameters['target type']=='creature':
            #find target. currently geared to ranged attacks, though can easily be extended to melee
            target=spfn.target_monster(parameters['range']['distance'])
            if target:
            #use attack against target.

                
            #in future, will add ability to boost attack. Also, rather than generating an attack, the spell should explicitly have the attack instance when created.
                attack.declare_attack(source, target, 0, 0)
            else:
                return 'cancelled'

class Spell:
    def __init__(self, name, base_cost, function, parameters, properties):
        self.name = name
        self.base_cost = base_cost
        #function indicates the general function to call. Parameters returns a dictionary used to define the parameters of the function.
        self.function = function
        self.parameters = parameters
        self.properties = properties

    @property
    def cost(self):
        #placeholder for when costs can be changed
        return self.base_cost

    def cast(self, source):
        if self.function is None:
            gui.message('The ' + self.name + ' cannot be used.')
            return 'cancelled'
        else:
            if self.function(self.parameters) == 'cancelled':
                return 'cancelled'
            else:
                return 'successful'

    #reduce the price of the spell as you become more familiar with it
    def learn(self, amount):
        if self.cost > self.base_cost + amount:
            self.cost -= amount
        else:
            self.cost = self.base_cost

#a list of spells, their associated levels, their base costs, their associated use functions, and their descriptions.

def get_spell(dictionary):
    spell = Spell(
        dictionary['name'],
        dictionary['base cost'],
        dictionary['function'],
        dictionary['parameters'],
        dictionary['properties'])
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
        
        'name' : 'lightning bolt',
        'attack dice' : 5,
        'traits' : [['lightning'],['ethereal']],
        'effects' : [[['daze'],6],[['stun'],8]],
        'target type' : 'creature',
        'range' : {'type' : 'ranged', 'distance' : 9},
        'speed' : {'type' : 'quick', 'turns' : 1}},
    
    'properties' : {
        'school' : 'air',
        'level' : 2,
        'reusable' : False},
    'description' :'blah,blah'}

spell_dict['invisible fist'] = {
    'name' : 'invisible fist',
    'level' : [['mind', 1]],
    'base cost' : 4,
    'type' : ['force'],
    'function' : attack_spell,
    'parameters' : {
        
        'name' : 'invisible fist',
        'attack dice' : 4,
        'traits' : [['ethereal']],
        'effects' : [[['daze'],8]],
        'target type' : 'creature',
        'range' : {'type' : 'ranged', 'distance' : 6},
        'speed' : {'type' : 'quick', 'turns' : 1}},
    
    'properties' : {
        'school' : 'mind',
        'level' : 1,
        'reusable' : False},
    'description' :'Mordok invented the spell as an easy way to enforce discipline amongst his apprentices'}

spell_dict['pillar of light'] = {
    'name' : 'pillar of light',
    'level' : [['holy', 1]],
    'base cost' : 5,
    'type' : ['light'],
    'function' : attack_spell,
    'parameters' : {
        
        'name' : 'pillar of light',
        'attack dice' : 2,
        'traits' : [['ethereal'],['vs nonliving +', 2]],
        'effects' : [[['daze'],4],[['stun'],11]],
        'target type' : 'creature',
        'range' : {'type' : 'ranged', 'distance' : 6},
        'speed' : {'type' : 'quick', 'turns' : 1}},
    
    'properties' : {
        'school' : 'holy',
        'level' : 1,
        'reusable' : False},
    'description' :'Blah blah blah light'}

spell_dict['ring of fire'] = {
    'name' : 'ring of fire',
    'level' : [['fire', 2]],
    'base cost' : 9,
    'type' : ['flame'],
    'function' : attack_spell,
    'parameters' : {
        
        'name' : 'ring of fire',
        'attack dice' : 5,
        'traits' : [['unavoidable'],['defrost'],['zone']],
        'effects' : [[['burn'],7],[['burn','burn'],11]],
        'target type' : 'circle',
        'range' : {'type' : 'ranged', 'distance' : 0},
        'speed' : {'type' : 'full', 'turns' : 3}},
    
    'properties' : {
        'school' : 'fire',
        'level' : 2,
        'reusable' : False},
    'description' :'\"Fire is a living thing, but it can be commanded\ninto shapes through your will. A wall is simple,\na ring difficult, but perhaps more useful.\"\n -Mastery of Fire: A Primer of Spells'}

spell_dict['hail of stones'] = {
    'name' : 'hail of stones',
    'level' : [['earth', 2]],
    'base cost' : 8,
    'type' : [],
    'function' : attack_spell,
    'parameters' : {
        
        'name' : 'hail of stones',
        'attack dice' : 4,
        'traits' : [['unavoidable'],['zone']],
        'effects' : [[['daze'],6],[['stun'],11]],
        'target type' : 'zone',
        'range' : {'type' : 'ranged', 'distance' : 6},
        'speed' : {'type' : 'full', 'turns' : 3}},
    
    'properties' : {
        'school' : 'earth',
        'level' : 2,
        'reusable' : False},
    'description' :'\"Throwing a rock will not deter an enemy. But throwing a\nhundred rocks will rout them!\"\n -Gurmash, Orc Warmaster'}

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
    'properties' : {
        'school' : 'holy',
        'level' : 1,
        'reusable' : False},
    'description' : '\"No scratch is insignificant to the Goddess\"\n -On Health and Blessings True'}

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
    'properties' : {
        'school' : 'holy',
        'level' : 2,
        'reusable' : False},
    'description' : 'blah blah'}
