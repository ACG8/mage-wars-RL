import map_functions as mpfn
import object_classes as obcl
import action_classes as accl
import libtcodpy as libtcod
import spell_functions as spfn
import spell_dictionary as sdic
import definitions as defn
import gui

def cast_heal(parameters):
    #heal the player
    if defn.player.creature.hp == defn.player.creature.max_hp:
        gui.message('You are already at full health.', libtcod.red)
        return 'cancelled'
    gui.message('Your wounds start to feel better!', libtcod.light_violet)
    defn.player.creature.heal(parameters['amount healed'])

def scroll(parameters):
    #mothballing spell learning system. instead, scrolls function as one time uses of the spell, and require mana. I.E. only in very special cases are spells reusable.
    spell = sdic.get_spell(parameters['spell'])
    #arg = sdic.spell_dict[parameters['spell']]
    #spell = sdic.Spell(name = arg['name'], base cost = arg['cost'], function = arg['function'], parameters = arg['parameters'])
    #attempt to cast spell
    if spell.cast(defn.player) == 'cancelled':
        return 'cancelled'

def book(parameters):
    #book for now teaches you how to cast a spell.
    spell = sdic.get_spell(parameters['spell'])
    if len(defn.spellbook)<26:
        for known_spell in defn.spellbook:
            if known_spell.name == spell.name:
                gui.message('You already know how to cast' + spell.name + '!', libtcod.white)
                return 'cancelled'    
        defn.spellbook.append(spell)
        gui.message('After careful study, you learn how to cast ' + spell.name + '!' , libtcod.white)
    else:
        #long run, allow players to forget spells. Also, Mordok's tome to add extra capacity of 13 spells.
        gui.message('Unfortunately, your spellbook is full.', libtcod.white)
        return 'cancelled'

def get_item(name, x, y):
    arg = item_dict[name]
    item_component = obcl.Item(arg['function'], arg['parameters'])
    item = obcl.Object(x, y, arg['character'], arg['name'], arg['color'], description=arg['description'],
        item=item_component)
    return item

item_dict = {}

item_dict['healing potion'] = {
    'name' : 'healing potion',
    'character' : '!',
    'spawn chance' : 100,
    'color' : libtcod.blue,
    'function' : cast_heal,
    'parameters' : {
        'amount healed' : 5},
    'description' : 'Mmm, healthy'}

#iterate over spells in the spell dictionary to create a scroll for every spell
for spell in sdic.spell_dict: 
    item_dict['scroll of ' + sdic.spell_dict[spell]['name']] = {
        'name' : 'scroll of ' + sdic.spell_dict[spell]['name'],
        'character' : '#',
        'spawn chance' : 100 / sdic.spell_dict[spell]['level'][0][1],  #will need to think about this part of the function
        'color' : libtcod.lightest_yellow,
        'function' : scroll,
        'parameters' : {
            'spell' : sdic.spell_dict[spell]['name']},
        'description' : 'Magic bound to words on paper, ready to be released when read. Good for one use only.'}

for spell in sdic.spell_dict: 
    item_dict['book of ' + sdic.spell_dict[spell]['name']] = {
        'name' : 'book of ' + sdic.spell_dict[spell]['name'],
        'character' : '#',
        'spawn chance' : 50/ sdic.spell_dict[spell]['level'][0][1],  #will need to think about this part of the function
        'color' : libtcod.lightest_green,
        'function' : book,
        'parameters' : {
            'spell' : sdic.spell_dict[spell]['name']},
        'description' : 'A detailed treatise on the workings of a single spell. By the time you finish reading it, casting that spell will be second nature to you.'}
