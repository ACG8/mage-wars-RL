import definitions as defn
import libtcodpy as libtcod
#import object_classes as obj
#import map_functions as mpfn
#import math
#import textwrap
#import shelve
#import random
import gui


#############################################
# Inventory Functions
#############################################

def get_equipped_in_slot(slot):  #returns the equipment in a slot, or None if it's empty
    for obj in defn.inventory:
        if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
            return obj.equipment
    return None

def get_all_equipped(obj):  #returns a list of equipped items
    if obj == defn.player:
        equipped_list = []
        for item in defn.inventory:
            if item.equipment and item.equipment.is_equipped:
                equipped_list.append(item.equipment)
        return equipped_list
    else:
        return []  #other objects have no equipment
