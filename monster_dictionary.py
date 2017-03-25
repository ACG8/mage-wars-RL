import map_functions as mpfn
import object_classes as obcl
import action_classes as accl
import libtcodpy as libtcod
import ai_dictionary as aidic
import attack_dictionary as adic
import ai_dictionary as aidic

#############################################################
# MONSTER DICTIONARY                                        #
# This file contains following:                             #
# 1. The function to create a monster                       #
# 2. Definitions for all monsters in the game.              #
#############################################################

################################
# 1: Monster Creation Function #
################################

def get_monster(name, x, y):
    arg = mons_dict[name]

    #get monster's attacks
    
    attacks = []
    if arg['attacks']:
        for atk in arg['attacks']:
            attacks.append(adic.get_attack(atk))

    #get monster's defense

    defense = [adic.get_defense(arg['defense'])]
    
    creature_component = obcl.Creature(
        hp = arg['life'],
        mana = arg['mana'],
        channeling = arg['channeling'],
        armor = arg['armor'],
        xp = arg['experience'],
        attacks = attacks,
        defense = defense,
        alignment = 'dungeon',
        death_function=obcl.monster_death)
    
    #ai_component = obcl.BasicMonster()
    ai = arg['ai']
    
    ai_component = aidic.Ai(ai['personality'],ai['traits'], ai['senses'])#aidic.ai_dict['traits'])
    monster = obcl.Object(x, y, arg['character'], arg['name'], arg['color'], traits=arg['traits'], description=arg['description'],
        blocks=True, creature=creature_component, ai=ai_component)
    return monster

#########################
# 2: Monster Dictionary #
#########################

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
    'attacks' : [{
        
        'name' : 'basic melee attack',
        'attack dice' : 3,
        'traits' : [],
        'effects' : [],
        'target type' : 'creature',
        'range' : ['melee',1],
        'speed' : {
            'type' : 'quick',
            'turns' : 2}}],
    
    'defense' : None,
    'ai' : aidic.ai_dict['canine'],
    'description' : 'Grunt, grunt.'}

mons_dict['zombie crawler'] = {
    'name' : 'zombie crawler',
    'spawn chance' : mpfn.from_dungeon_level([[30, 1],[15,3]]),
    'character' : 'z',
    'color' : libtcod.light_red,
    'life' : 4,
    'mana' : 0,
    'channeling' : 0,
    'armor' : 0,
    'experience' : 20,
    'traits' : [['bloodthirsty +', 1],['slow'],['pest'],['resilient'],['psychic immunity'],['nonliving']],#,['poison immunity']],
    'attacks' : [{
        
        'name' : 'bite',
        'attack dice' : 2,
        'traits' : [],
        'effects' : [],
        'target type' : 'creature',
        'range' : ['melee',1],
        'speed' : {
            'type' : 'quick',
            'turns' : 2}}],
    
    'defense' : None,
    'ai' : aidic.ai_dict['zombie'],
    'description' : 'Watch where you step! Those half-corpses are still alive!'}

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
    'attacks' : [{
        
        'name' : 'basic melee attack',
        'attack dice' : 3,
        'traits' : [],
        'effects' : [],
        'target type' : 'creature',
        'range' : ['melee',1],
        'speed' : {
            'type' : 'quick',
            'turns' : 2}}],
    
    'defense' : None,
    'ai' : aidic.ai_dict['canine'],
    'description' : 'foo'}

mons_dict['emerald tegu'] = {
    'name' : 'emerald tegu',
    'spawn chance' : mpfn.from_dungeon_level([[20, 1],[20,2]]),
    'character' : 't',
    'color' : libtcod.green,
    'life' : 9,
    'mana' : 0,
    'channeling' : 0,
    'armor' : 2,
    'experience' : 35,
    'traits' : [],
    'attacks' : [{
        
        'name' : 'venomous bite',
        'attack dice' : 3,
        'traits' : [],
        'effects' : [[['rot'],9]],
        'target type' : 'creature',
        'range' : ['melee',1],
        'speed' : {
            'type' : 'quick',
            'turns' : 2}}],
    
    'defense' : None,
    'ai' : aidic.ai_dict['canine'],
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
    'attacks' : [{
        
        'name' : 'triple bite',
        'attack dice' : 3,
        'traits' : [['triplestrike']],
        'effects' : [],
        'target type' : 'creature',
        'range' : ['melee', 1],
        'speed' : {
            'type' : 'full',
            'turns' : 4}},{

        'name' : 'snapping bite',
        'attack dice' : 4,
        'traits' : [['counterstrike']],
        'effects' : [],
        'target type' : 'creature',
        'range' : ['melee', 1],
        'speed' : {
            'type' : 'quick',
            'turns' : 2}}],

    'defense' : None,
    'ai' : aidic.ai_dict['canine'],
    'description' : 'uh oh'}
