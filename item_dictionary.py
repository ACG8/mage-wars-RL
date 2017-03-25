import map_functions as mpfn
import object_classes as obcl
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
    #a scroll will allow you to cast its spell (even if un/antitrained!) for free.

    spell = sdic.get_spell(parameters['spell'])
    if spell.cast(defn.player) != 'cancelled':
        return 'succeeded'
    else:
        return 'cancelled'

def book(parameters):

    spellbook = defn.player.spellbook

    #lets you learn 1-6 copies of spell, depending on training and level.
    level_copies = [4,2,1,1,0,0]

    #this is not actually the spell instance that will go in your book - it is just a placeholder to find the properties
    spell = parameters['spell']

    if spell.properties['school'] in defn.antitraining:
        level_copies = [2,1,0,0,0,0]
    if spell.properties['school'] in defn.training:
        level_copies = [6,4,2,2,1,1]

    if level_copies[spell.properties['level']-1] == 0:
        gui.message('Unfortunately, you are not skilled enough in the ' + spell.properties['school'] + ' school of magic to learn anything from this book.', libtcod.yellow)
        return 'cancelled'

    copies = level_copies[spell.properties['level']-1]
    
    if len(spellbook.contents)<26:
        spellbook.insert(spell, copies)
        gui.message('As you memorize the spells contained in the tome, it crumbles to dust.', libtcod.green)
        return 'succeeded'
    else:
        gui.message('Your spellbook is full.', libtcod.white)
        return 'cancelled'

def get_item(name, x, y):
    arg = item_dict[name]
    item_component = obcl.Item(arg['function'], arg['parameters'].copy())
    item = obcl.Object(x, y,
        item=item_component, properties = arg['properties'].copy())
    return item

item_dict = {}

item_dict['healing potion'] = {
    'spawn chance' : [{'level' : 1, 'value' : 100}],
    'function' : cast_heal,
    'parameters' : {
        'amount healed' : 5},
    'properties' : {
        'name' : 'healing potion',
        'graphic' : '!',
        'color' : libtcod.blue,
        'description' : 'Heals 5 damage from drinker'}}

#iterate over spells in the spell dictionary to create a scroll for every spell
for spell in sdic.spell_dict: 
    item_dict['scroll of ' + sdic.spell_dict[spell]['name']] = {
        
        
        'spawn chance' : [{'level' : 1, 'value' : 100 / sdic.spell_dict[spell]['level'][0][1]}],  #will need to think about this part of the function
        'function' : scroll,
        'parameters' : {
            'spell' : sdic.spell_dict[spell]},
        'properties' : {
            'name' : 'scroll of ' + sdic.spell_dict[spell]['name'],
            'graphic' : '#',
            'color' : libtcod.lightest_yellow,
            'description' : 'Magic bound to words on paper, ready to be released when read. Good for one use only.\n\n'
            + sdic.spell_dict[spell]['properties']['description']}}
