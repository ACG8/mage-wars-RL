import libtcodpy as libtcod
import map_functions as mpfn
import object_classes as obcl
import spell_functions as spfn

#equipment dictionary
#each equipment is an array: [name, chance of appearing, symbol, color, slot, traits (for you), attacks, description]

equip_dict = {}

def create_equipment(name, x, y):
    choice = equip_dict[name]
    equipment_component = obcl.Equipment(slot=choice[4], trait_bonus=choice[5], attacks=choice[6])
    equipment = obcl.Object(x, y, choice[2], choice[0], choice[3], description=choice[7], equipment=equipment_component)
    return equipment

equip_dict['sword'] = ['sword',
    15,
    '/',
    libtcod.sky,
    'right hand',
    [],
    ['sword attack'],
    'A sharp blade for stabbing things. Hey, it\'s better than nothing.']

equip_dict['leather boots'] = ['leather boots',
    mpfn.from_dungeon_level([[25, 1],[15, 2]]),
    ':',
    libtcod.orange,
    'feet',
    [['armor +',1]],
    [],
    '\"They\'re good for kicking, tripping, stomping, and walking. I prefer running myself.\"\n-Baldric the Yellow']

equip_dict['leather gloves'] = ['leather gloves',
    mpfn.from_dungeon_level([[25, 1],[15, 2]]),
    ':',
    libtcod.orange,
    'hands',
    [['armor +', 1]],
    [],
    'Foo']

equip_dict['gauntlets of strength'] = ['gauntlets of strength',
    mpfn.from_dungeon_level([[25, 1],[15, 2]]),
    ':',
    libtcod.red,
    'hands',
    [['melee +', 1]],
    [],
    'Foo']

#item dictionary
#each item is an array: [name, chance of appearing, symbol, color, effect, description]

item_dict = {}

item_dict['healing potion'] = ['healing potion',
    35,
    '!',
    libtcod.violet,
    spfn.cast_heal,
    'Mmm, healthy.']

item_dict['scroll of lightning bolt'] = ['scroll of lightning bolt',
    mpfn.from_dungeon_level([[100, 1]]),
    '#',
    libtcod.light_yellow,
    spfn.scroll,
    'Owch.']

#array = [name, chance, symbol, color, hp, mana, armor, power, xp, ai, traits, attack, description]
mons_dict = {}

def create_monster(name, x, y):
    choice = mons_dict[name]
    creature_component = obcl.Creature(choice[4], choice[5], choice[6], choice[7], choice[9], death_function=obcl.monster_death)
    ai_component = obcl.BasicMonster()
    monster = obcl.Object(x, y,
        choice[2],
        choice[0],
        choice[3],
        blocks=True,
        description=choice[10],
        creature=creature_component,
        ai=ai_component,
        traits=choice[8])
    return monster

#mons_dict[key] = [0:name
    #1: chance of appearing
    #2: symbol
    #3: color
    #4,5,6: hp,mana,armor
    #7: experience
    #8: traits
    #9: attacks
    #10: description

mons_dict['goblin grunt'] = ['goblin grunt',
    mpfn.from_dungeon_level([[30, 1],[15,3]]),
    'g',
    libtcod.light_red,
    4, 0, 0,
    20,
    [],
    ['basic attack'],
    'Grunt, grunt.']

mons_dict['bitterwood fox'] = ['bitterwood fox',
    mpfn.from_dungeon_level([[20, 1]]),
    'f',
    libtcod.light_red,
    5, 0, 0,
    35,
    #ai_basic,
    [['fast']],
    ['basic attack'],
    'fox, fox']

mons_dict['darkfenne hydra'] = ['darkfenne hydra',
    mpfn.from_dungeon_level([[10, 1]]),
    'H',
    libtcod.darker_red,
    15, 0, 1,
    100,
    #ai_basic,
    [['slow'],['regenerate',2]],
    ['triple bite'],
    'uh-oh']

def tempstore():
    for i in range(num_items):
        #choose random spot for this item
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)
 
        #only place it if the tile is not blocked

        if not mpfn.is_blocked(x, y):
            choice = rng.random_choice(item_chances)
            if choice == 'fireball':
                item_component = obcl.Item(use_function=spfn.cast_fireball) 
                item = obcl.Object(x, y, '#', 'scroll of fireball', libtcod.light_yellow, item=item_component)
                item.always_visible = True
            elif choice == 'confuse':
                item_component = obcl.Item(use_function=spfn.cast_confuse)
                item = obcl.Object(x, y, '#', 'scroll of confusion', libtcod.light_yellow, item=item_component)
                item.always_visible = True
            defn.objects.append(item)
            item.send_to_back()
