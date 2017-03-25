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
        arg = sdic.spell_dict[parameters['spell']]
        #looks at the string after the 10th character of the scroll's name to determine effect
        spell = sdic.Spell(name = arg['name'], base_cost = 0, function = arg['function'], parameters = arg['parameters'])
        if spell.cast(defn.player) == 'cancelled':
            return 'cancelled'
        #learn spell if casting succeeded
        for your_spell in defn.spellbook:
            if spell.name == your_spell.name:
                your_spell.learn(1)
                gui.message('You got better at casting ' + spell.name + '!', libtcod.white)
                return
        if len(defn.spellbook)<26:
            spell.base_cost = arg['base cost']
            spell.cost = arg['base cost'] * 3
            defn.spellbook.append(spell)
            gui.message('You learned how to cast ' + spell.name + '!' , libtcod.white)
        else:
            #long run, allow players to forget spells. Also, Mordok's tome to add extra capacity of 13 spells.
            gui.message('Unfortunately, your spellbook is full.', libtcod.white)

def create_item(name, x, y):
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
        'spawn chance' : 100 / sdic.spell_dict[spell]['level'],  #will need to think about this part of the function
        'color' : libtcod.lightest_yellow,
        'function' : scroll,
        'parameters' : {
            'spell' : sdic.spell_dict[spell]['name']},
        'description' : 'ow'}


