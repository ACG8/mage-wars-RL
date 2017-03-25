import map_functions as mpfn
import object_classes as obcl
import action_classes as accl
import libtcodpy as libtcod
import definitions as defn

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
        return []  #other objects have no equipment

equip_dict = {}

def create_equipment(name, x, y):
    arg = equip_dict[name]
    equipment_component = obcl.Equipment(arg['slot'], arg['trait bonus'], arg['attacks'])
    equipment = obcl.Object(x, y, arg['character'], arg['name'], arg['color'], description=arg['description'],
        equipment=equipment_component, traits = arg['traits'])
    return equipment

equip_dict['sword'] = {
    'name' : 'sword',
    'spawn chance' : 25,
    'character' : '/',
    'color' : libtcod.sky,
    'slot' : 'right hand',
    'traits' : [],
    'trait bonus' : [],
    'attacks' : ['sword attack'],
    'description' : 'A sharp blade for stabbing things. Hey, it\'s better than nothing.'}

equip_dict['leather boots'] = {
    'name' : 'leather boots',
    'spawn chance' : mpfn.from_dungeon_level([[25, 1],[15, 2]]),
    'character' : ':',
    'color' : libtcod.orange,
    'slot' : 'feet',
    'traits' : [],
    'trait bonus' : [['armor +',1]],
    'attacks' : [],
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
    'description' : 'gloves'}

equip_dict['gauntlets of strength'] = {
    'name' : 'gauntlets of strength',
    'spawn chance' : mpfn.from_dungeon_level([[25, 1],[15, 2]]),
    'character' : ':',
    'color' : libtcod.red,
    'slot' : 'hands',
    'traits' : [],
    'trait bonus' : [['melee +',1]],
    'attacks' : [],
    'description' : 'gauntlets'}
