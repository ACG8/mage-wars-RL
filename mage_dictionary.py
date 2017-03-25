import attack_dictionary as adic
import object_classes as obcl
import libtcodpy as libtcod
import definitions as defn
import spell_dictionary as sdic
import spell_functions as spfn
import gui
import lists
import input_text as itxt

mages = [
    'arraxian crown warlock',
    'pellian forcemaster',
    'straywood beastmaster',
    'johktari beastmaster',
    'sortilege wizard',
    'darkfenne necromancer'
    ]

basic_attack = {
        
        'name' : 'basic melee attack',
        'attack dice' : 3,
        'traits' : [],
        'effects' : [],
        'target type' : 'creature',
        'range' : {'type' : 'melee', 'distance' : 1},
        'speed' : {'type' : 'quick', 'turns' : 2}}

def create_player(mage, x, y):

    #get players's attacks
    
    attacks = []
    if mage['attacks']:
        for atk in mage['attacks']:
            attacks.append(adic.get_attack(atk))

    #get monster's defense

    defense = [adic.get_defense(mage['defense'])]

    #note: armor, xp is hardcoded as zero
    creature_component = obcl.Creature(
        hp = mage['life'] - 10, #using MW values but adjusting for player's level
        mana = mage['mana'],
        channeling = mage['channeling'] - 4, #again, MW values adjusted. Player can regain over time
        armor = 0,
        xp = 0,
        attacks = attacks,
        defense = defense,
        alignment = 'player',
        death_function=obcl.player_death)
    
    defn.player = obcl.Object(
        x, y,
        traits=mage['traits'],
        properties = {
            'name' : mage['name'],
            'graphic' : '@',
            'color' : libtcod.white,
            'level' : 1,
            'subtypes' : None,
            'description' : 'This is you. If you die, the game is over.'},
        blocks=True,
        creature=creature_component)

    defn.player.spellbook = lists.List()
    #defn.player.spellbook.contents = []
    
    defn.training = mage['training']
    defn.antitraining = mage['antitraining']
    defn.player.creatures = [] #might change to allow some mages to start with a pet

    for spell in mage['spells']:
        new_spell = sdic.get_spell(spell)
        defn.player.spellbook.insert(new_spell, 'infinite')
    
    return defn.player
    

mage_dict = {}

mage_dict['pellian forcemaster'] = {
    'name' : 'pellian forcemaster',
    'traits' : [],
    'attacks' : [basic_attack],
    'defense' : {
        
        'minimum roll' : 7,
        'range' : 'any',
        'max uses' : 1,
        'effect' : 'no effect'}, #note: need to alter effect checking so that None is acceptable #note that this defense requires no energy, unlike in the game. Can be changed later.

    'spells' : [{
        
        'name' : 'force pull',
        'level' : [['mind', 1]],
        'base cost' : 1,
        'type' : ['force'],
        'function' : sdic.pushing_spell,
        'parameters' : {
            'range' : 8,
            'target type' : 'creature',
            'direction' : 'inward',
            'distance' : 3},
        'properties' : {
            'school' : 'mind',
            'level' : 1,
            'description' : 'Pulls target creature 3 steps toward caster.' +
            '\"Come a little closer...\"'}}],
    
    'training' : ['mind'],
    'antitraining' : ['creatures'],
    'life' : 32,
    'mana' : 10,
    'channeling' : 10}

mage_dict['sortilege wizard'] = {
    'name' : 'sortilege wizard',
    'traits' : [],
    'attacks' : [basic_attack],
    'defense' : None,
    'spells' : [{
        
        'name' : 'arcane zap',
        'level' : [['arcane', 1]],
        'base cost' : 1,
        'type' : [],
        'function' : sdic.attack_spell,
        'parameters' : {
            
            'name' : 'arcane zap',
            'attack dice' : 3,
            'traits' : [['ethereal']],
            'effects' : [],
            'target type' : 'creature',
            'range' : {'type' : 'ranged', 'distance' : 6},
            'speed' : {'type' : 'quick', 'turns' : 1}},
        
        'properties' : {
            'school' : 'arcane',
            'level' : 1,
            'description' : 'Attack 3\nEthereal.' +
            '\n\nZap!'}}],
    
    'training' : ['arcane'],
    'antitraining' : [],
    'life' : 32,
    'mana' : 10,
    'channeling' : 10}

def tame_animal(parameters, source=None, target=None):
    source=defn.player
    if parameters['target type']=='none':
        pass
            #eventually, maybe we can upgrade so that everything in sight is converted.
    elif parameters['target type']=='creature':
            #find target. currently geared to ranged attacks, though can easily be extended to melee
        target = spfn.target_monster(parameters['range'])
        if target:
            if target.creature.alignment == 'dungeon' and 'animal' in target.properties['subtypes']:
                if defn.player.properties['level'] > target.properties['level']:
                    health_percentage = float(target.creature.hp) / float(target.creature.max_hp)
                    if health_percentage <= parameters['threshold'] or target.creature.hp == 1:
                        target.creature.alignment = 'player'
                        target.color = libtcod.white
                        gui.message('The ' + target.name + ' submits to your will!', libtcod.green)
                        choice = gui.menu('Name your new friend?', ['Yes', 'No'], 24)
                        if choice == 0: #give it a name
                            name = itxt.input_text(50, 5, 'What would you like to name it?\n\n', '\n\n(Press *ENTER* when done)')
                            target.personal_name = name
                        return 'succeeded'
                    else:
                        gui.message('The ' + target.name + ' resists your attempts to tame it.', libtcod.red)
                        return 'failed'
                gui.message('You are not experienced enough to tame that.', libtcod.white)
                return 'cancelled' 
            gui.message('You cannot tame that!', libtcod.white)
            return 'cancelled' 
        else:
            return 'cancelled'

tame_animal_spell = {
        'name' : 'tame animal',
        'base cost' : 1,
        'type' : [],
        'function' : tame_animal,
        'parameters' : {
            'range' : 3,
            'target type' : 'creature',
            'threshold' : 0.15},
        'properties' : {
            'school' : 'nature',
            'level' : 1,
            'description' : 'Tames a wounded animal. Animal must be at either 10% of its maximum life or have only 1 life remaining.\n\nOnly works on creatures of lower level than yourself.\n\n' +
            '\"All you need is a gentle but...firm manner, and they will obey you always."'}}

mage_dict['straywood beastmaster'] = {
    'name' : 'straywood beastmaster',
    'traits' : [['melee +', 1]],
    'attacks' : [basic_attack],
    'defense' : None,
    'spells' : [tame_animal_spell],
    'training' : ['nature'],
    'antitraining' : ['fire'],
    'life' : 36,
    'mana' : 10,
    'channeling' : 9}

mage_dict['johktari beastmaster'] = {
    'name' : 'johktari beastmaster',
    'traits' : [['fast'],['ranged +',1]],
    'attacks' : [basic_attack],
    'defense' : None,
    'spells' : [tame_animal_spell],
    'training' : ['nature'],
    'antitraining' : ['fire'],
    'life' : 34,
    'mana' : 10,
    'channeling' : 9}

mage_dict['arraxian crown warlock'] = {
    'name' : 'arraxian crown warlock',
    'traits' : [['melee +', 1]],
    'attacks' : [basic_attack],
    'defense' : None,
    'spells' : [sdic.spell_dict['enfeeble']],
    'training' : ['fire', 'dark'],
    'antitraining' : ['holy'],
    'life' : 38,
    'mana' : 10,
    'channeling' : 9}

mage_dict['darkfenne necromancer'] = {
    'name' : 'darkfenne necromancer',
    'traits' : [['poison immunity']],
    'attacks' : [basic_attack],
    'defense' : None,
    'spells' : [sdic.spell_dict['animate dead']],
    'training' : ['dark'],
    'antitraining' : ['holy'],
    'life' : 32,
    'mana' : 10,
    'channeling' : 10}
