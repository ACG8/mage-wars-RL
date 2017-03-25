import definitions as defn
import libtcodpy as libtcod
import object_classes as obcl
import map_functions as mpfn
import inventory_functions as infn
import math
import random
import gui

def cast_fireball():
    #ask the player for a target tile to throw a fireball at
    gui.message('Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan)
    (x, y) = target_tile()
    if x is None: return 'cancelled'
    gui.message('The fireball explodes, burning everything within ' + str(defn.FIREBALL_RADIUS) + ' tiles!', libtcod.orange)
 
    for obj in defn.objects:  #damage every fighter in range, including the player
        if obj.distance(x, y) <= defn.FIREBALL_RADIUS and obj.creature:
            gui.message('The ' + obj.name + ' gets burned for ' + str(defn.FIREBALL_DAMAGE) + ' hit points.', libtcod.orange)
            obj.creature.take_damage(defn.FIREBALL_DAMAGE)

def cast_heal():
    #heal the player
    if defn.player.creature.hp == defn.player.creature.max_hp:
        gui.message('You are already at full health.', libtcod.red)
        return 'cancelled'
 
    gui.message('Your wounds start to feel better!', libtcod.light_violet)
    defn.player.creature.heal(defn.HEAL_AMOUNT)

def cast_confuse():
    #ask the player for a target to confuse
    gui.message('Left-click an enemy to confuse it, or right-click to cancel.', libtcod.light_cyan)
    monster = target_monster(defn.CONFUSE_RANGE)
    if monster is None: return 'cancelled'
    #replace the monster's AI with a "confused" one; after some turns it will restore the old AI
    old_ai = monster.ai
    monster.ai = obcl.ConfusedMonster(old_ai)
    monster.ai.owner = monster  #tell the new component who owns it
    gui.message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', libtcod.light_green)

def cast_lightning():
    #find closest enemy (inside a maximum range) and damage it
    monster = closest_monster(defn.LIGHTNING_RANGE)
    if monster is None:  #no enemy found within maximum range
        gui.message('No enemy is close enough to strike.', libtcod.red)
        return 'cancelled'
 
    #zap it!
    ##attack = (source, 'lightning bolt', 5)
    ##attack.target_creature(source, monster)

###may need to move these targeting functions
def target_monster(max_range=None):
    #returns a clicked monster inside FOV up to a range, or None if right-clicked
    while True:
        (x, y) = target_tile(max_range)
        if x is None:  #player cancelled
            return None
 
        #return the first clicked monster, otherwise continue looping
        for obj in defn.objects:
            if obj.x == x and obj.y == y and obj.creature and obj != defn.player:
                return obj

def target_tile(max_range=None):
    #return the position of a tile left-clicked in player's FOV (optionally in a range), or (None,None) if right-clicked.
    while True:
        #render the screen. this erases the inventory and shows the names of objects under the mouse.
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,defn.key,defn.mouse)
        render_all()
 
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
 
    for object in defn.objects:
        if object.creature and not object == defn.player and libtcod.map_is_in_fov(defn.fov_map, object.x, object.y):
            #calculate distance between this object and the player
            dist = defn.player.distance_to(object)
            if dist < closest_dist:  #it's closer, so remember it
                closest_enemy = object
                closest_dist = dist
    return closest_enemy
