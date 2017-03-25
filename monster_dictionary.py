import map_functions as mpfn
import object_classes as obcl
import action_classes as accl
import libtcodpy as libtcod

############################################################
# MONSTER DICTIONARY
# This file contains following:
# 1. The function to create a monster
# 2. Definitions for all monsters in the game.
############################################################
# 1: Monster Creation Function

def create_monster(name, x, y):
    arg = mons_dict[name]
    creature_component = obcl.Creature(arg['life'], arg['mana'], arg['channeling'], arg['armor'], arg['experience'], arg['attacks'],
        death_function=obcl.monster_death)
    ai_component = obcl.BasicMonster()
    monster = obcl.Object(x, y, arg['character'], arg['name'], arg['color'], traits=arg['traits'], description=arg['description'],
        blocks=True, creature=creature_component, ai=ai_component)
    return monster

############################################################
# 2: Monster Dictionary

mons_dict = {}

mons_dict['goblin grunt'] = {
    'name' : 'goblin grunt',
    'spawn chance' : mpfn.from_dungeon_level([[30, 1],[15,3]]),
    'character' : 'g',
    'color' : libtcod.light_red,
    'life' : 4,
    'mana' : 0,
    'channeling' : 0,
    'armor' : 0,
    'experience' : 20,
    'traits' : [],
    'attacks' : ['basic melee attack'],
    'description' : 'Grunt, grunt.'}

mons_dict['bitterwood fox'] = {
    'name' : 'bitterwood fox',
    'spawn chance' : mpfn.from_dungeon_level([[20, 1],[20,2]]),
    'character' : 'f',
    'color' : libtcod.light_red,
    'life' : 5,
    'mana' : 0,
    'channeling' : 0,
    'armor' : 0,
    'experience' : 35,
    'traits' : [['fast']],
    'attacks' : ['basic melee attack'],
    'description' : 'foo'}

mons_dict['darkfenne hydra'] = {
    'name' : 'darkfenne hydra',
    'spawn chance' : mpfn.from_dungeon_level([[5, 1],[15,3]]),
    'character' : 'H',
    'color' : libtcod.dark_red,
    'life' : 15,
    'mana' : 0,
    'channeling' : 0,
    'armor' : 1,
    'experience' : 100,
    'traits' : [['slow'],['regenerate',2]],
    'attacks' : ['triple bite'],
    'description' : 'uh oh'}
