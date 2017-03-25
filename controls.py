import libtcodpy as libtcod
import definitions as defn
import inventory_functions as infn
import gui
import dungeon_generator as dgen

def inventory_menu(header):
    #show a menu with each item of the inventory as an option
    if len(defn.inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = []
        for item in defn.inventory:
            text = item.name
            #show additional information, in case it's equipped
            if item.equipment and item.equipment.is_equipped:
                text = text + ' (on ' + item.equipment.slot + ')'
            options.append(text)
 
    index = gui.menu(header, options, defn.INVENTORY_WIDTH)

    #if an item was chosen, return it
    if index is None or len(defn.inventory) == 0: return None
    return defn.inventory[index].item

def spellbook_menu(header):
    #show a menu with each spell in memory as an option
    if len(defn.spellbook) == 0:
        options = ['You don\'t know any spells.']
    else:
        options = []
        for spell in defn.spellbook:
            text = spell.name
            options.append(text)
 
    index = gui.menu(header, options, defn.SPELLBOOK_WIDTH)

    #if an item was chosen, return it
    if index is None or len(defn.spellbook) == 0: return None
    return defn.spellbook[index]

def handle_keys():
    global keys
 
    #key = libtcod.console_check_for_keypress()  #real-time
    #key = libtcod.console_wait_for_keypress(True)  #turn-based
 
    if defn.key.vk == libtcod.KEY_ENTER and defn.key.lalt:
        #Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
 
    elif defn.key.vk == libtcod.KEY_ESCAPE:
        return 'exit'  #exit game
    
    if defn.game_state == 'playing':
        #movement keys
        if defn.key.vk==libtcod.KEY_KP8:
            player_move_or_attack(0, -1)
     
        elif defn.key.vk==libtcod.KEY_KP2:
            player_move_or_attack(0, 1)
     
        elif defn.key.vk==libtcod.KEY_KP4:
            player_move_or_attack(-1, 0)
     
        elif defn.key.vk==libtcod.KEY_KP6:
            player_move_or_attack(1, 0)

        elif defn.key.vk==libtcod.KEY_KP7:
            player_move_or_attack(-1, -1)
     
        elif defn.key.vk==libtcod.KEY_KP9:
            player_move_or_attack(1, -1)
     
        elif defn.key.vk==libtcod.KEY_KP1:
            player_move_or_attack(-1, 1)
     
        elif defn.key.vk==libtcod.KEY_KP3:
            player_move_or_attack(1, 1)

        elif defn.key.vk==libtcod.KEY_KP5:
            pass

        else:
            #test for other keys
            key_char = chr(defn.key.c)
 
            if key_char == ',':
                #pick up an item
                for object in defn.objects:  #look for an item in the player's tile
                    if object.x == defn.player.x and object.y == defn.player.y and object.item:
                        object.item.pick_up()
                        break

            if key_char == 'i':
                #show the inventory; if an item is selected, use it
                chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.use()

            if key_char == 'z':
                #show the spellbook; if a spell is selected, use it
                chosen_spell = spellbook_menu('Press the key next to a spell to cast it, or any other to cancel.\n')
                if chosen_spell is not None:
                    chosen_spell.use()

            if key_char == 'd':
                #show the inventory; if an item is selected, drop it
                chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.drop()

            if key_char == '<':
                #go up stairs, if the player is on them
                if defn.stairs.x == defn.player.x and defn.stairs.y == defn.player.y:
                    dgen.next_level()

            if key_char == 'c':
                #show character information
                level_up_xp = defn.LEVEL_UP_BASE + defn.player.level * defn.LEVEL_UP_FACTOR
                gui.msgbox('Character Information\n\nLevel: ' + str(defn.player.level) +
                    '\nExperience: ' + str(defn.player.creature.xp) +
                    '\nExperience to level up: ' + str(level_up_xp) +
                    '\n\nLife: ' + str(defn.player.creature.max_hp) +
                    '\n\nMana Capacity: ' + str(defn.player.creature.max_mana) +
                    '\nMelee Attack: ' + str(defn.player.creature.power) +
                    '\nArmor: ' + str(defn.player.creature.armor)
                    ,defn.CHARACTER_SCREEN_WIDTH)

            return 'didnt-take-turn'

def player_move_or_attack(dx, dy):
 
    #the coordinates the player is moving to/attacking
    x = defn.player.x + dx
    y = defn.player.y + dy
 
    #try to find an attackable object there
    target = None
    for object in defn.objects:
        if object.creature and object.x == x and object.y == y and object != defn.player:
            target = object
            break
 
    #attack if target found, move otherwise
    if target is not None:
        defn.player.creature.attack(target)
    else:
        defn.player.move(dx, dy)
        defn.fov_recompute = True
