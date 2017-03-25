import definitions as defn
import libtcodpy as libtcod
import object_classes as obcl
import map_functions as mpfn
import map_classes as mpcl
import random_generator_functions as rng
import spell_functions as spfn
import gui

def place_objects(room):

    #maximum number of monsters per room
    max_room_monsters = mpfn.from_dungeon_level([[2, 1], [3, 4], [5, 6]])
 
    #chance of each monster
    monster_chances = {}
    monster_chances['bitterwood_fox'] = 80
    monster_chances['iron_golem'] = mpfn.from_dungeon_level([[15, 3], [30, 5], [60, 7]])
 
    #maximum number of items per room
    max_room_items = mpfn.from_dungeon_level([[2, 1], [3, 4]])
 
    #chance of each item (by default they have a chance of 0 at level 1, which then goes up)
    item_chances = {}
    item_chances['sword'] = 15
    item_chances['leather boots'] = 25
    item_chances['leather gloves'] = 25
    item_chances['war gauntlets'] = mpfn.from_dungeon_level([[25, 2]]) 
    item_chances['heal'] = 35  #healing potion always shows up, even if all other items have 0 chance
    item_chances['lightning'] = mpfn.from_dungeon_level([[25, 4]])
    item_chances['fireball'] =  mpfn.from_dungeon_level([[25, 6]])
    item_chances['confuse'] =   mpfn.from_dungeon_level([[10, 2]])

    #choose random number of monsters
    num_monsters = libtcod.random_get_int(0, 0, max_room_monsters)
 
    for i in range(num_monsters):
        #choose random spot for this monster
        x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
         #only place it if the tile is not blocked
        if not mpfn.is_blocked(x, y):
            choice = rng.random_choice(monster_chances)
            if choice == 'bitterwood_fox':
                creature_component = obcl.Creature(hp=5, mana=0, armor=0, power=3, xp=35, death_function=obcl.monster_death)
                ai_component = obcl.BasicMonster()
                monster = obcl.Object(x, y, 'f', 'bitterwood fox', libtcod.amber,
                    blocks=True, creature=creature_component, ai=ai_component)
            elif choice == 'iron_golem':
                creature_component = obcl.Creature(hp=13, mana=0, armor=5, power=5, xp=100, death_function=obcl.monster_death)
                ai_component = obcl.BasicMonster()
                monster = obcl.Object(x, y, 'G', 'iron golem', libtcod.silver,
                    blocks=True, creature=creature_component, ai=ai_component)
     
        defn.objects.append(monster)

    #choose random number of items
    num_items = libtcod.random_get_int(0, 0, max_room_items)
 
    for i in range(num_items):
        #choose random spot for this item
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)
 
        #only place it if the tile is not blocked
        if not mpfn.is_blocked(x, y):
            choice = rng.random_choice(item_chances)
            if choice == 'heal':
                item_component = obcl.Item(use_function=spfn.cast_heal)
                item = obcl.Object(x, y, '!', 'healing potion', libtcod.violet, item=item_component)
                item.always_visible = True
            elif choice == 'lightning':
                item_component = obcl.Item(use_function=spfn.cast_lightning)
                item = obcl.Object(x, y, '#', 'scroll of lightning bolt', libtcod.light_yellow, item=item_component)
                item.always_visible = True
            elif choice == 'fireball':
                item_component = obcl.Item(use_function=spfn.cast_fireball) 
                item = obcl.Object(x, y, '#', 'scroll of fireball', libtcod.light_yellow, item=item_component)
                item.always_visible = True
            elif choice == 'confuse':
                item_component = obcl.Item(use_function=spfn.cast_confuse)
                item = obcl.Object(x, y, '#', 'scroll of confusion', libtcod.light_yellow, item=item_component)
                item.always_visible = True
            elif choice == 'sword':
                equipment_component = obcl.Equipment(slot='right hand', power_bonus=1)
                item = obcl.Object(x, y, '/', 'sword', libtcod.sky, equipment=equipment_component)
                item.always_visible = True
            elif choice == 'leather boots':
                equipment_component = obcl.Equipment(slot='feet', armor_bonus=1)
                item = obcl.Object(x, y, '[', 'leather boots', libtcod.darker_orange, equipment=equipment_component)
                item.always_visible = True
            elif choice == 'leather gloves':
                equipment_component = obcl.Equipment(slot='hands', armor_bonus=1)
                item = obcl.Object(x, y, '[', 'leather gloves', libtcod.darker_orange, equipment=equipment_component)
                item.always_visible = True
            elif choice == 'war gauntlets':
                equipment_component = obcl.Equipment(slot='hands', power_bonus=1)
                item = obcl.Object(x, y, '[', 'war_gauntlets', libtcod.darker_orange, equipment=equipment_component)
                item.always_visible = True

            defn.objects.append(item)
            item.send_to_back()

def make_map():
 
    #the list of objects with just the player
    defn.objects = [defn.player]
 
    #fill map with "blocked" tiles
    defn.dungeon = [[ mpcl.Tile(True)
        for y in range(defn.MAP_HEIGHT) ]
            for x in range(defn.MAP_WIDTH) ]

    rooms = []
    num_rooms = 0
 
    for r in range(defn.MAX_ROOMS):
        #random width and height
        w = libtcod.random_get_int(0, defn.ROOM_MIN_SIZE, defn.ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, defn.ROOM_MIN_SIZE, defn.ROOM_MAX_SIZE)
        #random position without going out of the boundaries of the map
        x = libtcod.random_get_int(0, 0, defn.MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, defn.MAP_HEIGHT - h - 1)

        #"Rect" class makes rectangles easier to work with
        new_room = mpcl.Rect(x, y, w, h)
 
        #run through the other rooms and see if they intersect with this one
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed:
            #this means there are no intersections, so this room is valid
 
            #"paint" it to the map's tiles
            mpfn.create_room(new_room)
            
            #add some contents to this room, such as monsters
            place_objects(new_room)

            #center coordinates of new room, will be useful later
            (new_x, new_y) = new_room.center()
 
            if num_rooms == 0:
                #this is the first room, where the player starts at
                defn.player.x = new_x
                defn.player.y = new_y

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
            #finally, append the new room to the list
            rooms.append(new_room)
            num_rooms += 1

    #create stairs at the center of the last room
    defn.stairs = obcl.Object(new_x, new_y, '<', 'stairs', libtcod.white, always_visible=True)
    defn.objects.append(defn.stairs)
    defn.stairs.send_to_back()  #so it's drawn below the monsters

def next_level():
    #advance to the next level
    gui.message('You take a moment to rest, and recover your strength.', libtcod.light_violet)
    defn.player.creature.heal(defn.player.creature.max_hp / 2)  #heal the player by 50%
 
    gui.message('After a rare moment of peace, you descend deeper into the heart of the dungeon...', libtcod.red)
    defn.dungeon_level += 1
    make_map()  #create a fresh new level!
    mpfn.initialize_fov()
