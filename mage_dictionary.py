import attack_dictionary as adic
import object_classes as obcl
import libtcodpy as libtcod
import definitions as defn
import spell_dictionary as sdic
import spell_functions as spfn
import gui

mages = [
    'pellian forcemaster',
    'straywood beastmaster',
    'johktari beastmaster',
    ]

basic_attack = {
        
        'name' : 'basic melee attack',
        'attack dice' : 3,
        'traits' : [['beastmaster']],
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
            'level' : 2,
            'subtypes' : None},
        blocks=True,
        creature=creature_component)

    defn.training = mage['training']
    defn.antitraining = mage['antitraining']

    for spell in mage['spells']:
        new_spell = sdic.get_spell(spell)
        #defn.spellbook.append(new_spell)
        #for now, player has 1 copies. later, I'll change the way the spellbook works so that the player may have unlimited copies.
        defn.spellbook.append({'name' : new_spell.name, 'copies' : [new_spell], 'reusable' : new_spell.properties['reusable']})
    
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
            'reusable' : True},
        'description' : '\"Come a little closer...\"'}],
    
    'training' : ['mind'],
    'antitraining' : ['creatures'],
    'life' : 32,
    'mana' : 10,
    'channeling' : 10}

#error (probably not from this module: taming a creature unsuccessfully causes it to temporarily disappear.
def tame_beast(parameters, source=None, target=None):
    source=defn.player
    if parameters['target type']=='none':
        pass
            #eventually, maybe we can upgrade so that everything in sight is converted.
    elif parameters['target type']=='creature':
            #find target. currently geared to ranged attacks, though can easily be extended to melee
        target=spfn.target_monster(parameters['range'])
        if target:
            if target.creature.alignment == 'dungeon' and 'animal' in target.properties['subtypes']:
                if defn.player.properties['level'] > target.properties['level']:
                    health_percentage = float(target.creature.hp) / float(target.creature.max_hp)
                    roll = libtcod.random_get_int(0,1,100) * health_percentage
                    if roll < 10 * float(defn.player.properties['level'] - target.properties['level']):
                        target.creature.alignment = 'player'
                        target.creature.color = libtcod.white
                        gui.message('The ' + target.name + ' submits to your will!', libtcod.green)
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


mage_dict['straywood beastmaster'] = {
    'name' : 'straywood beastmaster',
    'traits' : [['melee +', 1]],
    'attacks' : [basic_attack],
    'defense' : None,
    'spells' : [{
        
        'name' : 'tame beast',
        'level' : [['nature', 1]],
        'base cost' : 1,
        'type' : ['command'],
        'function' : tame_beast,
        'parameters' : {
            'range' : 3,
            'target type' : 'creature'},
        'properties' : {
            'school' : 'nature',
            'reusable' : True},
        'description' : 'Attempts to tame a nearby animal. Only animals with a level less than your own can be tamed. The more heavily wounded an animal is, the more likely it is to obey.'}],
    
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
    'spells' : [{
        
        'name' : 'tame beast',
        'level' : [['nature', 1]],
        'base cost' : 1,
        'type' : ['command'],
        'function' : tame_beast,
        'parameters' : {
            'range' : 3,
            'target type' : 'creature'},
        'properties' : {
            'school' : 'nature',
            'reusable' : True},
        'description' : 'Attempts to tame a nearby animal. Only animals with a level less than your own can be tamed. The more heavily wounded an animal is, the more likely it is to obey.'}],
    
    'training' : ['nature'],
    'antitraining' : ['fire'],
    'life' : 34,
    'mana' : 10,
    'channeling' : 9}
