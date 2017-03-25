import definitions as defn
import libtcodpy as libtcod
import object_classes as obcl
import map_functions as mpfn
import inventory_functions as infn
import math
import textwrap
import shelve
import random
import gui
import controls as ctrl
import dungeon_generator as dgen
import spell_functions as spfn
import title_screen as tit
import dijkstra as djks

def render_objects():
    #need to fix so that corpses,items,monsters,player are drawn in that order
    for obj in defn.objects:
        if obj != defn.player and (obj.always_visible or libtcod.map_is_in_fov(defn.fov_map, obj.x, obj.y)) :
            obj.draw()
    #player is always rendered last
    defn.player.draw()

def render_all():

    if defn.fov_recompute:
        #recompute FOV if needed (the player moved or something)
        defn.fov_recompute = False
        libtcod.map_compute_fov(defn.fov_map, defn.player.x, defn.player.y, defn.TORCH_RADIUS, defn.FOV_LIGHT_WALLS, defn.FOV_ALGO)

        #go through all tiles, and set their background color according to the FOV
        defn.visible_tiles = []
        for y in range(defn.MAP_HEIGHT):
            for x in range(defn.MAP_WIDTH):
                #is it visible?
                if not libtcod.map_is_in_fov(defn.fov_map, x, y):
                    defn.visible_tiles.append(defn.dungeon[x][y])
                    #if it's not visible right now, the player can only see it if it's explored
                    if defn.dungeon[x][y].explored:
                    #it's out of the player's FOV
                        libtcod.console_set_char_background(defn.con, x, y, defn.dungeon[x][y].color*libtcod.grey, libtcod.BKGND_SET)
                else:
                    libtcod.console_set_char_background(defn.con, x, y, defn.dungeon[x][y].color, libtcod.BKGND_SET)
                    #it's visible
                    defn.dungeon[x][y].explored = True
                    if defn.dungeon[x][y] in defn.unexplored_tiles:
                        defn.unexplored_tiles.remove(defn.dungeon[x][y])
    
    #compute FOV dijkstra map
        #visible tiles is wrong - the list is of invisible tiles
            #rather than putting this in render loop, let's only do this when things change.
    defn.dijkstra_fov_map = djks.Map(defn.visible_tiles)
    defn.dijkstra_fov_map.compute_map()
    
    render_objects()

    libtcod.console_blit(defn.con, 0, 0, defn.MAP_WIDTH, defn.MAP_HEIGHT, 0, 0, 0)
    
    #prepare to render the GUI panel
    libtcod.console_set_default_background(defn.stats_panel, libtcod.black)
    libtcod.console_set_default_background(defn.message_panel, libtcod.black)
    libtcod.console_clear(defn.stats_panel)
    libtcod.console_clear(defn.message_panel)

    #print the game messages, one line at a time
    y = 0
    for (line, color) in defn.game_msgs:
        libtcod.console_set_default_foreground(defn.message_panel, color)
        libtcod.console_print_ex(defn.message_panel, defn.MSG_X+1, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1
 
    #show the player's stats
    gui.render_bar(1, 2, defn.BAR_WIDTH, 'Life', defn.player.creature.hp, defn.player.creature.max_hp,
        libtcod.dark_red, libtcod.darkest_red)

    gui.render_bar(1, 4, defn.BAR_WIDTH, 'Mana', defn.player.creature.mana, defn.player.creature.max_mana,
        libtcod.dark_violet, libtcod.darkest_violet)

    #long term, divide message panel again to make room for a monster stats box
    #display names of objects under the mouse
    libtcod.console_print_ex(defn.stats_panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, defn.player.name.capitalize() + ', ' + defn.player.properties['name'].capitalize())
    libtcod.console_set_default_foreground(defn.stats_panel, libtcod.light_gray)
    libtcod.console_print_ex(defn.stats_panel, 1, 6, libtcod.BKGND_NONE, libtcod.LEFT, gui.get_names_under_mouse())
 
    #blit the panels to the root console 0
    libtcod.console_blit(defn.message_panel, 0, 0, defn.MSG_WIDTH, defn.MSG_HEIGHT, 0, defn.MSG_X, defn.MSG_Y)
    libtcod.console_blit(defn.stats_panel, 0, 0, defn.STATS_WIDTH, defn.STATS_HEIGHT, 0, defn.STATS_X, defn.STATS_Y)

def play_game():

    player_action = None
 
    while not libtcod.console_is_window_closed():
        #render the screen
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,defn.key,defn.mouse)

        libtcod.console_flush()

        #upkeep phase
        check_level_up()
        #don't use adjust turn counter here, since that also triggers the upkeep function
        defn.player.creature.turn_counter = max(defn.player.creature.turn_counter - 1,0)
 
        #if it is the player's turn, handle keys and exit game if needed
        if defn.player.creature.turn_counter == 0:
            defn.player.clear()
            #reset defenses
            if defn.player.creature.defenses:
                for defense in defn.player.creature.defenses:
                    if defense:
                        defense.reset()
            player_action = ctrl.handle_keys()
            #defn.dungeon[defn.player.x][defn.player.y].scent+=100
            render_all()
            if player_action == 'exit':
                tit.save_game()
                break
        #for now, we recompute the player's djkstra map here.
        if defn.player_location_changed:
            defn.dijkstra_player_map = djks.Map([defn.player])
            defn.dijkstra_player_map.compute_map()
            defn.player_location_changed = False

        #let monsters take their turn
        monsters = []
        for obj in defn.objects:
            if obj.creature and obj.ai and obj.creature.alignment != 'player':
                monsters.append(obj)

        defn.dijkstra_monster_map = djks.Map(monsters)
        defn.dijkstra_monster_map.compute_map()
        
        if defn.game_state == 'playing' and player_action != 'didnt-take-turn':
            for obj in defn.objects:
                obj.clear()
                if obj.ai:
                    if obj.creature.defenses:
                        for defense in obj.creature.defenses:
                            if defense:
                                defense.reset()
                    #adjust turn counter before moving.
                    obj.creature.turn_counter = max(obj.creature.turn_counter - 1, 0)
                    if obj.creature.turn_counter == 0:
                        obj.ai.take_turn()
                    
def check_level_up():
    #see if the player's experience is enough to level-up
    level_up_xp = defn.LEVEL_UP_BASE + defn.player.properties['level'] * defn.LEVEL_UP_FACTOR
    if defn.player.creature.xp >= level_up_xp:
        #it is! level up
        defn.player.properties['level'] += 1
        defn.player.creature.xp -= level_up_xp
        gui.message('You reached level ' + str(defn.player.properties['level']) + '!', libtcod.yellow)
        choice = None
        while choice == None:  #keep asking until a choice is made
            choice = gui.menu('Level up! Choose a stat to raise:\n',
                ['+4 Life, from ' + str(defn.player.creature.base_max_hp),
                '+5 Mana Capacity, from ' + str(defn.player.creature.base_max_mana),
                '+1 Channeling, from ' + str(defn.player.creature.channeling)
                ], defn.LEVEL_SCREEN_WIDTH)
 
        if choice == 0:
            defn.player.creature.base_max_hp += 4
            defn.player.creature.hp += 4

        elif choice == 1:
            defn.player.creature.base_max_mana += 5
            defn.player.creature.mana +=5

        elif choice == 2:
            defn.player.creature.channeling += 1
