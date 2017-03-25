import definitions as defn
import libtcodpy as libtcod
import object_classes as obcl
import map_functions as mpfn
import inventory_functions as infn
import gui
import attack_dictionary as adic
import action_classes as accl
import game
import spell_classes as spcl
import spell_dictionary as sdic
import time

def cast_fireball(name):
    #ask the player for a target tile to throw a fireball at
    gui.message('Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan)
    (x, y) = target_tile()
    if x is None: return 'cancelled'
    gui.message('The fireball explodes, burning everything within ' + str(defn.FIREBALL_RADIUS) + ' tiles!', libtcod.orange)
 
    for obj in defn.objects:  #damage every fighter in range, including the player
        if obj.distance(x, y) <= defn.FIREBALL_RADIUS and obj.creature:
            gui.message('The ' + obj.name + ' gets burned for ' + str(defn.FIREBALL_DAMAGE) + ' hit points.', libtcod.orange)
            obj.creature.take_damage(defn.FIREBALL_DAMAGE)

def cast_heal(name):
    #heal the player
    if defn.player.creature.hp == defn.player.creature.max_hp:
        gui.message('You are already at full health.', libtcod.red)
        return 'cancelled'
 
    gui.message('Your wounds start to feel better!', libtcod.light_violet)
    defn.player.creature.heal(defn.HEAL_AMOUNT)

def cast_confuse(name):
    #ask the player for a target to confuse
    gui.message('Left-click an enemy to confuse it, or right-click to cancel.', libtcod.light_cyan)
    monster = target_monster(defn.CONFUSE_RANGE)
    if monster is None: return 'cancelled'
    #replace the monster's AI with a "confused" one; after some turns it will restore the old AI
    old_ai = monster.ai
    monster.ai = obcl.ConfusedMonster(old_ai)
    monster.ai.owner = monster  #tell the new component who owns it
    gui.message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', libtcod.light_green)

def cast_lightning(name):
    #find closest enemy (inside a maximum range) and damage it
    monster = closest_monster(defn.LIGHTNING_RANGE)
    if monster is None:  #no enemy found within maximum range
        gui.message('No enemy is close enough to strike.', libtcod.red)
        return 'cancelled'
 
    #zap it! note: player hardcoded as source, need to change
    attack_trait = adic.attk_dict['lightning bolt']
    attack = accl.Attack(attack_trait[0], attack_trait[1], attack_trait[2], attack_trait[3])
    attack.target_creature(defn.player, monster)

###may need to move these targeting functions
def target_monster(max_range=None):
    gui.message('Left-click on target, or right-click to cancel.', libtcod.light_cyan)
    #primitive function highlighting range. Ideally would be implemented in read-only attribute of tile

        
    rangemap = defn.fov_map
    libtcod.map_compute_fov(rangemap, defn.player.x, defn.player.y, max_range, defn.FOV_LIGHT_WALLS, defn.FOV_ALGO)
    for y in range(defn.MAP_HEIGHT):
        for x in range(defn.MAP_WIDTH):
            if libtcod.map_is_in_fov(rangemap, x, y):
                libtcod.console_set_char_background(defn.con, x, y, defn.dungeon[x][y].color * libtcod.lightest_green, libtcod.BKGND_SET)
    #returns a clicked monster inside FOV up to a range, or None if right-clicked
    while True:

    
        (x, y) = target_tile(max_range)
            
        if x is None:  #player cancelled
            #remove highlight
            for y in range(defn.MAP_HEIGHT):
                for x in range(defn.MAP_WIDTH):
                    if libtcod.map_is_in_fov(rangemap, x, y):
                        libtcod.console_set_char_background(defn.con, x, y, defn.dungeon[x][y].color, libtcod.BKGND_SET)
            return None
 
        #return the first clicked creature, otherwise continue looping
        for obj in defn.dungeon[x][y].objects:
            if obj.creature:
                #remove highlight
                for y in range(defn.MAP_HEIGHT):
                    for x in range(defn.MAP_WIDTH):
                        if libtcod.map_is_in_fov(rangemap, x, y):
                            libtcod.console_set_char_background(defn.con, x, y, defn.dungeon[x][y].color, libtcod.BKGND_SET)
                return obj

def target_tile(max_range=None):
    #return the position of a tile left-clicked in player's FOV (optionally in a range), or (None,None) if right-clicked.
    while True:
        #render the screen. this erases the inventory and shows the names of objects under the mouse.
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,defn.key,defn.mouse)
        game.render_all()
 
        (x, y) = (defn.mouse.cx, defn.mouse.cy)

        #accept the target if the player clicked in FOV, and in case a range is specified, if it's in that range
        if (defn.mouse.lbutton_pressed and libtcod.map_is_in_fov(defn.fov_map, x, y) and
            (max_range is None or defn.player.distance(x, y) <= max_range)):
            return (x, y)
        
        if defn.mouse.rbutton_pressed or defn.key.vk == libtcod.KEY_ESCAPE:
            return (None, None)  #cancel if the player right-clicked or pressed Escape

def closest_monster(max_range):
    #find closest enemy, up to a maximum range, and in the player's FOV
    closest_enemy = None
    closest_dist = max_range + 1  #start with (slightly more than) maximum range
 
    for obj in defn.objects:
        if obj.creature and not obj == defn.player and libtcod.map_is_in_fov(defn.fov_map, obj.x, obj.y):
            #calculate distance between this object and the player
            dist = defn.player.distance_to(obj)
            if dist < closest_dist:  #it's closer, so remember it
                closest_enemy = obj
                closest_dist = dist
    return closest_enemy
