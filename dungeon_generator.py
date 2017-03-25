import definitions as defn
import libtcodpy as libtcod
import object_classes as obcl
import map_functions as mpfn
import map_classes as mpcl
import random_generator_functions as rng
import spell_functions as spfn
import gui
import monster_dictionary as mdic
import item_dictionary as idic
import equipment_dictionary as edic
import dijkstra as djks
import map_generator as mgen
import map_populator as mpop
import mazeGenerator
import caveGenerator
from random import *

def make_map():
    #add the player to the list of objects
    defn.objects = [defn.player]

    #create a blank dungeon
    defn.dungeon = [[ mpcl.Tile(x,y,'wall',libtcod.grey, True)
        for y in range(defn.MAP_HEIGHT) ]
            for x in range(defn.MAP_WIDTH) ]

    #generate a dungeon map and print it to the dungeon
    level = mgen.dMap()

    #choose leveltype
    randomint = randrange(100)
    if randomint > 40: #dungeon
        level.makeMap(defn.MAP_WIDTH,defn.MAP_HEIGHT,110,20,60)
    elif randomint > 10: #cave
        level.mapArr = caveGenerator.generateCave((defn.MAP_WIDTH,defn.MAP_HEIGHT),defn.MAP_WIDTH*defn.MAP_HEIGHT*2/3)
    else: #maze
        level.mapArr = mazeGenerator.generateMaze((defn.MAP_WIDTH,defn.MAP_HEIGHT))

    for y in range(defn.MAP_HEIGHT):
        for x in range(defn.MAP_WIDTH):
            print_tile(level,[x,y])

    #generate 12 encounters
    for i in range(12):
        generate_encounters()

    #populate each room
    #for room in level.roomList:
       # generate_encounters(room)

    #send all items to the back
    for obj in defn.objects:
        if obj.item:
            obj.send_to_back()

    #create stairs at the center of the last room
    defn.stairs = obcl.Object(0, 0,
        always_visible=True,
        properties = {
            'name' : 'portal',
            'graphic' : '<',
            'color' : libtcod.white,
            'description' : 'portal to the next level'})
    mpop.place_randomly(defn.stairs)
    defn.stairs.send_to_back()

    #place the player

    mpop.place_randomly(defn.player)

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

#Populate a room
def generate_encounters(room=None):

    #MONSTERS (60% chance of appearing)
    max_room_monsters = mpfn.from_dungeon_level([
                {'level' : 1, 'value' : 1},
                {'level' : 2, 'value' : 3},
                {'level' : 3, 'value' : 5}])
    max_room_equipment = mpfn.from_dungeon_level([
            {'level' : 1, 'value' : 1},
            {'level' : 3, 'value' : 2}])
    max_room_items = mpfn.from_dungeon_level([
            {'level' : 1, 'value' : 1},
            {'level' : 3, 'value' : 2}])
    
    if randrange(100)<20:
        
        
        #choose random number of equipments
        num_equipment = libtcod.random_get_int(0, 0, max_room_equipment)
        equipments = []
        for i in range(num_equipment):
            arg = rng.random_choice(edic.equip_dict)
            equipment = edic.get_equipment(arg['properties']['name'],0,0)
            equipment.always_visible = True
            equipments.append(equipment)

        #place in rooms or randomly
        if room==None:
            for equip in equipments:
                mpop.place_randomly(equip)
        else:
            mpop.populate_room(equipments,room)

    #ITEMS (40% chance of appearing)
    if randrange(100)<40:
        

        #choose random number of items
        num_items = libtcod.random_get_int(0, 0, max_room_equipment)
        items = []
        for i in range(num_items):
            arg = rng.random_choice(idic.item_dict)
            item = idic.get_item(arg['properties']['name'],0,0)
            item.always_visible = True
            items.append(item)

        #place in rooms or randomly
        if room==None:
            for item in items:
                mpop.place_randomly(item)
        else:
            mpop.populate_room(items,room)

        #MONSTERS
    
    if randrange(100)<60:
        
        num_monsters = libtcod.random_get_int(0, 0, max_room_monsters)
        #later, can define specific hordes of monster. For now, just generate randomly
        monsters = []
        for i in range(num_monsters):
            arg = rng.random_choice(mdic.mons_dict)
            monster = mdic.get_monster(arg['properties']['name'],0,0)
            monsters.append(monster)

        #place in rooms or randomly
        if room==None:
            for monst in monsters:
                mpop.place_randomly(monst)
        else:
            mpop.populate_room(monsters,room)

    #EQUIPMENT (20% chance of appearing

#Define a mapping between a dMap and the dungeon map
def print_tile(dMap,x):
    x0 = x[0]
    x1 = x[1]
    value = dMap.mapArr[x0][x1]
    if value=='.': #dirt floor
        defn.dungeon[x0][x1].blocked = False
        defn.dungeon[x0][x1].block_sight = False
        defn.dungeon[x0][x1].name = 'floor'
        defn.dungeon[x0][x1].color = libtcod.sepia
        defn.dungeon[x0][x1].graphic = '.'
        
    if value==' ': #wall
        defn.dungeon[x0][x1].blocked = True
        defn.dungeon[x0][x1].block_sight = True
        defn.dungeon[x0][x1].name = 'wall'
        defn.dungeon[x0][x1].color = libtcod.grey
        defn.dungeon[x0][x1].graphic = ' '
        
    if value=='+': #door
        defn.dungeon[x0][x1].blocked = False
        defn.dungeon[x0][x1].block_sight = True
        defn.dungeon[x0][x1].name = 'door'
        defn.dungeon[x0][x1].color = libtcod.blue
        defn.dungeon[x0][x1].graphic = '+'

    if value=='\"': #grass floor
        defn.dungeon[x0][x1].blocked = False
        defn.dungeon[x0][x1].block_sight = False
        defn.dungeon[x0][x1].name = 'grass floor'
        defn.dungeon[x0][x1].color = libtcod.darkest_green
        defn.dungeon[x0][x1].graphic = '\"'

    if value=='#': #window
        defn.dungeon[x0][x1].blocked = True
        defn.dungeon[x0][x1].block_sight = False
        defn.dungeon[x0][x1].name = 'window'
        defn.dungeon[x0][x1].color = libtcod.light_sepia
        defn.dungeon[x0][x1].graphic = '#'

#advance to the next level
def next_level():
    gui.message('You pass through the magical gate with some apprehension. The gate\'s magic heals and restores you.', libtcod.light_violet)
    #heal the player by 50%
    defn.player.creature.conditions = []
    defn.player.creature.heal(defn.player.creature.max_hp)
    #store all friendly creatures
    for obj in defn.objects:
        if obj.creature and obj != defn.player and not obj in defn.player.creatures:
            if obj.creature.alignment == 'player':
                defn.player.creatures.append(obj)
    #increment the dungeon level
    defn.dungeon_level += 1
    #generate a new map
    make_map()
    mpfn.initialize_fov()
