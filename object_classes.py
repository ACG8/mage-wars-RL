import definitions as defn
import libtcodpy as libtcod
import gui
import math
import inventory_functions as invfn
import map_functions as mpfn
import descriptions as descr

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
        if not mpfn.is_blocked(self.x + dx, self.y + dy):
        #move by the given amount
            self.x += dx
            self.y += dy
 
    def draw(self):
        #set the color and then draw the character that represents this object at its position
        #only show if it's visible to the player; or it's set to "always visible" and on an explored tile
        if (libtcod.map_is_in_fov(defn.fov_map, self.x, self.y) or
            (self.always_visible and defn.dungeon[self.x][self.y].explored)):
            libtcod.console_set_default_foreground(defn.con, self.color)
            libtcod.console_put_char(defn.con, self.x, self.y, self.char, libtcod.BKGND_NONE)
            
    def clear(self):
        #erase the character that represents this object
        libtcod.console_put_char(defn.con, self.x, self.y, ' ', libtcod.BKGND_NONE)

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
        defn.objects.remove(self)
        defn.objects.insert(0, self)

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
        bonus = sum(equipment.power_bonus for equipment in invfn.get_all_equipped(self.owner))
        return self.base_power + bonus

    @property
    def armor(self):  #return actual armor, by summing up the bonuses from all equipped items
        bonus = sum(equipment.armor_bonus for equipment in invfn.get_all_equipped(self.owner))
        return self.base_armor + bonus

    @property
    def max_mana(self):  #return actual max_hp, by summing up the bonuses from all equipped items
        bonus = sum(equipment.max_mana_bonus for equipment in invfn.get_all_equipped(self.owner))
        return self.base_max_hp + bonus
 
    @property
    def max_hp(self):  #return actual max_hp, by summing up the bonuses from all equipped items
        bonus = sum(equipment.max_hp_bonus for equipment in invfn.get_all_equipped(self.owner))
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
                if self.owner != defn.player:  #yield experience to the player
                    defn.player.creature.xp += self.xp

    def attack(self, target):
        from action_classes import Attack
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
        if libtcod.map_is_in_fov(defn.fov_map, monster.x, monster.y):
 
            #move towards player if far away
            if monster.distance_to(defn.player) >= 2:
                monster.move_towards(defn.player.x, defn.player.y)
 
            #close enough, attack! (if the player is still alive.)
            elif defn.player.creature.hp > 0:
                monster.creature.attack(defn.player)

class ConfusedMonster:
    #AI for a temporarily confused monster (reverts to previous after a while).
    def __init__(self, old_ai, num_turns=defn.CONFUSE_NUM_TURNS):
        self.old_ai = old_ai
        self.num_turns = num_turns
 
    def take_turn(self):
        if self.num_turns > 0:  #still confused...
            #move in a random direction, and decrease the number of turns confused
            self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
            self.num_turns -= 1
 
        else:  #restore the previous AI (this one will be deleted because it's not referenced anymore)
            self.owner.ai = self.old_ai
            gui.message('The ' + self.owner.name + ' is no longer confused!', libtcod.red)

class Item:
    def __init__(self, use_function=None):
        self.use_function = use_function
    #an item that can be picked up and used.
    def pick_up(self):
        #add to the player's inventory and remove from the map
        if len(defn.inventory) >= 26:
            gui.message('Your inventory is full, cannot pick up ' + self.owner.name + '.', libtcod.red)
        else:
            defn.inventory.append(self.owner)
            defn.objects.remove(self.owner)
            gui.message('You picked up a ' + self.owner.name + '!', libtcod.green)
            #special case: automatically equip, if the corresponding equipment slot is unused
            equipment = self.owner.equipment
            if equipment and invfn.get_equipped_in_slot(equipment.slot) is None:
                equipment.equip()
    def use(self):
        #special case: if the object has the Equipment component, the "use" action is to equip/dequip
        if self.owner.equipment:
            self.owner.equipment.toggle_equip()
            return
        #just call the "use_function" if it is defined
        if self.use_function is None:
            gui.message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function() != 'cancelled':
                defn.inventory.remove(self.owner)  #destroy after use, unless it was cancelled for some reason

    def info(self):
        #just call the "use_function" if it is defined
        try:
            gui.message(descr.self.object.name)
        except:
            gui.message('Sorry - I have\'nt got around to describing this yet.')

    def drop(self):
        #add to the map and remove from the player's inventory. also, place it at the player's coordinates
        defn.objects.append(self.owner)
        defn.inventory.remove(self.owner)
        self.owner.x = defn.player.x
        self.owner.y = defn.player.y
        #special case: if the object has the Equipment component, dequip it before dropping
        if self.owner.equipment:
            self.owner.equipment.dequip()
        gui.message('You dropped a ' + self.owner.name + '.', libtcod.yellow)

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
        old_equipment = invfn.get_equipped_in_slot(self.slot)
        if old_equipment is not None:
            old_equipment.dequip()
        self.is_equipped = True
        gui.message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', libtcod.light_green)
 
    def dequip(self):
        #dequip object and show a message about it
        if not self.is_equipped: return
        self.is_equipped = False
        gui.message('Dequipped ' + self.owner.name + ' from ' + self.slot + '.', libtcod.light_yellow)

#####Note: I need to eventually move these or integrate them into the creature function

def player_death(player):
    #the game ended!
    gui.message ('You died!', libtcod.red)
    defn.game_state = 'dead'
 
    #for added effect, transform the player into a corpse!
    defn.player.char = '%'
    defn.player.color = libtcod.dark_red
 
def monster_death(monster):
    #transform it into a nasty corpse! it doesn't block, can't be
    #attacked and doesn't move
    gui.message('The ' + monster.name + ' collapses in defeat! You gain ' + str(monster.creature.xp) + ' experience points.', libtcod.orange)
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.creature = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.send_to_back()


