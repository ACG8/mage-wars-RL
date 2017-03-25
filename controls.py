import libtcodpy as libtcod
import definitions as defn
import gui
import dungeon_generator as dgen
import attack_dictionary as adic
import spell_functions as spfn
import game
import data_methods as data
import dijkstra as djks
import item_dictionary as idic
import map_populator as mpop

def inventory_menu(header):
    #show a menu with each item of the inventory as an option
    if len(defn.inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = []
        for item in defn.inventory:
            text = item.properties['graphic'] + ' ' + item.properties['name']
            #show additional information, in case it's equipped
            if item.equipment and item.equipment.is_equipped:
                text = text + ' (on ' + item.equipment.slot + ')'
            options.append(text)
 
    index = gui.menu(header, options, defn.INVENTORY_WIDTH)

    #if an item was chosen, return it
    if index is None or len(defn.inventory) == 0: return None
    return defn.inventory[index].item

def summoning_menu(header):
    #show a menu with each creature as an option
    if len(defn.inventory) == 0:
        options = ['No allies to summon.']
    else:
        options = []
        for obj in defn.player.creatures:
            text = obj.title
            #show additional information, in case it's equipped
            options.append(text)
 
    index = gui.menu(header, options, defn.INVENTORY_WIDTH)

    #if an item was chosen, return it
    if index is None or len(defn.player.creatures) == 0: return None
    return defn.player.creatures[index]

def spellbook_menu(header):
    spellbook = defn.player.spellbook
    contents = spellbook.contents
    #will implement cantrips later.
    #show a menu with each spell in memory as an option
    if len(contents) == 0:
        options = ['You don\'t know any spells.']
    else:
        options = []
        #show spell names and mana costs. Indent properly so that all spells are aligned.
        for entry in contents:
            quantity = entry[1]
            spell = entry[0]
            
            if quantity == 'infinite':
                text = '   ' + spell.name.capitalize() + ' (' + str(spell.cost) + ')'
            elif spellbook.get_quantity(spell) < 10:
                text = str(quantity) + '  ' + spell.name.capitalize() + ' (' + str(spell.cost) + ')'
            elif spellbook.get_quantity(spell) < 100:
                text = str(quantity) + ' ' + spell.name.capitalize() + ' (' + str(spell.cost) + ')'
            options.append(text)
 
    index = gui.menu(header, options, defn.SPELLBOOK_WIDTH)
    

    #if a spell was chosen, return it
    if index is None or len(contents) == 0: return None
    if spellbook.get_quantity(spellbook.get_item_at_position(index)) == 0 : return None
    return spellbook.get_item_at_position(index)

def handle_keys():
    #global keys

    if defn.key.vk == libtcod.KEY_ENTER and defn.key.lalt:
        #Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
 
    elif defn.key.vk == libtcod.KEY_ESCAPE:
        return 'exit'  #exit game
    
    if defn.game_state == 'playing':

        #autoplay module
        if defn.autoplaying != None:
            #if any hostile monsters are in view, stop autoplaying:
            for obj in defn.objects:
                if obj.creature and obj.creature.alignment != 'player' and libtcod.map_is_in_fov(defn.fov_map, obj.x, obj.y):
                    gui.message ('Seeing enemies, you decide to pay a bit more attention to what you are doing.', libtcod.white)
                    defn.autoplaying = None
                    break
                    
            #Move.

            if defn.autoplaying == 'autoexplore':
                    
                    #first check if standing on an item. If so, pick it up.
                for obj in defn.dungeon[defn.player.x][defn.player.y].objects:  #look for an item in the player's tile
                    if obj.item and len(defn.inventory) < 26:
                        #we have an error where a full inventory will cause the player to remain on the same spot, continually trying to pick up the item.
                        if obj.item.pick_up() == 'cancelled':
                            defn.autoplaying == None
                        return
                    #compute fog of war (FOW) dijkstra map
                unexplored_tiles = []
                for y in range(defn.MAP_HEIGHT):
                    for x in range(defn.MAP_WIDTH):
                        if not defn.dungeon[x][y].explored:
                            unexplored_tiles.append(defn.dungeon[x][y])
                    #if inventory is not full, compute item map
                item_tiles = []
                if len(defn.inventory) < 26:
                    for obj in defn.objects:
                        if obj.item and defn.dungeon[obj.x][obj.y].explored:
                            item_tiles.append(defn.dungeon[obj.x][obj.y])

                    #check whether any target squares were found
                dijkstra_autoexplore_map = djks.Map(unexplored_tiles + item_tiles)
                dijkstra_autoexplore_map.compute_map()
                    #if there is a next point, move there, otherwise cancel autoplay:
                if dijkstra_autoexplore_map.array[defn.player.x][defn.player.y] < 999:
                    destination = dijkstra_autoexplore_map.get_next_step(defn.player.x,defn.player.y)
                    defn.player.creature.try_to_move(destination.x,destination.y)
                    return
                else:
                        #cancel autoplay; we're done
                    defn.autoplaying = None
            elif defn.autoplaying == 'autoascend':

                #go up if standing on the portal
                if defn.stairs.x == defn.player.x and defn.stairs.y == defn.player.y:
                    dgen.next_level()
                    defn.autoplaying = None
                    return
                    #see if the portal is visible:
                portals = []
                for y in range(defn.MAP_HEIGHT):
                    for x in range(defn.MAP_WIDTH):
                        if defn.stairs in defn.dungeon[x][y].objects and defn.dungeon[x][y].explored:
                            portals.append(defn.dungeon[x][y])
                if portals:
                    dijkstra_autoascend_map = djks.Map(portals)
                    dijkstra_autoascend_map.compute_map()
                    destination = dijkstra_autoascend_map.get_next_step(defn.player.x,defn.player.y)
                    defn.player.creature.try_to_move(destination.x,destination.y)
                    return
                        #cancel autoplay; we're done
                    defn.autoplaying = None
                else:
                    #no portals found; cancel autoplay
                    gui.message ('You have no idea where the nearest portal is.', libtcod.white)
                    defn.autoplaying = None
                    
            else:
                #stop autoexploring when a key is pressed.
                defn.autoplaying = None

        #autofight with tab
        if defn.key.vk==libtcod.KEY_TAB:
            enemy_tiles = []
            for obj in defn.objects:
                if obj.creature and obj.creature.alignment != 'player' and libtcod.map_is_in_fov(defn.fov_map, obj.x, obj.y):
                    enemy_tiles.append(defn.dungeon[obj.x][obj.y])
            if enemy_tiles:
                #create dijkstra map and roll towards nearest enemy.
                dijkstra_autofight_map = djks.Map(enemy_tiles)
                dijkstra_autofight_map.compute_map()
                destination = dijkstra_autofight_map.get_next_step(defn.player.x,defn.player.y)
                defn.player.creature.try_to_move(destination.x,destination.y)
                return
            else:
                gui.message ('No enemies in sight!', libtcod.white)

        #cancel autoplay if any key is pressed

        if defn.key.vk != libtcod.KEY_NONE:
            defn.autoplaying = None
        
        #movement keys
        
        try:
            (dx0,dx1) = {libtcod.KEY_KP1 : (-1,1),
                         libtcod.KEY_KP2 : (0,1),
                         libtcod.KEY_KP3 : (1,1),
                         libtcod.KEY_KP4 : (-1,0),
                         libtcod.KEY_KP6 : (1,0),
                         libtcod.KEY_KP7 : (-1,-1),
                         libtcod.KEY_KP8 : (0,-1),
                         libtcod.KEY_KP9 : (1,-1)
                         }[defn.key.vk]
            player_move_or_attack(dx0,dx1)
        except:
            
            if defn.key.vk==libtcod.KEY_KP5:
                return

            key_char = chr(defn.key.c)
 
            if key_char == ',':
                #pick up an item
                for obj in defn.dungeon[defn.player.x][defn.player.y].objects:  #look for an item in the player's tile
                    if obj.item:
                        obj.item.pick_up()
                        return

            if key_char == '?':
                gui.msgbox('Use the numpad keys to move around. You can mouse-over any object to identify it. The following keys can be used to get more information:' +

                           '\n\nI = examine an item in your inventory' +
                           '\nZ = examine a spell in your spellbook' +
                           '\nc = access information about your character' +
                           '\nx = get information on a nearby object' +

                           '\n\nThe following keys may be used to interact with your environment:' +
                           
                           '\n\nCOMMA = pick up item from current position' +
                           '\ni = use an item from your inventory'+
                           '\nd = drop an item from your inventory' +
                           '\nz = choose a spell from your spellbook to cast' +
                           '\ns = summon an ally from a previous level' +
                           
                           '\n\nTo avoid tedious repetition, you can automate certain tasks:' +
                           '\n\n< = travel to the nearest portal and pass through' +
                           '\no = autoexplore (press any key to stop exploring)' +
                           '\nTAB = move towards/attack nearest enemy' +
                           '\n\nYour objective on each level is to find the exit and ascend to the next level. Enemies will get more dangerous the further you go, so it will be to your advantage to pick up equipment that you find lying around.'
                           ,50)

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
                spellbook = defn.player.spellbook
                #show the spellbook; if a spell is selected, use it
                chosen_spell = spellbook_menu('Press the key next to a spell to cast it, or any other to cancel.\n')
                if chosen_spell is not None:
                    if defn.player.creature.cast_spell(chosen_spell) != 'cancelled':
                        spellbook.remove(chosen_spell, 1)
                    return

            if key_char == 'Z':
                #show the inventory; if an item is selected, describe it
                chosen_spell = spellbook_menu('Press the key next to a spell for more information, or any other to cancel.\n')
                if chosen_spell is not None:
                    chosen_spell.describe()

            if key_char == 'd':
                #show the inventory; if an item is selected, drop it
                chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.drop()
                    chosen_item.owner.send_to_back()
                    return
                
                chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.drop()
                    return

            if key_char == '<':
                #go up if standing on the portal
                if defn.stairs.x == defn.player.x and defn.stairs.y == defn.player.y:
                    dgen.next_level()
                    defn.autoplaying = None
                #head toward portal and then blank input key in preparation for override.
                defn.autoplaying = 'autoascend'
                defn.key.vk = libtcod.KEY_NONE

            if key_char == 'o':
                #initialize autoexplore and then blank input key in preparation for override.
                defn.autoplaying = 'autoexplore'
                defn.key.vk = libtcod.KEY_NONE

            if key_char == 'c':
                #show character information
                #first, compute traits
                traits_inc = []
                appended_traits = []
                for trait in defn.player.traits:
                    if trait[0] not in appended_traits:
                        if len(trait) == 2:
                            if trait[0][-1:]=='+': #sum them
                                trait_inc = [trait[0], data.sum_values_from_list(defn.player.traits,trait[0])]
                            else: #find max
                                trait_inc = [trait[0], data.max_value_from_list(defn.player.traits,trait[0])]
                            traits_inc.append(trait_inc)
                            appended_traits.append(trait_inc[0])
                        else:
                            traits_inc.append(trait)
                            appended_traits.append(trait)
                traits = ''
                
                for trait in traits_inc:
                    if len(trait) == 1:
                        traits += '\n   ' + trait[0].capitalize()
                    else:
                        traits += '\n   ' + trait[0].capitalize() + str(trait[1])

                #next, compute conditions

                conditions_inc = []
                appended_conditions = []
                for condition in defn.player.creature.conditions:
                    if condition not in appended_conditions:
                        conditions_inc.append([condition,data.count_instances_in_list(defn.player.creature.conditions,condition)])
                        appended_conditions.append(condition)

                conditions = ''

                for condition in conditions_inc:
                    conditions += '\n   ' + condition[0].capitalize() + ' (' + str(condition[1]) + ')'
                        
                
                level_up_xp = defn.LEVEL_UP_BASE + defn.player.properties['level'] * defn.LEVEL_UP_FACTOR
                gui.msgbox('Character Information\n\nLevel: ' + str(defn.player.properties['level']) +
                    '\nExperience: ' + str(defn.player.creature.xp) +
                    '\nExperience to level up: ' + str(level_up_xp) +
                    '\n\nLife: ' + str(defn.player.creature.max_hp) +
                    '\nMana Capacity: ' + str(defn.player.creature.max_mana) +
                    '\n\nAttack: ' + str(defn.player.creature.active_attack.name.capitalize()) +
                    '\n\nTraits:' + traits +
                    '\n\nConditions' + conditions
                    ,defn.CHARACTER_SCREEN_WIDTH)

            if key_char == 'x':
                #first, select a target object
                target = None
                gui.message('Click on the object you would like to know more about, or right click to cancel.', libtcod.white)
                rangemap = defn.fov_map
                while True:
                    #render the screen. this erases the inventory and shows the names of objects under the mouse.
                    libtcod.console_flush()
                    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,defn.key,defn.mouse)
                    game.render_all()
 
                    (x, y) = (defn.mouse.cx, defn.mouse.cy)
                    
                    if defn.mouse.lbutton_pressed and libtcod.map_is_in_fov(defn.fov_map, x, y):
                        for j in range(defn.MAP_HEIGHT):
                            for i in range(defn.MAP_WIDTH):
                                if libtcod.map_is_in_fov(rangemap, i, j):
                                    libtcod.console_set_char_background(defn.con, i, j, defn.dungeon[i][j].color, libtcod.BKGND_SET)
                        break
                    
                    if defn.mouse.rbutton_pressed or defn.key.vk == libtcod.KEY_ESCAPE:
                        for j in range(defn.MAP_HEIGHT):
                            for i in range(defn.MAP_WIDTH):
                                if libtcod.map_is_in_fov(rangemap, i, j):
                                    libtcod.console_set_char_background(defn.con, i, j, defn.dungeon[i][j].color, libtcod.BKGND_SET)
                        break
                if x != None:
                    for obj in defn.dungeon[x][y].objects:
                        target = obj
                        #describe the target more fully if it is a creature
                        if target.creature:
                            traits_inc = []
                            appended_traits = []
                            for trait in target.traits:
                                if trait[0] not in appended_traits:
                                    if len(trait) == 2:
                                        if trait[0][-1:]=='+': #sum them
                                            trait_inc = [trait[0], data.sum_values_from_list(target.traits,trait[0])]
                                        else: #find max
                                            trait_inc = [trait[0], data.max_value_from_list(target.traits,trait[0])]
                                        traits_inc.append(trait_inc)
                                        appended_traits.append(trait_inc[0])
                                    else:
                                        traits_inc.append(trait)
                                        appended_traits.append(trait)
                            traits = ''
                            
                            for trait in traits_inc:
                                if len(trait) == 1:
                                    traits += '\n   ' + trait[0].capitalize()
                                else:
                                    traits += '\n   ' + trait[0].capitalize() + str(trait[1])

                            #next, compute conditions

                            conditions_inc = []
                            appended_conditions = []
                            for condition in target.creature.conditions:
                                if condition not in appended_conditions:
                                    conditions_inc.append([condition,data.count_instances_in_list(target.creature.conditions,condition)])
                                    appended_conditions.append(condition)

                            conditions = ''

                            for condition in conditions_inc:
                                conditions += '\n   ' + condition[0].capitalize() + ' (' + str(condition[1]) + ')'

                            title = target.title.capitalize()
                            if target.title == target.name:
                                title = title + ', ' + target.properties['name']
                            #now describe the creature
                            gui.msgbox(title +
                            '\n\nLevel: ' + str(target.properties['level']) +
                            '\n\nAttack: ' + str(target.creature.active_attack.name.capitalize()) +
                            '\n\nTraits:' + traits +
                            '\n\nConditions:' + conditions +
                            '\n\n' + target.properties['description']
                            ,defn.CHARACTER_SCREEN_WIDTH)
                                        
                        else:
                            target.describe()
                        break
                        
                        #later, can add menu in case of multiple objects
            if key_char == 's':
                #summon an ally
                creature = summoning_menu('Press the key next to a creature to select it, or any other to cancel.\n')
                if creature != None:
                    gui.message('Left-click on an open tile to summon creature there, or right-click to cancel.', libtcod.light_cyan)
                    x0,x1 = spfn.target_tile(3)
                    if mpop.place_object(creature,[x0,x1]) != 'failed':
                        defn.player.creatures.remove(creature)
                    else:
                        gui.message('There\'s something in the way...', libtcod.light_cyan)
                    
                    
                
                        

            #if key_char == 'w':
                #defn.player.creature.heal(30)
                #dgen.next_level()
                #defn.inventory.append(idic.get_item('scroll of animate dead',0,0))
                #defn.inventory.append(idic.get_item('scroll of heal',0,0))
                #defn.inventory.append(idic.get_item('scroll of minor heal',0,0))
                
            return 'didnt-take-turn'

def player_move_or_attack(dx, dy):
 
    #the coordinates the player is moving to/attacking
    x = defn.player.x + dx
    y = defn.player.y + dy

    defn.player.creature.try_to_move(x,y)
