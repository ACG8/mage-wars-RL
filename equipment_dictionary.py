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

def get_equipment(name, x, y):
    arg = equip_dict[name]

    attacks = []
    if arg['attacks']:
        for atk in arg['attacks']:
            attacks.append(adic.get_attack(atk))
    
    #generate defenses
    defense = adic.get_defense(arg['defense'])
    
    equipment_component = obcl.Equipment(arg['slot'], arg['trait bonus'], attacks, defense)
    equipment = obcl.Object(x, y,
        equipment=equipment_component, traits = arg['traits'],
        properties = arg['properties'].copy())
    return equipment

equip_dict['vorpal blade'] = {
    'spawn chance' : [{'level' : 1, 'value' : 25}],
    'slot' : 'right hand',
    'traits' : [],
    'trait bonus' : [],
    'attacks' : [{
        
        'name' : 'razor edged slash',
        'attack dice' : 4,
        'traits' : [['piercing +', 2]],
        'effects' : [],
        'target type' : 'creature',
        'range' : {'type' : 'melee', 'distance' : 1},
        'speed' : {'type' : 'quick', 'turns' : 2}}],
    
    'defense' : None,
    'properties' : {
        'name' : 'vorpal blade',
        'graphic' : '/',
        'color' : libtcod.sky,
        'description' : 'Razor Edged Slash:\nMelee 4\nPiercing +2\n\nThe blade is impossibly sharp...able to cut through bone and muscle with hardly any effort. How do you sheath it?'}}

equip_dict['spiked buckler'] = {
    'spawn chance' : [{'level' : 1, 'value' : 25}],
    'slot' : 'left hand',
    'traits' : [],
    'trait bonus' : [],
    'attacks' : [{

        'name' : 'shield bash',
        'attack dice' : 3,
        'traits' : [['piercing +', 1]],
        'effects' : [],
        'target type' : 'creature',
        'range' : {'type' : 'melee', 'distance' : 1},
        'speed' : {'type' : 'quick', 'turns' : 2}}],
    
    'defense' : {
        
        'minimum roll' : 8,
        'range' : 'melee',
        'max uses' : 1,
        'effect' : 'shield bash'},

    'properties' : {
        'name' : 'spiked buckler',
        'graphic' : '}',
        'color' : libtcod.sky,
        'description' :'Shield Bash:\nMelee 3\nPiercing +1\n\nSometimes, the best offense is a good defense.'}}

equip_dict['leather boots'] = {
    'spawn chance' : [
        {'level' : 1, 'value' : 40},
        {'level' : 2, 'value' : 30}],
    'slot' : 'feet',
    'traits' : [],
    'trait bonus' : [['armor +',1]],
    'attacks' : [],
    'defense' : None,
    'properties' : {
        'name' : 'leather boots',
        'graphic' : ':',
        'color' : libtcod.orange,
        'description' : 'Leather Boots\n\nArmor +1\n\n\n"They\'re good for kicking, tripping, stomping, and walking. I prefer running myself.\"\n  -Baldric the Yellow'}}

equip_dict['reflex boots'] = {
    'spawn chance' : [
        {'level' : 1, 'value' : 20},
        {'level' : 2, 'value' : 30}],
    'slot' : 'feet',
    'traits' : [],
    'trait bonus' : [],
    'attacks' : [],
    'defense' : {
        'minimum roll' : 7,
        'range' : 'any',
        'max uses' : 1,
        'effect' : None},
    'properties' : {
        'name' : 'reflex boots',
        'graphic' : ':',
        'color' : libtcod.light_han,
        'description' : 'Reflex Boots\n\nGrants a Defense (7)\n\n\n\"Agility is the greatest asset on the battlefield.\"\n -Johktari Battle Manual'}}

equip_dict['regrowth belt'] = {
    'spawn chance' : [
        {'level' : 1, 'value' : 5},
        {'level' : 2, 'value' : 20}],
    'slot' : 'belt',
    'traits' : [],
    'trait bonus' : [['regenerate ',2]],
    'attacks' : [],
    'defense' : None,
    'properties' : {
        'name' : 'regrowth belt',
        'graphic' : '=',
        'color' : libtcod.darkest_green,
        'description' : 'Regrowth Belt\n\nRegenerate 2\n\n\n\"The belt actually heals his life?\"\n\"And it holds his pants up, too.\"'}}

equip_dict['veteran\'s belt'] = {
    'spawn chance' : [
        {'level' : 1, 'value' : 10},
        {'level' : 2, 'value' : 30}],
    'slot' : 'belt',
    'traits' : [],
    'trait bonus' : [['sturdy +',2]],
    'attacks' : [],
    'defense' : None,
    'properties' : {
        'name' : 'veteran\'s belt',
        'graphic' : '=',
        'color' : libtcod.dark_sepia,
        'description' : 'Veteran\'s Belt\n\nSturdy 2\n\n\n\Your skill may be refined, but my experience is greater.'}}

equip_dict['leather gloves'] = {

    'spawn chance' : [
        {'level' : 1, 'value' : 40},
        {'level' : 2, 'value' : 30}],
    'slot' : 'hands',
    'traits' : [],
    'trait bonus' : [['armor +',1]],
    'attacks' : [],
    'defense' : None,
    'properties' : {
        'name' : 'leather gloves',
        'graphic' : ':',
        'color' : libtcod.orange,
        'description' : 'Leather Gloves\n\nArmor +1\n\n\"Revolution does not wear silk gloves\"\n -Olkaff, Warlord of Woad'}}

equip_dict['defense ring'] = {
    'spawn chance' : [{'level' : 1, 'value' : 25}],
    'slot' : 'finger',
    'traits' : [],
    'trait bonus' : [['defense +',1]],
    'attacks' : [],
    'defense' : None,
    'properties' : {
        'name' : 'defense ring',
        'graphic' : '.',
        'color' : libtcod.gold,
        'description' : 'Defense Ring\n +1 to all Defenses\n\n\"Shields are so primitive. No need to sacrifice style for protection.\"\n -Xer, Arbiter of Eldritch Design'}}

equip_dict['gauntlets of strength'] = {
    'spawn chance' : [
        {'level' : 1, 'value' : 40},
        {'level' : 2, 'value' : 30}],
    'slot' : 'hands',
    'traits' : [],
    'trait bonus' : [['melee +',1]],
    'attacks' : [],
    'defense' : None,
    'properties' : {
        'name' : 'gauntlets of strength',
        'graphic' : ':',
        'color' : libtcod.red,
        'description' : 'gauntlets'}}
