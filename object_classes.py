import definitions as defn
import libtcodpy as libtcod
import gui
import math
import random
import map_functions as mpfn
import foo_dictionary as fdic
import attack_dictionary as adic
import game
import equipment_dictionary as edic
import data_methods as data
import dijkstra as djks

class Object:
    #this is a generic object: the player, a monster, an item, the stairs...
    #it's always represented by a character on screen.
    def __init__(self, x, y, char, name, color, description=None, blocks=False, always_visible=False, creature=None, ai=None, item=None, equipment=None, traits=[]):

        self.always_visible = always_visible
        self.name = name
        self.blocks = blocks
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.description = description
        self.base_traits = traits

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

    @property
    def traits(self):
        bonus_traits = []
        bonus_sources = edic.get_all_equipped(self) #+enchantments + conditions, etc.
        if bonus_sources:
            for obj in bonus_sources:
                bonus_traits += obj.trait_bonus
        traits = self.base_traits + bonus_traits
        return traits

    def describe(self):
        #render the screen. this erases the inventory and shows the names of objects under the mouse.
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,defn.key,defn.mouse)
        game.render_all()
        gui.msgbox(self.description)
 
    def move(self, dx, dy):
        if not mpfn.is_blocked(self.x + dx, self.y + dy):
        #move by the given amount
            self.x += dx
            self.y += dy
 
    def draw(self):
        #set the color and then draw the character that represents this object at its position
        #only show if it's visible to the player; or it's set to "always visible" and on an explored tile
        if (libtcod.map_is_in_fov(defn.fov_map, self.x, self.y) or (self.always_visible and defn.dungeon[self.x][self.y].explored)):
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
        if distance != 0:
            dx = int(round(dx / distance))
            dy = int(round(dy / distance))
        else:
            dx = 0
            dy = 0
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
    def __init__(self, hp, mana, channeling, armor, xp, attacks, defenses = [], death_function=None):
        self.death_function = death_function
        self.base_max_mana = mana
        self.mana = mana
        self.base_max_hp = hp
        self.hp = hp
        self.base_armor = armor
        self.xp = xp
        self.base_attacks = attacks
        self.channeling = channeling
        self.base_defenses = defenses
        #initialize a turn counter. When counter reaches 0, action may be taken. Thus, different lengths of actions may be taken.
        self.turn_counter = 0

    @property
    def defenses(self):
        bonus_defenses = []
        bonus_sources = edic.get_all_equipped(self.owner) #+enchantments + conditions, etc.
        if bonus_sources:
            for obj in bonus_sources:
                bonus_defenses += [obj.defense]
        defenses = self.base_defenses + bonus_defenses
        if defenses:
            return defenses
        return None

    @property
    def attacks(self):
        bonus_attacks = []
        bonus_sources = edic.get_all_equipped(self.owner) #+enchantments + conditions, etc.
        if bonus_sources:
            for obj in bonus_sources:
                bonus_attacks += obj.attacks
        attacks = self.base_attacks + bonus_attacks
        return attacks

    @property
    def active_attack(self):
        if self.owner == defn.player:
            equipment = edic.get_equipped_in_slot(defn.player, 'right hand')
            if equipment and equipment.attacks:
                return equipment.attacks[0]
        return self.attacks[0]

    #returns attack bonus to [melee, range]
    @property
    def attack_bonus(self):
        #compute bonus to attack
        melee_bonus = data.sum_values_from_list(self.owner.traits,'melee +')
        range_bonus = data.sum_values_from_list(self.owner.traits,'range +')
        return [melee_bonus, range_bonus]

    @property
    def armor(self):  #return actual armor, by summing up the bonuses from all equipped items
        armor_bonus = data.sum_values_from_list(self.owner.traits,'armor +')
        return self.base_armor + armor_bonus

    @property
    def max_hp(self):  #return actual max_hp, by summing up the bonuses from all equipped items
        life_bonus = data.sum_values_from_list(self.owner.traits,'life +')
        return self.base_max_hp + life_bonus
 
    @property
    def max_mana(self):  #return actual max_hp, by summing up the bonuses from all equipped items
        mana_bonus = data.sum_values_from_list(self.owner.traits,'mana +')
        return self.base_max_mana + mana_bonus

    def adjust_turn_counter(self, turns):
        self.turn_counter = max(self.turn_counter + turns,0)

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

    def attack(self, target, attack, is_counterstrike=None):
        arg = adic.attk_dict[attack]
        if 'melee' in arg['range'][0]:
            dice_bonus = self.attack_bonus[0]
        if 'ranged' in arg['range'][0]:
            dice_bonus = self.attack_bonus[1]
        attack = adic.get_attack(arg['name'])
        attack.is_counterstrike = is_counterstrike
        attack.dice_bonus = dice_bonus
        attack.declare_attack(self.owner, target)

    def heal(self, amount):
        #heal by the given amount, without going over the maximum
        #note: need to do periodic check, in case player loses life without taking damage
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def spend_mana(self, cost):
        #spend mana if possible.
        if self.mana - cost >= 0:
            self.mana -= cost
        else:
            return 'cancelled'

def get_adjacent_tiles(x,y):
    #returns a list of non-blocked adjacent tiles, including current tile.
    adjacent_tiles = []
    for j in range(defn.MAP_HEIGHT):
        for i in range(defn.MAP_WIDTH):
            if abs(x-i) <= 1 and abs(y-j) <=1 and not defn.dungeon[i][j].blocked:
                adjacent_tiles.append(defn.dungeon[i][j])

    return adjacent_tiles
    
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
    def __init__(self, use_function=None, parameters=None):
        self.use_function = use_function
        self.parameters = parameters
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
            if equipment and edic.get_equipped_in_slot(defn.player, equipment.slot) is None:
                equipment.equip()
    def use(self):
        #note: name is just so that certain use functions can be generalized. Not necessary for all purposes.
        #special case: if the object has the Equipment component, the "use" action is to equip/dequip
        if self.owner.equipment:
            self.owner.equipment.toggle_equip()
            return
        #just call the "use_function" if it is defined
        #if self.use_function(name) is None:
         #   gui.message('The ' + self.owner.name + ' cannot be used.')
        #else:
        if self.use_function(self.parameters) != 'cancelled':
            defn.inventory.remove(self.owner)  #destroy after use, unless it was cancelled for some reason
        else: return 'cancelled'

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
    def __init__(self, slot, trait_bonus=[], attacks=[], defense = None):
        self.slot = slot
        self.trait_bonus = trait_bonus
        self.is_equipped = False
        self.attacks = attacks
        self.defense = defense
 
    def toggle_equip(self):  #toggle equip/dequip status
        if self.is_equipped:
            self.dequip()
        else:
            self.equip()
 
    def equip(self):
        #equip object and show a message about it
        #if the slot is already being used, dequip whatever is there first
        old_equipment = edic.get_equipped_in_slot(defn.player, self.slot)
        if old_equipment is not None:
            old_equipment.dequip()
        self.is_equipped = True
        gui.message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', libtcod.light_green)
 
    def dequip(self):
        #dequip object and show a message about it
        if not self.is_equipped: return
        self.is_equipped = False
        gui.message('Removed ' + self.owner.name + ' from ' + self.slot + '.', libtcod.light_yellow)

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
    gui.message('The ' + monster.name + ' gurgles as its life-blood spills upon the sands!', libtcod.orange)
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.creature = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.send_to_back()


