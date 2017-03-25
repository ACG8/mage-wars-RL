import definitions as defn
import random

#the only thing that matters when initializing a dijkstra map is the goals and impassable objects

class Map:
    def __init__(self, goals):
        self.goals = goals
        self.array = [[ 999999
            for y in range(defn.MAP_HEIGHT)]
                for x in range(defn.MAP_WIDTH)]

    #goals can be objects or tiles; only the location matters

    #okay, new plan. Each map tile's dijkstra map is only computed as needed, but the maps are still associated with the tiles.
    #The first time a tile is called, the algorithm runs; other times, it just uses what is already there.
    #currently, square pattern. Later, maybe I'll make it rounded so that diagonal movements have a higher value
    def compute_map(self):

        self.array = [[ 999999
            for y in range(defn.MAP_HEIGHT)]
                for x in range(defn.MAP_WIDTH)]

        for goal in self.goals:
            self.array[goal.x][goal.y] = 0

        done = False
        
        #avoid obstacles
        #unblocked_list = defn.dungeon_unblocked_list
        #for obj in defn.objects:
         #   if obj.blocks and defn.dungeon[obj.x][obj.y] in unblocked_list:
          #      unblocked_list.remove(defn.dungeon[obj.x][obj.y])
        
        while not done:
            change = False
            for tile in defn.dungeon_unblocked_list:
                minimum_neighbor = self.lowest_neighbor_value(tile.x,tile.y)
                if self.array[tile.x][tile.y] > minimum_neighbor + 1:
                    self.array[tile.x][tile.y] = minimum_neighbor + 1
                    change = True
            if change == False:
                done = True

    def lowest_neighbor_value(self,x,y):
        neighbors = []
        for tile in defn.dungeon[x][y].adjacent_tiles:
            neighbors.append(self.array[tile.x][tile.y])
        return min(neighbors)

    def lowest_neighbors(self,x,y):
        neighbor_list = []
        lowest_neighbor_value = self.lowest_neighbor_value(x,y)
        for tile in defn.dungeon[x][y].adjacent_tiles:
            if self.array[tile.x][tile.y] == lowest_neighbor_value:
                neighbor_list.append(tile)
        return neighbor_list

    def get_next_step(self,x,y):
        choices = self.lowest_neighbors(x,y)
        return random.choice(choices)
        
