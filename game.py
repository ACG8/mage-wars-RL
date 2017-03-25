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

def render_objects():
    
    for object in defn.objects:
        if object != defn.player:
            object.draw()
    #player is always rendered last
    defn.player.draw()

def render_all():

    if defn.fov_recompute:
        #recompute FOV if needed (the player moved or something)
        defn.fov_recompute = False
        libtcod.map_compute_fov(defn.fov_map, defn.player.x, defn.player.y, defn.TORCH_RADIUS, defn.FOV_LIGHT_WALLS, defn.FOV_ALGO)

        #go through all tiles, and set their background color according to the FOV
        for y in range(defn.MAP_HEIGHT):
            for x in range(defn.MAP_WIDTH):
                #is it visible?
                if not libtcod.map_is_in_fov(defn.fov_map, x, y):
                    #if it's not visible right now, the player can only see it if it's explored
                    if defn.dungeon[x][y].explored:
                    #it's out of the player's FOV
                        libtcod.console_set_char_background(defn.con, x, y, defn.dungeon[x][y].color*libtcod.grey, libtcod.BKGND_SET)
                else:
                    libtcod.console_set_char_background(defn.con, x, y, defn.dungeon[x][y].color, libtcod.BKGND_SET)
                    #it's visible
                    defn.dungeon[x][y].explored = True
                
    render_objects()

    libtcod.console_blit(defn.con, 0, 0, defn.MAP_WIDTH, defn.MAP_HEIGHT, 0, 0, 0)
    #prepare to render the GUI panel
    libtcod.console_set_default_background(defn.panel, libtcod.black)
    libtcod.console_clear(defn.panel)

    #print the game messages, one line at a time
    y = 1
    for (line, color) in defn.game_msgs:
        libtcod.console_set_default_foreground(defn.panel, color)
        libtcod.console_print_ex(defn.panel, defn.MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1
 
    #show the player's stats
    gui.render_bar(1, 1, defn.BAR_WIDTH, 'Life', defn.player.creature.hp, defn.player.creature.max_hp,
        libtcod.dark_red, libtcod.darkest_red)

    gui.render_bar(1, 3, defn.BAR_WIDTH, 'Mana', defn.player.creature.mana, defn.player.creature.max_mana,
        libtcod.dark_violet, libtcod.darkest_violet)

    #display names of objects under the mouse
    libtcod.console_set_default_foreground(defn.panel, libtcod.light_gray)
    libtcod.console_print_ex(defn.panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, gui.get_names_under_mouse())
 
    #blit the contents of "panel" to the root console
    libtcod.console_blit(defn.panel, 0, 0, defn.SCREEN_WIDTH, defn.PANEL_HEIGHT, 0, 0, defn.PANEL_Y)

def play_game():

    player_action = None
 
    while not libtcod.console_is_window_closed():
        #render the screen
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,defn.key,defn.mouse)
        #render_all() - why not only render when it is the player's turn?

        libtcod.console_flush()

        #upkeep phase
        check_level_up()

        #for object in defn.objects:
         #   object.clear()

        #scent decay
        for y in range(defn.MAP_HEIGHT):
            for x in range(defn.MAP_WIDTH):
                defn.dungeon[x][y].scent = max(defn.dungeon[x][y].scent-1,0)
 
        #if it is the player's turn, handle keys and exit game if needed
        if defn.player.creature.turn_counter == 0:
            defn.player.clear()
            player_action = ctrl.handle_keys()
            defn.dungeon[defn.player.x][defn.player.y].scent+=100
            render_all()
            if player_action == 'exit':
                tit.save_game()
                break
        #add scent to floor
        
        
        defn.player.creature.adjust_turn_counter(-1)

        #for object in defn.objects:
         #   object.clear()
 
        #let monsters take their turn
        if defn.game_state == 'playing' and player_action != 'didnt-take-turn':
            for obj in defn.objects:
                obj.clear()
                if obj.ai:
                    if obj.creature.turn_counter == 0:
                        obj.ai.take_turn()
                    obj.creature.adjust_turn_counter(-1)
                #obj.draw()
                    
def check_level_up():
    #see if the player's experience is enough to level-up
    level_up_xp = defn.LEVEL_UP_BASE + defn.player.level * defn.LEVEL_UP_FACTOR
    if defn.player.creature.xp >= level_up_xp:
        #it is! level up
        defn.player.level += 1
        defn.player.creature.xp -= level_up_xp
        gui.message('You reached level ' + str(defn.player.level) + '!', libtcod.yellow)
        choice = None
        while choice == None:  #keep asking until a choice is made
            choice = gui.menu('Level up! Choose a stat to raise:\n',
                ['+2 Life, from ' + str(defn.player.creature.base_max_hp),
                '+2 Mana Capacity, from ' + str(defn.player.creature.base_max_mana)
                ], defn.LEVEL_SCREEN_WIDTH)
 
        if choice == 0:
            defn.player.creature.base_max_hp += 2
            defn.player.creature.hp += 2

        elif choice == 1:
            defn.player.creature.base_max_mana += 2
