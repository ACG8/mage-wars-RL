import definitions as defn
import dijkstra as djks
import random
import libtcodpy as libtcod

class Ai:
    def __init__(self, personality, traits, senses):
        self.personality = personality
        self.traits = traits
        self.senses = senses

    def can_detect_player(self):
        #this function returns true if this creature can detect the target.
        actor = self.owner
        #currently, let's just stick with hearing and sight. For sight, we'll just check for FOV right now.
        if libtcod.map_is_in_fov(defn.fov_map, actor.x, actor.y):
            return True
        if defn.dijkstra_player_map.array[actor.x][actor.y] <= self.senses['hearing']:
            return True
        return False
        
    def take_turn(self):
        #a basic monster takes its turn. If you can see it, it can see you
        monster = self.owner

        #for now, ranged enemies only attack player. Will revamp AI later. Note that ranged allies will attack player w/ current programming.
        
        for attack in self.owner.creature.attacks:
            if attack.range['type'] == 'ranged' and monster.distance_to(defn.player) <= attack.range['distance'] and libtcod.map_is_in_fov(defn.fov_map, monster.x, monster.y):
                monster.creature.attack(defn.player,attack)
                monster.creature.adjust_turn_counter(attack.speed['turns'])
                return None
        destination = self.find_best_move()
        monster.creature.try_to_move(destination.x,destination.y)

    def find_best_move(self):
        #Scans surrounding tiles, weights them, and returns the best one. Currently just evaluates distance between tile and player. x and y are the current location from which the best move is being computed.
        #later I can alter it to give different values based on environment, using an AI dictionary
        #uses dijkstra weighted maps. currently just looks for player.
        #or statement leads to hearing based on dijkstra distance from player; some creatures can hear
        #hearing disabled for now
        actor = self.owner

        #if libtcod.map_is_in_fov(defn.fov_map, creature.x, creature.y):

        #temporary disable for testing
        #return defn.dungeon[creature.x][creature.y]
        #note: owner of ai should really be creature, not object
        #ai for dungeon denizens
        if self.owner.creature.alignment == 'dungeon':

            player_weight = 0.0
            #prefers to stay out of FOV if possible.
            fov_weight = 0.1

            dijkstra_map = djks.Map([])
            if self.can_detect_player():
                player_weight = 1.0
                #scared creatures run from player and try to stay out of view
                if self.owner.creature.hp <= self.owner.creature.max_hp * self.personality['fear']:
                    player_weight = -1.0
                    fov_weight = 1.0
                
                            
            for tile in defn.dungeon_unblocked_list:
                dijkstra_map.array[tile.x][tile.y] = (
                    defn.dijkstra_player_map.array[tile.x][tile.y] * player_weight +
                    defn.dijkstra_fov_map.array[tile.x][tile.y] * fov_weight) #+
                    #0.5*defn.dijkstra_monster_map.array[tile.x][tile.y])
                #avoid other objects - we'll disable this for now
               # for obj in defn.objects:
              #      if obj.blocks:
                  #      dijkstra_map.array[obj.x][obj.y] += 1
                    
            return dijkstra_map.get_next_step(self.owner.x,self.owner.y)

        #ai for allies
        if self.owner.creature.alignment == 'player':

            #changing the denominator affects how far the creature is willing to stray. Probably would work better to switch between different states (guarding, attacking, etc.) to determine weights.
            player_weight = float(defn.player.distance_to(actor))/5.0
            #high fov weight so monster remains in FOV
            fov_weight = 0.0
            monster_weight = 1.0

            dijkstra_map = djks.Map([])

            if not self.can_detect_player():
            #if the monster isn't close enough to sense the player, it makes a beeline straight for the player.
                player_weight = 1.5

            for tile in defn.dungeon_unblocked_list:
                dijkstra_map.array[tile.x][tile.y] = (
                    defn.dijkstra_player_map.array[tile.x][tile.y] * player_weight +
                    defn.dijkstra_fov_map.array[tile.x][tile.y] * fov_weight +
                    defn.dijkstra_monster_map.array[tile.x][tile.y] * monster_weight)

            return dijkstra_map.get_next_step(self.owner.x,self.owner.y)
                #avoid other objects
                #for obj in defn.objects:
                 #   if obj.blocks:
                     #   dijkstra_map.array[obj.x][obj.y] += 1
                        

#personality consists of several components:
        #fear is an index that affects how much damage (just damage for now) the monster must take before it flees, proportional to its life. A fearless monster has 0.0 fear.
        #sociability is an index indicating how much the monster wants to be near its allies.

#senses affect the monster's ability to sense the world. Should be a number indicating distance
        #sight requires LOS. Need to think more about how to implement. Probably uses straight-line distance and requires LOS, but I don't want to compute LOS for monsters.
            #easiest way is to compute 2 LOS maps for player, one with infinite radius, and then just use the one
            #with the larger radius for the monsters. Actually, I could do it with just one FOV map and distance checks for the player.
        #smell at the moment affects how far away the monster can detect the player. I think a better implementation
            #might be creating a map of the player's scent and updating it differently than the current dijkstra map
            #algorithm - the player's scent could expand gradually. Or perhaps recalculating the map could occur gradually.
            # such that information might be outdated. obviously you would not want to add the scent map unless scent was actually detected.
        #want to implement sound, which could work in the same way that smell currently works (i.e. just considers steps to player)

ai_dict = {}

ai_dict['zombie'] = {
    'personality' : {
        'fear' : 0.0,
        'sociability' : 0.0},
    'traits' : ['mindless'],
    'senses' : {
        'sight' : 8,
        'smell' : 6,
        'hearing' : 8}}

ai_dict['canine'] = {
    'personality' : {
        'fear' : 0.3,
        'sociability' : 0.8},
    'traits' : [''],
    'senses' : {
        'sight' : 7,
        'smell' : 12,
        'hearing' : 9}}
