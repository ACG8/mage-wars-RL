#This allows for the population of a map created with the map_generator.
import map_functions as mpfn
import definitions as defn
from random import *


#Function that places an object at a location

def place_object(obj,x):
    if not mpfn.is_blocked(x[0],x[1]):
        defn.objects.append(obj)
        defn.dungeon[x[0]][x[1]].objects.append(obj)
        obj.x = x[0]
        obj.y = x[1]
    else:
        return 'failed'

#Function that places all objects in a list in a room

def populate_room(objects,room):
    for obj in objects:
        placed = False
        attempts = 0

        #try 10 times to find a place in the room for the object
        
        while not placed:
            x0 = randrange(room[1]) + room[2]
            x1 = randrange(room[0]) + room[3]
            if not mpfn.is_blocked(x0,x1):
                place_object(obj,[x0,x1])
                placed = True
            attempts += 1
            if attempts >= 10:
                placed = True

def place_randomly(obj):
    """Places the object in a random open location"""
    placed = False
    while not placed:
        x0 = randrange(defn.MAP_WIDTH)
        x1 = randrange(defn.MAP_HEIGHT)
        if not mpfn.is_blocked(x0,x1):
            place_object(obj,[x0,x1])
            placed = True
            
