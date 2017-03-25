import libtcodpy as libtcod
import map_functions as mpfn
import object_classes as obcl

#item dictionary
#each item is an array: [chance of appearing, symbol, color, equipment component, description]

equip_dict = {}

equip_dict['sword'] = [
    chance = 15
    symbol = '/'
    color = libtcod.sky
    equipment_component = obcl.Equipment(slot='right hand', power_bonus=1)
    description = 'A sharp blade for stabbing things. Hey, it\'s better than nothing.']
equip_dict['leather boots'] = [
    chance = mpfn.from_dungeon_level([[25, 1],[15, 2]]) 
    symbol = ':'
    color = libtcod.orange
    equipment_component = obcl.Equipment(slot='feet', armor_bonus=1)
    description = '\"They\'re good for kicking, tripping, stomping, and walking. I prefer running myself.\" \n-Baldric the Yellow']
equip_dict['leather gloves'] = [
    chance = mpfn.from_dungeon_level([[25, 1][15, 2]]) 
    symbol = ':'
    color = libtcod.orange
    equipment_component = obcl.Equipment(slot='hands', armor_bonus=1)
    description = 'Foo']
equip_dict['war gauntlets'] = [
    chance = mpfn.from_dungeon_level([[25, 1][15, 2]]) 
    symbol = ':'
    color = libtcod.red
    equipment_component = obcl.Equipment(slot='hands', power_bonus=1)
    description = 'Foo']
