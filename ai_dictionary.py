import definitions as defn
import dijkstra as djks
import random

class Ai:
    def __init__(self, personality, traits):
        self.personality = personality
        self.traits = traits
        
    def take_turn(self):
        #a basic monster takes its turn. If you can see it, it can see you
        monster = self.owner
        # and monster.creature:
        player_weight = 1
        if self.owner.creature.hp <= self.owner.creature.max_hp * self.personality['fear']:
                player_weight = -1
            #move towards player if far away; slow creatures move every other turn, randomly (will change). Need to fix monster-corpse problem again with monster.creature check
        if monster.distance_to(defn.player) >= 2 or player_weight == -1:
            destination = self.find_best_move()
            monster.move_towards(destination.x, destination.y)
            monster.creature.adjust_turn_counter(3)
            if monster.traits:
                if ['fast'] in monster.traits:
                    monster.creature.adjust_turn_counter(-1)
                if ['slow'] in monster.traits:
                    monster.creature.adjust_turn_counter(1)
                        
            #close enough, attack! (if the player is still alive.)
        elif defn.player.creature.hp > 0:
            #odd occasional error where monster.creature is none_type; again, the issue of the monster becoming a corpse rears its head. Must find more elegant solution.
                #current solution - attacking is the last thing the monster does.
            monster.creature.adjust_turn_counter(3)
            monster.creature.attack(defn.player,monster.creature.active_attack)

    def find_best_move(self):
        #Scans surrounding tiles, weights them, and returns the best one. Currently just evaluates distance between tile and player. x and y are the current location from which the best move is being computed.
        #later I can alter it to give different values based on environment, using an AI dictionary
        #uses dijkstra weighted maps. currently just looks for player.
        #or statement leads to hearing based on dijkstra distance from player; some creatures can hear
        #hearing disabled for now
        #if libtcod.map_is_in_fov(defn.fov_map, creature.x, creature.y):

        #temporary disable for testing
        #return defn.dungeon[creature.x][creature.y]

        dijkstra_map = djks.Map([])
        player_weight = 1
        if self.owner.creature.hp <= self.owner.creature.max_hp * self.personality['fear']:
                player_weight = -1
        
        for tile in defn.dungeon_unblocked_list:
            dijkstra_map.array[tile.x][tile.y] = defn.dijkstra_player_map.array[tile.x][tile.y]*player_weight + 0.5*defn.dijkstra_monster_map.array[tile.x][tile.y]
            #avoid other objects
            for obj in defn.objects:
                if obj.blocks:
                    dijkstra_map.array[obj.x][obj.y] += 1
                
        choices = dijkstra_map.lowest_neighbors(self.owner.x,self.owner.y)
        #if len(choices) == 1:
         #   return choices[0]
        return random.choice(choices)


#personality consists of several components:
        #fear is an index that affects how much damage (just damage for now) the monster must take before it flees, proportional to its life. A fearless monster has 0.0 fear.
        #

ai_dict = {}

ai_dict['mindless'] = {
    'personality' : {
        'fear' : 0.0},
    'traits' : ['mindless']}

ai_dict['rational'] = {
    'personality' : {
        'fear' : 0.5},
    'traits' : []}

ai_dict['scaredy-cat'] = {
    'personality' : {
        'fear' : 1.0},
    'traits' : []}
