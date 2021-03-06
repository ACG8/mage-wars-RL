import definitions as defn
import libtcodpy as libtcod
import random

def initialize_fov():

    libtcod.console_clear(defn.con)  #unexplored areas start black (which is the default background color)

    #create the FOV map, according to the generated map
    fov_map = libtcod.map_new(defn.MAP_WIDTH, defn.MAP_HEIGHT)
    for y in range(defn.MAP_HEIGHT):
        for x in range(defn.MAP_WIDTH):
            libtcod.map_set_properties(defn.fov_map, x, y, not defn.dungeon[x][y].block_sight, not defn.dungeon[x][y].blocked)
            
    defn.fov_recompute = True

def create_room(room):
    #go through the tiles in the rectangle and make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            defn.dungeon[x][y].blocked = False
            defn.dungeon[x][y].block_sight = False
            defn.dungeon[x][y].name = 'floor'
            defn.dungeon[x][y].color = libtcod.sepia

def create_h_tunnel(x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        defn.dungeon[x][y].blocked = False
        defn.dungeon[x][y].block_sight = False
        defn.dungeon[x][y].name = 'floor'
        defn.dungeon[x][y].color = libtcod.sepia

def create_v_tunnel(y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        defn.dungeon[x][y].blocked = False
        defn.dungeon[x][y].block_sight = False
        defn.dungeon[x][y].name = 'floor'
        defn.dungeon[x][y].color = libtcod.sepia

def from_dungeon_level(table):
    #returns a value that depends on level. the table specifies what value occurs after each level, default is 0.
    for pair in reversed(table):
        if defn.dungeon_level >= pair['level']:
            return pair['value']
    return 0

def is_blocked(x, y):
    #first test the map tile
    if defn.dungeon[x][y].blocked:
        return True
 
    #now check for any blocking objects
    for object in defn.objects:
        if object.blocks and object.x == x and object.y == y:
            return True
 
    return False

def get_tiles_between(x1,y1,x2,y2):
    tiles = []
    #returns all tiles on the line between tile1 and tile2, including those tiles.
    libtcod.line_init(x1,y1,x2,y2)
    done = False
    while not done:
        (x,y) = libtcod.line_step()
        if x and y:
            tiles.append(defn.dungeon[x][y])
        else:
            done = True
    return tiles
        

def get_map_as_array():

    array = [[ 1
        for y in range(defn.MAP_HEIGHT) ]
            for x in range(defn.MAP_WIDTH) ]

    for y in range(defn.MAP_HEIGHT):
        for x in range(defn.MAP_WIDTH):
            if defn.dungeon[x][y].blocked:
                array[x][y] = -1
