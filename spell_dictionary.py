import attack_dictionary as adic
import spell_functions as spfn
import definitions as defn
import gui
import libtcodpy as libtcod
import map_functions as mpfn
import time
import game
import monster_dictionary as mdic
import enchantments as ech

def enchant_spell(parameters, source=None, target=None):
    if source==None:
        source=defn.player
        if parameters['target type']=='zone':
            spfn.target_tile(arg['name'])
            #placeholder for zone spells
        elif parameters['target type']=='creature':
            #find target. currently geared to ranged attacks, though can easily be extended to melee
            target=spfn.target_monster(parameters['range'])
            if target:
                enchantment = ech.get_enchantment(parameters['enchantment'])
                target.enchantments.append(enchantment)
            else:
                return 'cancelled'
    

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

def reanimation_spell(parameters, source=None, target=None):
    if source==None:
        source=defn.player
        (x,y) = spfn.target_tile(parameters['range'])
        if x:
            for obj in defn.dungeon[x][y].objects:
                if obj.corpse:
                    monster = mdic.get_monster(obj.corpse.properties['name'], x,y)
                    if ['nonliving'] in monster.traits:
                        return 'cancelled'
                    ##this will lead to an eventual error when corpses are stacked, if the top corpse is nonliving then the rest cannot be reanimated. I'll fix this later.
                    monster.creature.alignment = 'player'
                    monster.traits += [['bloodthirsty +',0], ['slow'], ['nonliving']]
                    monster.creature.conditions.append('zombie')
                    defn.objects.append(monster)
                    defn.dungeon[x][y].objects.append(monster)
                    defn.objects.remove(obj)
                    defn.dungeon[x][y].objects.remove(obj)
                    return 'succeeded'
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
                    #currently manages only random healing amounts
                    amount = sum([libtcod.random_get_int(0,0,2) for i in range(parameters['amount healed'])])
                    target.creature.heal(amount)
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
            (x,y) = spfn.target_tile(parameters['range']['distance'])
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
    def describe(self):
        #render the screen. this erases the inventory and shows the names of objects under the mouse.
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,defn.key,defn.mouse)
        game.render_all()
        gui.msgbox(self.properties['description'])

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
        'description' : 'Lightning Attack 5\nEffective against incorporeal enemies\nMay daze or stun target\n\n' +
        '\"You see soldiers of Westlock. I see little lightning rods.\"\n -Laddinfance, Primus of the White Spires'}}

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
        'description' : 'Attack 4\nEffective against incorporeal enemies\nMay daze target\n\n' +
        'Mordok invented the spell as an easy way to enforce discipline amongst his apprentices'}}

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
        'description' : 'Light Attack 2\nEffective against incorporeal enemies\n+2 vs. Nonliving targets\nMay daze or stun target\n\n' +
        '\"The Dawnbreaker has cast\nhis judgement upon thee, and it is vengeance!\"\n -Yarbyn, Paladin of Westlock'}}

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
        'description' : 'Flame Attack 5\nMay burn targets\nAffects all other creatures within 3 tiles of caster\n\n' +
        '\"Fire is a living thing, but it can be commanded\ninto shapes through your will. A wall is simple,\na ring difficult, but perhaps more useful.\"\n -Mastery of Fire: A Primer of Spells'}}

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
        'description' : 'Attack 4\nMay daze or stun targets\nAffects all creatures within 3 tiles of targeted location\n\n' +
        '\"Throwing a rock will not deter an enemy. But throwing a\nhundred rocks will rout them!\"\n -Gurmash, Orc Warmaster'}}

spell_dict['minor heal'] = {
    'name' : 'minor heal',
    'level' : [['holy' ,1]],
    'base cost' : 5,
    'type' : ['healing'],
    'function' : healing_spell,
    'parameters' : {
        'range' : 5,
        'target type' : 'creature',
        'amount healed' : 5,
        'conditions removed' : None},
    'properties' : {
        'school' : 'holy',
        'level' : 1,
        'description' : 'Heal 5\n\n' +
        '\"No scratch is insignificant to the Goddess\"\n -On Health and Blessings True'}}

spell_dict['heal'] = {
    'name' : 'heal',
    'level' : [['holy', 2]],
    'base cost' : 9,
    'type' : ['healing'],
    'function' : healing_spell,
    'parameters' : {
        'range' : 5,
        'target type' : 'creature',
        'amount healed' : 8,
        'conditions removed' : None},
    'properties' : {
        'school' : 'holy',
        'level' : 2,
        'description' : 'Heal 8\n\n' +
        '\"Westlock is a frail nation, but their faith is strong. With it,\nthey have saved those I have sent to death\'s door.\"\n -Trokoth, of the Blood Wave'}}

spell_dict['animate dead'] = {
    'name' : 'animate dead',
    'level' : [['dark', 3]],
    'base cost' : 9,
    'type' : ['necro'],
    'function' : reanimation_spell,
    'parameters' : {
        'range' : 3,
        'target type' : 'remains'},
    'properties' : {
        'school' : 'dark',
        'level' : 3,
        'description' : 'Animates a nearby corpse to serve you as a zombie.\nHas no effect on the corpses of nonliving creatures.' +
        '\"Come, forgotten one. I am your master now!\"\n - Shlaka, Blight of Darkfenne'}}

spell_dict['enfeeble'] = {
    'name' : 'enfeeble',
    'level' : [['dark', 2]],
    'base cost' : 6,
    'type' : ['curse'],
    'function' : enchant_spell,
    'parameters' : {
        'range' : 6,
        'target type' : 'creature',
        'enchantment' : {
            'name' : 'enfeeble',
            'function' : None,
            'parameters' : None,
            'trait bonus' : [['slow']]}},
    'properties' : {
        'school' : 'dark',
        'level' : 2,
        'description' : 'Slows the movement of a creature.'}}
