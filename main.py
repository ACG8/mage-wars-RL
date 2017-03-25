import var
import libtcodpy as libtcod
import math
import textwrap
import shelve
import random

#############################################
# Classes
#############################################

class Attack:
    #any attack made by one creature against another
    def __init__(self, source, name, dice, traits=None, effect=None):
        self.base_dice = dice
        self.name = name
        self.traits = traits
        self.effect = effect
        
    @property
    def dice(self):
        bonus = 0 #for now, no bonuses sum(equipment.power_bonus for equipment in get_all_equipped(self.owner))
        return self.base_dice #+ bonus

    def target_creature(self, source, target):
        #mage wars attack formula
        i=0
        norm_dmg=0
        crit_dmg=0
        while i < self.dice:
            dmg = libtcod.random_get_int(0,0,2)
            crit = dmg*libtcod.random_get_int(0,0,1)
            norm_dmg += dmg - crit
            crit_dmg += crit
            i += 1

        damage = crit_dmg + max(norm_dmg - target.creature.armor, 0)
 
        if damage > 0:
            #make the target take some damage
            message (source.owner.name.capitalize() + ' attacks ' + target.name + ', inflicing ' + str(damage) + ' damage.', libtcod.red)
            target.creature.take_damage(damage)
        else:
            message (source.owner.name.capitalize() + ' attacks ' + target.name + ' but fails to inflict any damage!', libtcod.red)


class Object:
    #this is a generic object: the player, a monster, an item, the stairs...
    #it's always represented by a character on screen.
    def __init__(self, x, y, char, name, color, blocks=False, always_visible=False, creature=None, ai=None, item=None, equipment=None):

        self.always_visible = always_visible
        self.name = name
        self.blocks = blocks
        self.x = x
        self.y = y
        self.char = char
        self.color = color

        self.creature = creature
        if self.creature:  #let the fighter component know who owns it
            self.creature.owner = self
 
        self.ai = ai
        if self.ai:  #let the AI component know who owns it
            self.ai.owner = self

        self.item = item
        if self.item:  #let the Item component know who owns it
            self.item.owner = self

        self.equipment = equipment
        if self.equipment:  #let the Equipment component know who owns it
            self.equipment.owner = self
            #there must be an Item component for the Equipment component to work properly
            self.item = Item()
            self.item.owner = self
 
    def move(self, dx, dy):
        if not is_blocked(self.x + dx, self.y + dy):
        #move by the given amount
            self.x += dx
            self.y += dy
 
    def draw(self):
        #set the color and then draw the character that represents this object at its position
        #only show if it's visible to the player; or it's set to "always visible" and on an explored tile
        if (libtcod.map_is_in_fov(fov_map, self.x, self.y) or
            (self.always_visible and map[self.x][self.y].explored)):
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)
            
    def clear(self):
        #erase the character that represents this object
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

    def move_towards(self, target_x, target_y):
        #vector from this object to the target, and distance
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
 
        #normalize it to length 1 (preserving direction), then round it and
        #convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)

    def distance_to(self, other):
        #return the distance to another object
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)
    
    def send_to_back(self):
        #make this object be drawn first, so all others appear above it if they're in the same tile.
        global objects
        objects.remove(self)
        objects.insert(0, self)

    def distance(self, x, y):
        #return the distance to some coordinates
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

class Creature:
    #combat-related properties and methods (monster, player, NPC).
    def __init__(self, hp, mana, armor, power, xp, death_function=None):
        self.death_function = death_function
        self.base_max_mana = mana
        self.mana = mana
        self.base_max_hp = hp
        self.hp = hp
        self.base_armor = armor
        self.base_power = power
        self.xp = xp

    @property
    def power(self):
        bonus = sum(equipment.power_bonus for equipment in get_all_equipped(self.owner))
        return self.base_power + bonus

    @property
    def armor(self):  #return actual armor, by summing up the bonuses from all equipped items
        bonus = sum(equipment.armor_bonus for equipment in get_all_equipped(self.owner))
        return self.base_armor + bonus

    @property
    def max_mana(self):  #return actual max_hp, by summing up the bonuses from all equipped items
        bonus = sum(equipment.max_mana_bonus for equipment in get_all_equipped(self.owner))
        return self.base_max_hp + bonus
 
    @property
    def max_hp(self):  #return actual max_hp, by summing up the bonuses from all equipped items
        bonus = sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.owner))
        return self.base_max_hp + bonus

    def take_damage(self, damage):
        #apply damage if possible
        if damage > 0:
            self.hp -= damage
            #check for death. if there's a death function, call it
        if self.hp <= 0:
            function = self.death_function
            if function is not None:
                function(self.owner)
                if self.owner != player:  #yield experience to the player
                    player.creature.xp += self.xp

    def attack(self, target):
        attack = Attack(self, 'melee attack', self.power)
        attack.target_creature(self, target)

    def heal(self, amount):
        #heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def spend_mana(self, cost):
        #apply damage if possible
        if self.mana - cost >= 0:
            self.mana -= cost
        else:
            return 'cancelled'

class BasicMonster:
    #AI for a basic monster.
    def take_turn(self):
        #a basic monster takes its turn. If you can see it, it can see you
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
 
            #move towards player if far away
            if monster.distance_to(player) >= 2:
                monster.move_towards(player.x, player.y)
 
            #close enough, attack! (if the player is still alive.)
            elif player.creature.hp > 0:
                monster.creature.attack(player)

class ConfusedMonster:
    #AI for a temporarily confused monster (reverts to previous after a while).
    def __init__(self, old_ai, num_turns=var.CONFUSE_NUM_TURNS):
        self.old_ai = old_ai
        self.num_turns = num_turns
 
    def take_turn(self):
        if self.num_turns > 0:  #still confused...
            #move in a random direction, and decrease the number of turns confused
            self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
            self.num_turns -= 1
 
        else:  #restore the previous AI (this one will be deleted because it's not referenced anymore)
            self.owner.ai = self.old_ai
            message('The ' + self.owner.name + ' is no longer confused!', libtcod.red)

class Spell:
    def __init__(self, name, source, cost, use_function=None):
        self.name = name
        self.source = source
        self.use_function = use_function
        self.cost = cost
    #an spell that that can be learned and used.
    def use(self):
        if self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used.')
        #else:
            ##edit!
            #if self.use_function() != 'cancelled':
                #pass
                #self.source.creature.spend_mana(self.cost) != 'cancelled':
                
                
                #inventory.remove(self.source)  #destroy after use, unless it was cancelled for some reason

class Item:
    def __init__(self, use_function=None):
        self.use_function = use_function
    #an item that can be picked up and used.
    def pick_up(self):
        #add to the player's inventory and remove from the map
        if len(inventory) >= 26:
            message('Your inventory is full, cannot pick up ' + self.owner.name + '.', libtcod.red)
        else:
            inventory.append(self.owner)
            objects.remove(self.owner)
            message('You picked up a ' + self.owner.name + '!', libtcod.green)
            #special case: automatically equip, if the corresponding equipment slot is unused
            equipment = self.owner.equipment
            if equipment and get_equipped_in_slot(equipment.slot) is None:
                equipment.equip()
    def use(self):
        #special case: if the object has the Equipment component, the "use" action is to equip/dequip
        if self.owner.equipment:
            self.owner.equipment.toggle_equip()
            return
        #just call the "use_function" if it is defined
        if self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function() != 'cancelled':
                inventory.remove(self.owner)  #destroy after use, unless it was cancelled for some reason

    def drop(self):
        #add to the map and remove from the player's inventory. also, place it at the player's coordinates
        objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        #special case: if the object has the Equipment component, dequip it before dropping
        if self.owner.equipment:
            self.owner.equipment.dequip()
        message('You dropped a ' + self.owner.name + '.', libtcod.yellow)

class Equipment:
    #an object that can be equipped, yielding bonuses. automatically adds the Item component.
    def __init__(self, slot, power_bonus=0, armor_bonus=0, max_hp_bonus=0, max_mana_bonus=0):
        self.power_bonus = power_bonus
        self.armor_bonus = armor_bonus
        self.max_hp_bonus = max_hp_bonus
        self.max_mana_bonus = max_mana_bonus
        self.slot = slot
        self.is_equipped = False
 
    def toggle_equip(self):  #toggle equip/dequip status
        if self.is_equipped:
            self.dequip()
        else:
            self.equip()
 
    def equip(self):
        #equip object and show a message about it
        #if the slot is already being used, dequip whatever is there first
        old_equipment = get_equipped_in_slot(self.slot)
        if old_equipment is not None:
            old_equipment.dequip()
        self.is_equipped = True
        message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', libtcod.light_green)
 
    def dequip(self):
        #dequip object and show a message about it
        if not self.is_equipped: return
        self.is_equipped = False
        message('Dequipped ' + self.owner.name + ' from ' + self.slot + '.', libtcod.light_yellow)

class Tile:
    #a tile of the map and its properties
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
        self.explored = False
        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

class Rect:
    #defines a rectangle
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)
     
    def intersect(self, other):
            #returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1) 


#############################################
# Inventory Functions
#############################################

def inventory_menu(header):
    #show a menu with each item of the inventory as an option
    if len(inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = []
        for item in inventory:
            text = item.name
            #show additional information, in case it's equipped
            if item.equipment and item.equipment.is_equipped:
                text = text + ' (on ' + item.equipment.slot + ')'
            options.append(text)
 
    index = menu(header, options, var.INVENTORY_WIDTH)

    #if an item was chosen, return it
    if index is None or len(inventory) == 0: return None
    return inventory[index].item

def spellbook_menu(header):
    #show a menu with each spell in memory as an option
    if len(spellbook) == 0:
        options = ['You don\'t know any spells.']
    else:
        options = []
        for spell in spellbook:
            text = spell.name
            options.append(text)
 
    index = menu(header, options, var.SPELLBOOK_WIDTH)

    #if an item was chosen, return it
    if index is None or len(spellbook) == 0: return None
    return spellbook[index]

def get_equipped_in_slot(slot):  #returns the equipment in a slot, or None if it's empty
    for obj in inventory:
        if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
            return obj.equipment
    return None

def get_all_equipped(obj):  #returns a list of equipped items
    if obj == player:
        equipped_list = []
        for item in inventory:
            if item.equipment and item.equipment.is_equipped:
                equipped_list.append(item.equipment)
        return equipped_list
    else:
        return []  #other objects have no equipment



#############################################
# Death Functions
#############################################

def player_death(player):
    #the game ended!
    global game_state
    message ('You died!', libtcod.red)
    game_state = 'dead'
 
    #for added effect, transform the player into a corpse!
    player.char = '%'
    player.color = libtcod.dark_red
 
def monster_death(monster):
    #transform it into a nasty corpse! it doesn't block, can't be
    #attacked and doesn't move
    message('The ' + monster.name + ' collapses in defeat! You gain ' + str(monster.creature.xp) + ' experience points.', libtcod.orange)
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.creature = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.send_to_back()

#############################################
# Map Functions
#############################################

def create_room(room):
    global map
    #go through the tiles in the rectangle and make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            map[x][y].blocked = False
            map[x][y].block_sight = False

def create_h_tunnel(x1, x2, y):
    global map
    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def create_v_tunnel(y1, y2, x):
    global map
    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def place_objects(room):

    #maximum number of monsters per room
    max_room_monsters = from_dungeon_level([[2, 1], [3, 4], [5, 6]])
 
    #chance of each monster
    monster_chances = {}
    monster_chances['bitterwood_fox'] = 80  #orc always shows up, even if all other monsters have 0 chance
    monster_chances['iron_golem'] = from_dungeon_level([[15, 3], [30, 5], [60, 7]])
 
    #maximum number of items per room
    max_room_items = from_dungeon_level([[1, 1], [2, 4]])
 
    #chance of each item (by default they have a chance of 0 at level 1, which then goes up)
    item_chances = {}
    item_chances['sword'] = 25
    item_chances['leather boots'] = 25
    item_chances['leather gloves'] = 25
    item_chances['heal'] = 35  #healing potion always shows up, even if all other items have 0 chance
    item_chances['lightning'] = from_dungeon_level([[25, 4]])
    item_chances['fireball'] =  from_dungeon_level([[25, 6]])
    item_chances['confuse'] =   from_dungeon_level([[10, 2]])

    #choose random number of monsters
    num_monsters = libtcod.random_get_int(0, 0, max_room_monsters)
 
    for i in range(num_monsters):
        #choose random spot for this monster
        x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
         #only place it if the tile is not blocked
        if not is_blocked(x, y):
            choice = random_choice(monster_chances)
            if choice == 'bitterwood_fox':
                creature_component = Creature(hp=5, mana=0, armor=0, power=3, xp=35, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 'f', 'bitterwood fox', libtcod.amber,
                    blocks=True, creature=creature_component, ai=ai_component)
            elif choice == 'iron_golem':
                creature_component = Creature(hp=13, mana=0, armor=5, power=5, xp=100, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 'G', 'iron golem', libtcod.silver,
                    blocks=True, creature=creature_component, ai=ai_component)
     
        objects.append(monster)

    #choose random number of items
    num_items = libtcod.random_get_int(0, 0, max_room_items)
 
    for i in range(num_items):
        #choose random spot for this item
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)
 
        #only place it if the tile is not blocked
        if not is_blocked(x, y):
            choice = random_choice(item_chances)
            if choice == 'heal':
                item_component = Item(use_function=cast_heal)
                item = Object(x, y, '!', 'healing potion', libtcod.violet, item=item_component)
                item.always_visible = True
            elif choice == 'lightning':
                item_component = Item(use_function=cast_lightning)
                item = Object(x, y, '#', 'scroll of lightning bolt', libtcod.light_yellow, item=item_component)
                item.always_visible = True
            elif choice == 'fireball':
                item_component = Item(use_function=cast_fireball) 
                item = Object(x, y, '#', 'scroll of fireball', libtcod.light_yellow, item=item_component)
                item.always_visible = True
            elif choice == 'confuse':
                item_component = Item(use_function=cast_confuse)
                item = Object(x, y, '#', 'scroll of confusion', libtcod.light_yellow, item=item_component)
                item.always_visible = True
            elif choice == 'sword':
                equipment_component = Equipment(slot='right hand', power_bonus=1)
                item = Object(x, y, '/', 'sword', libtcod.sky, equipment=equipment_component)
                item.always_visible = True
            elif choice == 'leather boots':
                equipment_component = Equipment(slot='feet', armor_bonus=1)
                item = Object(x, y, '[', 'leather boots', libtcod.darker_orange, equipment=equipment_component)
                item.always_visible = True
            elif choice == 'leather gloves':
                equipment_component = Equipment(slot='hands', armor_bonus=1)
                item = Object(x, y, '[', 'leather gloves', libtcod.darker_orange, equipment=equipment_component)
                item.always_visible = True

            objects.append(item)
            item.send_to_back()

def from_dungeon_level(table):
    #returns a value that depends on level. the table specifies what value occurs after each level, default is 0.
    for (value, level) in reversed(table):
        if dungeon_level >= level:
            return value
    return 0

def is_blocked(x, y):
    #first test the map tile
    if map[x][y].blocked:
        return True
 
    #now check for any blocking objects
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True
 
    return False

def get_map_as_array():

    array = [[ 1
        for y in range(var.MAP_HEIGHT) ]
            for x in range(var.MAP_WIDTH) ]

    for y in range(var.MAP_HEIGHT):
        for x in range(var.MAP_WIDTH):
            if map[x][y].blocked:
                array[x][y] = -1

    print array

def make_map():
    global map, objects, stairs
 
    #the list of objects with just the player
    objects = [player]
 
    #fill map with "blocked" tiles
    map = [[ Tile(True)
        for y in range(var.MAP_HEIGHT) ]
            for x in range(var.MAP_WIDTH) ]

    rooms = []
    num_rooms = 0
 
    for r in range(var.MAX_ROOMS):
        #random width and height
        w = libtcod.random_get_int(0, var.ROOM_MIN_SIZE, var.ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, var.ROOM_MIN_SIZE, var.ROOM_MAX_SIZE)
        #random position without going out of the boundaries of the map
        x = libtcod.random_get_int(0, 0, var.MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, var.MAP_HEIGHT - h - 1)

        #"Rect" class makes rectangles easier to work with
        new_room = Rect(x, y, w, h)
 
        #run through the other rooms and see if they intersect with this one
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed:
            #this means there are no intersections, so this room is valid
 
            #"paint" it to the map's tiles
            create_room(new_room)
            
            #add some contents to this room, such as monsters
            place_objects(new_room)

            #center coordinates of new room, will be useful later
            (new_x, new_y) = new_room.center()
 
            if num_rooms == 0:
                #this is the first room, where the player starts at
                player.x = new_x
                player.y = new_y

            else:
                #all rooms after the first:
                #connect it to the previous room with a tunnel
                
                #center coordinates of previous room
                (prev_x, prev_y) = rooms[num_rooms - 1].center()

                #flip a coin
                if libtcod.random_get_int(0, 0, 1) == 1:
                    #first move horizontally, then vertically
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    #first move vertically, then horizontally
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)
            #finally, append the new room to the list
            rooms.append(new_room)
            num_rooms += 1

    #create stairs at the center of the last room
    stairs = Object(new_x, new_y, '<', 'stairs', libtcod.white, always_visible=True)
    objects.append(stairs)
    stairs.send_to_back()  #so it's drawn below the monsters

#############################################
# Spell Functions
#############################################

def cast_fireball():
    #ask the player for a target tile to throw a fireball at
    message('Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan)
    (x, y) = target_tile()
    if x is None: return 'cancelled'
    message('The fireball explodes, burning everything within ' + str(var.FIREBALL_RADIUS) + ' tiles!', libtcod.orange)
 
    for obj in objects:  #damage every fighter in range, including the player
        if obj.distance(x, y) <= var.FIREBALL_RADIUS and obj.creature:
            message('The ' + obj.name + ' gets burned for ' + str(var.FIREBALL_DAMAGE) + ' hit points.', libtcod.orange)
            obj.creature.take_damage(var.FIREBALL_DAMAGE)

def cast_heal():
    #heal the player
    if player.creature.hp == player.creature.max_hp:
        message('You are already at full health.', libtcod.red)
        return 'cancelled'
 
    message('Your wounds start to feel better!', libtcod.light_violet)
    player.creature.heal(var.HEAL_AMOUNT)

def cast_confuse():
    #ask the player for a target to confuse
    message('Left-click an enemy to confuse it, or right-click to cancel.', libtcod.light_cyan)
    monster = target_monster(var.CONFUSE_RANGE)
    if monster is None: return 'cancelled'
    #replace the monster's AI with a "confused" one; after some turns it will restore the old AI
    old_ai = monster.ai
    monster.ai = ConfusedMonster(old_ai)
    monster.ai.owner = monster  #tell the new component who owns it
    message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', libtcod.light_green)

###Edit!###

def cast_lightning():
    #find closest enemy (inside a maximum range) and damage it
    monster = closest_monster(var.LIGHTNING_RANGE)
    if monster is None:  #no enemy found within maximum range
        message('No enemy is close enough to strike.', libtcod.red)
        return 'cancelled'
 
    #zap it!
    ##attack = (source, 'lightning bolt', 5)
    ##attack.target_creature(source, monster)

#############################################
# Targeting Functions
#############################################

def target_monster(max_range=None):
    #returns a clicked monster inside FOV up to a range, or None if right-clicked
    while True:
        (x, y) = target_tile(max_range)
        if x is None:  #player cancelled
            return None
 
        #return the first clicked monster, otherwise continue looping
        for obj in objects:
            if obj.x == x and obj.y == y and obj.creature and obj != player:
                return obj

def target_tile(max_range=None):
    #return the position of a tile left-clicked in player's FOV (optionally in a range), or (None,None) if right-clicked.
    global key, mouse
    while True:
        #render the screen. this erases the inventory and shows the names of objects under the mouse.
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
        render_all()
 
        (x, y) = (mouse.cx, mouse.cy)
 
        #accept the target if the player clicked in FOV, and in case a range is specified, if it's in that range
        if (mouse.lbutton_pressed and libtcod.map_is_in_fov(fov_map, x, y) and
            (max_range is None or player.distance(x, y) <= max_range)):
            return (x, y)
        
        if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
            return (None, None)  #cancel if the player right-clicked or pressed Escape

def closest_monster(max_range):
    #find closest enemy, up to a maximum range, and in the player's FOV
    closest_enemy = None
    closest_dist = max_range + 1  #start with (slightly more than) maximum range
 
    for object in objects:
        if object.creature and not object == player and libtcod.map_is_in_fov(fov_map, object.x, object.y):
            #calculate distance between this object and the player
            dist = player.distance_to(object)
            if dist < closest_dist:  #it's closer, so remember it
                closest_enemy = object
                closest_dist = dist
    return closest_enemy

def render_all():
    global fov_map, fov_recompute

    if fov_recompute:
        #recompute FOV if needed (the player moved or something)
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, var.TORCH_RADIUS, var.FOV_LIGHT_WALLS, var.FOV_ALGO)

        #go through all tiles, and set their background color according to the FOV
        for y in range(var.MAP_HEIGHT):
            for x in range(var.MAP_WIDTH):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = map[x][y].block_sight
                if not visible:
                    #if it's not visible right now, the player can only see it if it's explored
                    if map[x][y].explored:
                    #it's out of the player's FOV
                        if wall:
                            libtcod.console_set_char_background(con, x, y, libtcod.darkest_grey, libtcod.BKGND_SET)
                        else:
                            libtcod.console_set_char_background(con, x, y, libtcod.darkest_sepia, libtcod.BKGND_SET)
                else:
                    #it's visible
                    if wall:
                        libtcod.console_set_char_background(con, x, y, libtcod.grey, libtcod.BKGND_SET )
                    else:
                        libtcod.console_set_char_background(con, x, y, libtcod.sepia, libtcod.BKGND_SET )
                    map[x][y].explored = True

    #draw all objects in the list, except the player. we want it to
    #always appear over all other objects! so it's drawn later.
    for object in objects:
        if object != player:
            object.draw()
    player.draw()

    libtcod.console_blit(con, 0, 0, var.MAP_WIDTH, var.MAP_HEIGHT, 0, 0, 0)

    #prepare to render the GUI panel
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    #print the game messages, one line at a time
    y = 1
    for (line, color) in game_msgs:
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, var.MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1
 
    #show the player's stats
    render_bar(1, 1, var.BAR_WIDTH, 'Life', player.creature.hp, player.creature.max_hp,
        libtcod.dark_red, libtcod.darkest_red)

    render_bar(1, 3, var.BAR_WIDTH, 'Mana', player.creature.mana, player.creature.max_mana,
        libtcod.dark_violet, libtcod.darkest_violet)

    #display names of objects under the mouse
    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())
 
    #blit the contents of "panel" to the root console
    libtcod.console_blit(panel, 0, 0, var.SCREEN_WIDTH, var.PANEL_HEIGHT, 0, 0, var.PANEL_Y)

def player_move_or_attack(dx, dy):
    global fov_recompute
 
    #the coordinates the player is moving to/attacking
    x = player.x + dx
    y = player.y + dy
 
    #try to find an attackable object there
    target = None
    for object in objects:
        if object.creature and object.x == x and object.y == y and object != player:
            target = object
            break
 
    #attack if target found, move otherwise
    if target is not None:
        player.creature.attack(target)
    else:
        player.move(dx, dy)
        fov_recompute = True

#####Controls#####

def handle_keys():
    global fov_recompute, keys
 
    #key = libtcod.console_check_for_keypress()  #real-time
    #key = libtcod.console_wait_for_keypress(True)  #turn-based
 
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
 
    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit'  #exit game
    
    if game_state == 'playing':
        #movement keys
        if key.vk==libtcod.KEY_KP8:
            player_move_or_attack(0, -1)
     
        elif key.vk==libtcod.KEY_KP2:
            player_move_or_attack(0, 1)
     
        elif key.vk==libtcod.KEY_KP4:
            player_move_or_attack(-1, 0)
     
        elif key.vk==libtcod.KEY_KP6:
            player_move_or_attack(1, 0)

        elif key.vk==libtcod.KEY_KP7:
            player_move_or_attack(-1, -1)
     
        elif key.vk==libtcod.KEY_KP9:
            player_move_or_attack(1, -1)
     
        elif key.vk==libtcod.KEY_KP1:
            player_move_or_attack(-1, 1)
     
        elif key.vk==libtcod.KEY_KP3:
            player_move_or_attack(1, 1)

        elif key.vk==libtcod.KEY_KP5:
            pass

        else:
            #test for other keys
            key_char = chr(key.c)
 
            if key_char == ',':
                #pick up an item
                for object in objects:  #look for an item in the player's tile
                    if object.x == player.x and object.y == player.y and object.item:
                        object.item.pick_up()
                        break

            if key_char == 'i':
                #show the inventory; if an item is selected, use it
                chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.use()

            if key_char == 'z':
                #show the spellbook; if a spell is selected, use it
                chosen_spell = spellbook_menu('Press the key next to a spell to cast it, or any other to cancel.\n')
                if chosen_spell is not None:
                    chosen_spell.use()

            if key_char == 'd':
                #show the inventory; if an item is selected, drop it
                chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.drop()

            if key_char == '<':
                #go up stairs, if the player is on them
                if stairs.x == player.x and stairs.y == player.y:
                    next_level()

            if key_char == 'c':
                #show character information
                level_up_xp = var.LEVEL_UP_BASE + player.level * var.LEVEL_UP_FACTOR
                msgbox('Character Information\n\nLevel: ' + str(player.level) +
                    '\nExperience: ' + str(player.creature.xp) +
                    '\nExperience to level up: ' + str(level_up_xp) +
                    '\n\nLife: ' + str(player.creature.max_hp) +
                    '\n\nMana Capacity: ' + str(player.creature.max_mana) +
                    '\nMelee Attack: ' + str(player.creature.power) +
                    '\nArmor: ' + str(player.creature.armor)
                    ,var.CHARACTER_SCREEN_WIDTH)

            return 'didnt-take-turn'

def random_choice_index(chances):  #choose one option from list of chances, returning its index
    #the dice will land on some number between 1 and the sum of the chances
    dice = libtcod.random_get_int(0, 1, sum(chances))
 
    #go through all chances, keeping the sum so far
    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w
 
        #see if the dice landed in the part that corresponds to this choice
        if dice <= running_sum:
            return choice
        choice += 1

def random_choice(chances_dict):
    #choose one option from dictionary of chances, returning its key
    chances = chances_dict.values()
    strings = chances_dict.keys()

    return strings[random_choice_index(chances)]

def next_level():
    global dungeon_level
    #advance to the next level
    message('You take a moment to rest, and recover your strength.', libtcod.light_violet)
    player.creature.heal(player.creature.max_hp / 2)  #heal the player by 50%
 
    message('After a rare moment of peace, you descend deeper into the heart of the dungeon...', libtcod.red)
    dungeon_level += 1
    make_map()  #create a fresh new level!
    initialize_fov()

def menu(header, options, width):
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')
    #calculate total height for the header (after auto-wrap) and one line per option
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, var.SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
    height = len(options) + header_height
    
    #create an off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)
 
    #print the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    #print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

   #blit the contents of "window" to the root console
    x = var.SCREEN_WIDTH/2 - width/2
    y = var.SCREEN_HEIGHT/2 - height/2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    #present the root console to the player and wait for a key-press
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

    #convert the ASCII code to an index; if it corresponds to an option, return it
    index = key.c - ord('a')
    #convert the ASCII code to an index; if it corresponds to an option, return it
    index = key.c - ord('a')
    if index >= 0 and index < len(options): return index
    return None

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    #render a bar (HP, experience, etc). first calculate the width of the bar
    bar_width = int(float(value) / maximum * total_width)
 
    #render the background first
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)
 
    #now render the bar on top
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    #finally, some centered text with the values
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
        name + ': ' + str(value) + '/' + str(maximum))

def message(new_msg, color = libtcod.white):
    #split the message if necessary, among multiple lines
    new_msg_lines = textwrap.wrap(new_msg, var.MSG_WIDTH)
 
    for line in new_msg_lines:
        #if the buffer is full, remove the first line to make room for the new one
        if len(game_msgs) == var.MSG_HEIGHT:
            del game_msgs[0]
 
        #add the new line as a tuple, with the text and the color
        game_msgs.append( (line, color) )

def get_names_under_mouse():
    global mouse
 
    #return a string with the names of all objects under the mouse
    (x, y) = (mouse.cx, mouse.cy)
    
    #create a list with the names of all objects at the mouse's coordinates and in FOV
    names = [obj.name for obj in objects
        if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y)]

    names = ', '.join(names)  #join the names, separated by commas
    return names.capitalize()

def main_menu():
    img = libtcod.image_load(random.choice(var.title_screen_choices))
 
    while not libtcod.console_is_window_closed():
        #show the background image, at twice the regular console resolution
        libtcod.image_blit_2x(img, 0, 0, 0)

        #show the game's title, and some credits!
        libtcod.console_set_default_foreground(0, libtcod.light_yellow)
        libtcod.console_print_ex(0, var.SCREEN_WIDTH/2, var.SCREEN_HEIGHT/2-4, libtcod.BKGND_NONE, libtcod.CENTER,
            'Etherian Chronicles')
        libtcod.console_print_ex(0, var.SCREEN_WIDTH/2, var.SCREEN_HEIGHT-2, libtcod.BKGND_NONE, libtcod.CENTER,
            'By ACG')
 
        #show options and wait for the player's choice
        choice = menu('', ['Play a new game', 'Continue last game', 'Quit'], 24)

        if choice == 0:  #new game
            new_game()
            play_game()
        if choice == 1:  #load last game
            try:
                load_game()
            except:
                msgbox('\n No saved game to load.\n', 24)
                continue
            play_game()
        elif choice == 2:  #quit
            break

def msgbox(text, width=50):
    menu(text, [], width)  #use menu() as a sort of "message box"

def check_level_up():
    #see if the player's experience is enough to level-up
    level_up_xp = var.LEVEL_UP_BASE + player.level * var.LEVEL_UP_FACTOR
    if player.creature.xp >= level_up_xp:
        #it is! level up
        player.level += 1
        player.creature.xp -= level_up_xp
        message('Your battle skills grow stronger! You reached level ' + str(player.level) + '!', libtcod.yellow)
        choice = None
        while choice == None:  #keep asking until a choice is made
            choice = menu('Level up! Choose a stat to raise:\n',
                ['+2 Life, from ' + str(player.creature.base_max_hp),
                '+2 Mana Capacity, from ' + str(player.creature.base_max_mana)
                ], var.LEVEL_SCREEN_WIDTH)
 
        if choice == 0:
            player.creature.base_max_hp += 2
            player.creature.hp += 2
        elif choice == 1:
            player.creature.base_mana += 2

def initialize_fov():
    global fov_recompute, fov_map
    fov_recompute = True

    libtcod.console_clear(con)  #unexplored areas start black (which is the default background color)

    #create the FOV map, according to the generated map
    fov_map = libtcod.map_new(var.MAP_WIDTH, var.MAP_HEIGHT)
    for y in range(var.MAP_HEIGHT):
        for x in range(var.MAP_WIDTH):
            libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)

#############################################
# Title Screen Functions
#############################################

#####Saving/Loading#####

def load_game():
    #open the previously saved shelve and load the game data
    global map, objects, player, inventory, game_msgs, game_state
 
    file = shelve.open('savegame', 'r')
    map = file['map']
    objects = file['objects']
    player = objects[file['player_index']]  #get index of player in objects list and access it
    inventory = file['inventory']
    game_msgs = file['game_msgs']
    game_state = file['game_state']
    stairs = objects[file['stairs_index']]
    dungeon_level = file['dungeon_level']
    file.close()
 
    initialize_fov()

def save_game():
    #open a new empty shelve (possibly overwriting an old one) to write the game data
    file = shelve.open('savegame', 'n')
    file['map'] = map
    file['objects'] = objects
    file['player_index'] = objects.index(player)  #index of player in objects list
    file['inventory'] = inventory
    file['game_msgs'] = game_msgs
    file['game_state'] = game_state
    file['stairs_index'] = objects.index(stairs)
    file['dungeon_level'] = dungeon_level
    file.close()


#####Starting a New Game#####

def new_game():
    global player, inventory, spellbook, game_msgs, game_state, dungeon_level
 
    #create object representing the player
    creature_component = Creature(hp=30, mana=30, armor=0, power=3, xp=0, death_function=player_death)
    player = Object(0, 0, '@', 'player', libtcod.white, blocks=True, creature=creature_component)
 
    player.level = 1
 
    #generate map (at this point it's not drawn to the screen)
    dungeon_level = 1
    make_map()
    initialize_fov()
 
    game_state = 'playing'
    inventory = []
    spellbook = []
 
    #create the list of game messages and their colors, starts empty
    game_msgs = []
 
    #a warm welcoming message!
    message('Welcome to Etheria! May you last longer than your predecessor...', libtcod.red)

    #initial spell: a lightning bolt
    effect = cast_lightning()
    spell = Spell('lightning bolt', source=player, cost=1, use_function=effect)
    spellbook.append(spell)

    #initial equipment: a dagger
    #equipment_component = Equipment(slot='right hand', power_bonus=2)
    #obj = Object(0, 0, '-', 'dagger', libtcod.sky, equipment=equipment_component)
    #inventory.append(obj)
    #equipment_component.equip()
    #obj.always_visible = True

def play_game():
    global key, mouse
 
    player_action = None
 
    mouse = libtcod.Mouse()
    key = libtcod.Key()
    while not libtcod.console_is_window_closed():
        #render the screen
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
        render_all()
 
        libtcod.console_flush()

        #upkeep phase
        check_level_up()
 
        #erase all objects at their old locations, before they move
        for object in objects:
            object.clear()
 
        #handle keys and exit game if needed
        player_action = handle_keys()
        if player_action == 'exit':
            save_game()
            break
 
        #let monsters take their turn
        if game_state == 'playing' and player_action != 'didnt-take-turn':
            for object in objects:
                if object.ai:
                    object.ai.take_turn()

#############################################
# Initialization & Main Loop
#############################################
 
libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(var.SCREEN_WIDTH, var.SCREEN_HEIGHT, 'Etherian Chronicles', False)
libtcod.sys_set_fps(var.LIMIT_FPS)
con = libtcod.console_new(var.MAP_WIDTH, var.MAP_HEIGHT)
panel = libtcod.console_new(var.SCREEN_WIDTH, var.PANEL_HEIGHT)

main_menu()
