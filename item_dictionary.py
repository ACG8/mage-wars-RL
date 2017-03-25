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

    #new spell system: scrolls can be read to attempt to learn the spell (success rate of 100% for trained spells, 50% for untrained, and 33% for antitrained)
    #wands (not books) allow you to cast the spell indefinitely, without learning it
    #spells in the spellbook are actually dictionaries, with the name of the spell and all copies of it.
    spell = sdic.get_spell(parameters['spell'])

    #if you are not trained in the spell, there is a chance that you may fail to learn it.
    #If your level is less than the level of the spell, there is a chance you will fail to learn it. (will implement this later)
    if spell.properties['school'] in defn.antitraining:
        if libtcod.random_get_int(0,1,100) > 33:
            gui.message('The scroll crumbles as you read it. Unfortunately, you failed to learn ' + spell.name + '.', libtcod.light_red)
            return 'failed'
    elif spell.properties['school'] not in defn.training:
        if libtcod.random_get_int(0,1,100) > 50:
            gui.message('The scroll crumbles as you read it. Unfortunately, you failed to learn ' + spell.name + '.', libtcod.light_red)
            return 'failed'
        
    if len(defn.spellbook)<26:
        for known_spell in defn.spellbook:
            if known_spell['name'] == spell.name:
                known_spell['copies'].append(spell)
                gui.message('As you memorize the scroll, it crumbles to dust.', libtcod.green)
                return 'succeeded'
        defn.spellbook.append({'name' : spell.name, 'copies' : [spell], 'reusable' : spell.properties['reusable']})
        gui.message('As you memorize the scroll, it crumbles to dust.', libtcod.green)
        return 'succeeded'
    else:
        gui.message('Your spellbook is full.', libtcod.white)
        return 'cancelled'

def book(parameters):
    #will change book into wand. Players can't learn spells anymore.
    return 'cancelled'

def get_item(name, x, y):
    arg = item_dict[name]
    item_component = obcl.Item(arg['function'], arg['parameters'].copy())
    item = obcl.Object(x, y,
        item=item_component, properties = arg['properties'].copy())
    return item

item_dict = {}

item_dict['healing potion'] = {
    'spawn chance' : 100,
    'function' : cast_heal,
    'parameters' : {
        'amount healed' : 5},
    'properties' : {
        'name' : 'healing potion',
        'graphic' : '!',
        'color' : libtcod.blue,
        'description' : 'Mmm, healthy'}}

#iterate over spells in the spell dictionary to create a scroll for every spell
for spell in sdic.spell_dict: 
    item_dict['scroll of ' + sdic.spell_dict[spell]['name']] = {
        
        
        'spawn chance' : 100 / sdic.spell_dict[spell]['level'][0][1],  #will need to think about this part of the function

        'function' : scroll,
        'parameters' : {
            'spell' : sdic.spell_dict[spell]},
        'properties' : {
            'name' : 'scroll of ' + sdic.spell_dict[spell]['name'],
            'graphic' : '#',
            'color' : libtcod.lightest_yellow,
            'description' : 'Magic bound to words on paper, ready to be released when read. Good for one use only.'}}

for spell in sdic.spell_dict: 
    item_dict['book of ' + sdic.spell_dict[spell]['name']] = {
        
        'spawn chance' : 0,#50/ sdic.spell_dict[spell]['level'][0][1],  #will need to think about this part of the function
        'function' : book,
        'parameters' : {
            'spell' : sdic.spell_dict[spell]},
        'properties' : {
            'name' : 'book of ' + sdic.spell_dict[spell]['name'],
            'graphic' : '#',
            'color' : libtcod.lightest_green,
            'description' : 'A detailed treatise on the workings of a single spell. By the time you finish reading it, casting that spell will be second nature to you.'}}
