import attack_dictionary as adic
import object_classes as obcl
import libtcodpy as libtcod
import definitions as defn
import spell_dictionary as sdic

mages = [
    'straywood beastmaster',
    'pellian forcemaster']

basic_attack = {
        
        'name' : 'basic melee attack',
        'attack dice' : 3,
        'traits' : [['beastmaster']],
        'effects' : [],
        'target type' : 'creature',
        'range' : ['melee',1],
        'speed' : {
            'type' : 'quick',
            'turns' : 2}}

def create_player(mage, x, y):
    #arg = mage_dict[mage]

    #get players's attacks
    
    attacks = []
    if mage['attacks']:
        for atk in mage['attacks']:
            attacks.append(adic.get_attack(atk))

    #get monster's defense

    defense = [adic.get_defense(mage['defense'])]

    #note: armor, xp is hardcoded as zero
    creature_component = obcl.Creature(
        hp = mage['life'],
        mana = mage['mana'],
        channeling = mage['channeling'],
        armor = 0,
        xp = 0,
        attacks = attacks,
        defense = defense,
        alignment = 'player',
        death_function=obcl.player_death)
    
    defn.player = obcl.Object(
        x, y,
        char = '@',
        name = 'player',
        color = libtcod.white,
        traits=mage['traits'],
        blocks=True,
        creature=creature_component)
    
    defn.player.level = 1
    defn.training = mage['training']
    defn.antitraining = mage['antitraining']

    for spell in mage['spells']:
        new_spell = sdic.get_spell(spell)
        defn.spellbook.append(new_spell)
    
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
        'description' : '\"Come a little closer...\"'}],
    
    'training' : ['mind'],
    'antitraining' : ['creatures'],
    'life' : 32,
    'mana' : 10,
    'channeling' : 10}
    
mage_dict['straywood beastmaster'] = {
    'name' : 'straywood beastmaster',
    'traits' : [['melee +', 1]],
    'attacks' : [basic_attack],
    'defense' : None,
    'spells' : [],
    'training' : ['nature'],
    'antitraining' : ['fire'],
    'life' : 36,
    'mana' : 10,
    'channeling' : 9}
