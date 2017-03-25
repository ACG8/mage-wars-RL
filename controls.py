import libtcodpy as libtcod
import definitions as defn
import inventory_functions as infn
import gui
import dungeon_generator as dgen
import action_classes as accl
import attack_dictionary as adic
import spell_functions as spfn
import spell_classes as spcl
import game

def inventory_menu(header):
    #show a menu with each item of the inventory as an option
    if len(defn.inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = []
        for item in defn.inventory:
            text = item.char + ' ' + item.name
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
        #show spell names and mana costs
        for spell in defn.spellbook:
            text = str(spell.name) + ' (' + str(spell.cost) + ')'
            options.append(text)
 
    index = gui.menu(header, options, defn.SPELLBOOK_WIDTH)

    #if a spell was chosen, return it
    if index is None or len(defn.spellbook) == 0: return None
    return defn.spellbook[index]

def handle_keys():
    #global keys
 
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
                        return

            if key_char == 'i':
                #show the inventory; if an item is selected, use it
                chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
                if chosen_item is not None:
                    if chosen_item.use() != 'cancelled':
                        return

            if key_char == 'I':
                #show the inventory; if an item is selected, describe it
                chosen_item = inventory_menu('Press the key next to an item to examine it, or any other to cancel.\n')
                if chosen_item is not None:
                    info = chosen_item.owner
                    info.describe()

            if key_char == 'z':
                #show the spellbook; if a spell is selected, use it
                chosen_spell = spellbook_menu('Press the key next to a spell to cast it, or any other to cancel.\n')
                if chosen_spell is not None:
                    chosen_spell.cast(defn.player)
                    return

            if key_char == 'd':
                #show the inventory; if an item is selected, drop it
                chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.drop()
                    return

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
                    '\nAttack: ' + str(defn.player.creature.active_attack.name.capitalize()) +
                    #'\nTraits: ' + str(defn.player.traits) + #; we'll leave this for a future date.
                    '\nArmor: ' + str(defn.player.creature.armor)
                    ,defn.CHARACTER_SCREEN_WIDTH)

            if key_char == 'w':
                defn.player.creature.heal(30)
                
            return 'didnt-take-turn'

def player_move_or_attack(dx, dy):
 
    #the coordinates the player is moving to/attacking
    x = defn.player.x + dx
    y = defn.player.y + dy

    defn.player.creature.try_to_move(x,y)
 
    #try to find an attackable object there
#    target = None
 #   for obj in defn.objects:
  #      if obj.creature and obj.x == x and obj.y == y and obj != defn.player:
   #         target = obj
    #        break
 
#    #attack if target found, move otherwise
 #   if target:
  #      defn.player.creature.attack(target, defn.player.creature.active_attack)
   #     defn.player.creature.adjust_turn_counter(3)
    #else:
     #   defn.player.move(dx, dy)
      #  defn.fov_recompute = True
       # defn.player_location_changed = True
        #defn.player.creature.adjust_turn_counter(3)
