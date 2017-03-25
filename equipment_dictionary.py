import map_functions as mpfn
import object_classes as obcl
import action_classes as accl
import libtcodpy as libtcod
import definitions as defn
import attack_dictionary as adic

def get_equipped_in_slot(obj, slot):  #returns the equipment in a slot, or None if it's empty
    if obj == defn.player:
        for item in defn.inventory:
            if item.equipment and item.equipment.slot == slot and item.equipment.is_equipped:
                return item.equipment
    return None

def get_all_equipped(obj):  #returns a list of equipped items
    if obj == defn.player:
        equipped_list = []
        for item in defn.inventory:
            if item.equipment and item.equipment.is_equipped:
                equipped_list.append(item.equipment)
        return equipped_list
    else:
        return [] #other objects have no equipment

equip_dict = {}

def create_equipment(name, x, y):
    arg = equip_dict[name]
    #generate defenses
    defense = adic.get_defense(arg['defense'])
    equipment_component = obcl.Equipment(arg['slot'], arg['trait bonus'], arg['attacks'], defense)
    equipment = obcl.Object(x, y, arg['character'], arg['name'], arg['color'], description=arg['description'],
        equipment=equipment_component, traits = arg['traits'])
    return equipment

equip_dict['vorpal blade'] = {
    'name' : 'vorpal blade',
    'spawn chance' : 25,
    'character' : '/',
    'color' : libtcod.sky,
    'slot' : 'right hand',
    'traits' : [],
    'trait bonus' : [],
    'attacks' : ['razor edged slash'],
    'defense' : None,
    'description' : 'Razor Edged Slash:\nMelee 4\nPiercing +2\n\nThe blade is impossibly sharp...able to cut through bone and muscle with hardly any effort. How do you sheath it?'}

equip_dict['spiked buckler'] = {
    'name' : 'spiked buckler',
    'spawn chance' : 100,
    'character' : '}',
    'color' : libtcod.sky,
    'slot' : 'left hand',
    'traits' : [],
    'trait bonus' : [],
    'attacks' : ['shield bash'],
    'defense' : {
        'minimum roll' : 8,
        'range' : 'melee',
        'max uses' : 1,
        'effect' : 'shield bash'},
    'description' :'Shield Bash:\nMelee 3\nPiercing +1\n\nSometimes, the best offense is a good defense.'}

equip_dict['leather boots'] = {
    'name' : 'leather boots',
    'spawn chance' : mpfn.from_dungeon_level([[25, 1],[15, 2]]),
    'character' : ':',
    'color' : libtcod.orange,
    'slot' : 'feet',
    'traits' : [],
    'trait bonus' : [['armor +',1]],
    'attacks' : [],
    'defense' : None,
    'description' : 'Leather Boots\n\nArmor+1\n\n\n"They\'re good for kicking, tripping, stomping, and walking. I prefer running myself.\"\n  -Baldric the Yellow'}

equip_dict['leather gloves'] = {
    'name' : 'leather gloves',
    'spawn chance' : mpfn.from_dungeon_level([[25, 1],[15, 2]]),
    'character' : ':',
    'color' : libtcod.orange,
    'slot' : 'hands',
    'traits' : [],
    'trait bonus' : [['armor +',1]],
    'attacks' : [],
    'defense' : None,
    'description' : 'gloves'}

equip_dict['defense ring'] = {
    'name' : 'defense ring',
    'spawn chance' : 100,
    'character' : '.',
    'color' : libtcod.blue,
    'slot' : 'finger',
    'traits' : [],
    'trait bonus' : [['defense +',1]],
    'attacks' : [],
    'defense' : None,
    'description' : 'Defense Ring\n+1 to all Defenses\n\n\"Shields are so primitive. No need to sacrifice style for protection.\"\n -Xer, Arbiter of Eldritch Design'}

equip_dict['gauntlets of strength'] = {
    'name' : 'gauntlets of strength',
    'spawn chance' : mpfn.from_dungeon_level([[25, 1],[15, 2]]),
    'character' : ':',
    'color' : libtcod.red,
    'slot' : 'hands',
    'traits' : [],
    'trait bonus' : [['melee +',1]],
    'attacks' : [],
    'defense' : None,
    'description' : 'gauntlets'}
