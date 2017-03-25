import definitions as defn
import libtcodpy as libtcod
import object_classes as obcl
import map_functions as mpfn
import map_classes as mpcl
import random_generator_functions as rng
import spell_functions as spfn
import gui
import foo_dictionary as fdic
import monster_dictionary as mdic
import item_dictionary as idic
import equipment_dictionary as edic
import dijkstra as djks
            
def make_map():
 
    #the list of objects with just the player
    defn.objects = [defn.player]
 
    #fill map with "blocked" tiles
    defn.dungeon = [[ mpcl.Tile(x,y,'wall',libtcod.grey, True)
        for y in range(defn.MAP_HEIGHT) ]
            for x in range(defn.MAP_WIDTH) ]
    
    rooms = []
    num_rooms = 0

    #carve rooms out of the map
    for r in range(defn.MAX_ROOMS):
        #random width and height
        w = libtcod.random_get_int(0, defn.ROOM_MIN_SIZE, defn.ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, defn.ROOM_MIN_SIZE, defn.ROOM_MAX_SIZE)
        #random position without going outside the map
        x = libtcod.random_get_int(0, 0, defn.MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, defn.MAP_HEIGHT - h - 1)

        #define new room as a rectangle
        new_room = mpcl.Rect(x, y, w, h)
 
        #check that none of the other rooms intersect with this one.
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break
            
        #if there are no intersections, then proceed.
        if not failed:
            #"paint" it to the map's tiles
            mpfn.create_room(new_room)

            #get center coordinates of new room
            (new_x, new_y) = new_room.center()
 
            if num_rooms == 0:
                #this is the first room, where the player starts
                defn.player.x = new_x
                defn.player.y = new_y
                defn.dungeon[defn.player.x][defn.player.y].objects.append(defn.player)

            else:
                #all rooms after the first:
                #connect it to the previous room with a tunnel
                
                #center coordinates of previous room
                (prev_x, prev_y) = rooms[num_rooms - 1].center()

                #flip a coin
                if libtcod.random_get_int(0, 0, 1) == 1:
                    #first move horizontally, then vertically
                    mpfn.create_h_tunnel(prev_x, new_x, prev_y)
                    mpfn.create_v_tunnel(prev_y, new_y, new_x)
                else:
                    #first move vertically, then horizontally
                    mpfn.create_v_tunnel(prev_y, new_y, prev_x)
                    mpfn.create_h_tunnel(prev_x, new_x, new_y)

                                
            #populate the room with objects
            place_objects(new_room)
            
            #finally, append the new room to the list
            rooms.append(new_room)
            num_rooms += 1

    #create stairs at the center of the last room
    defn.stairs = obcl.Object(new_x, new_y,
        always_visible=True,
        properties = {
            'name' : 'portal',
            'graphic' : '<',
            'color' : libtcod.white,
            'description' : 'portal to the next level'})
    defn.objects.append(defn.stairs)
    defn.dungeon[defn.stairs.x][defn.stairs.y].objects.append(defn.stairs)
    defn.stairs.send_to_back()  #so it's drawn below the monsters

    #clear list of dungeon tiles

    defn.dungeon_unblocked_list = []

    #compute adjacencies and dijkstra maps. create list of unblocked tiles. Note that all adjacencies must be computed first, since computing dijkstra maps requires adjacencies
    for y in range(defn.MAP_HEIGHT):
        for x in range(defn.MAP_WIDTH):
            tile = defn.dungeon[x][y]
            tile.compute_adjacent_tiles()
            #currently, the dungeon list includes only unblocked tiles
            if not tile.blocked:
                defn.dungeon_unblocked_list.append(tile)

#populate each new room with objects

def place_objects(room):

    #choose random number of monsters
    max_room_monsters = mpfn.from_dungeon_level([[2, 1], [3, 4], [4, 6]])
    num_monsters = libtcod.random_get_int(0, 0, max_room_monsters)
    for i in range(num_monsters):
        #choose random spot for this monster
        x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
        #only place it if the tile is not blocked
        if not mpfn.is_blocked(x, y):
            #choose a random monster from the dictionary
            arg = rng.random_choice(mdic.mons_dict)
            monster = mdic.get_monster(arg['properties']['name'],x,y)
            #add new monster to the game
            defn.objects.append(monster)
            defn.dungeon[x][y].objects.append(monster)

    max_room_equipment = mpfn.from_dungeon_level([[1, 1], [2, 4], [3, 6]])

    #choose random number of equipment items
    num_equipment = libtcod.random_get_int(0, 0, max_room_equipment)
 
    for i in range(num_equipment):
        #choose random spot for this item
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)
 
        #only place it if the tile is not blocked
        if not mpfn.is_blocked(x, y):
            arg = rng.random_choice(edic.equip_dict)
            equipment = edic.get_equipment(arg['properties']['name'],x,y)
            equipment.always_visible = True

            defn.objects.append(equipment)
            equipment.send_to_back()
            defn.dungeon[x][y].objects.append(equipment)

    max_room_items = mpfn.from_dungeon_level([[2, 1], [3, 4], [4, 6]])

    #choose random number of equipment items
    num_items = libtcod.random_get_int(0, 0, max_room_equipment)
 
    for i in range(num_items):
        #choose random spot for this item
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)
 
        #only place it if the tile is not blocked
        if not mpfn.is_blocked(x, y):
            arg = rng.random_choice(idic.item_dict)
            item = idic.get_item(arg['properties']['name'],x,y)
            item.always_visible = True

            defn.objects.append(item)
            item.send_to_back()
            defn.dungeon[x][y].objects.append(item)   

#advance to the next level
def next_level():
    gui.message('You pass through the magical gate with some apprehension. The gate\'s magic heals and restores you.', libtcod.light_violet)
    #heal the player by 50%
    defn.player.creature.heal(defn.player.creature.max_hp / 2)
    defn.player.creature.conditions = []
    #increment the dungeon level
    defn.dungeon_level += 1
    #generate a new map
    make_map()
    mpfn.initialize_fov()
