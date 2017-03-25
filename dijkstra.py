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

    #here's the plan for optimization: we simply vary the order in which tiles are scanned. Let's try alternating back and forth. If necessary, we can alternate up and down as well.

        
    def compute_map(self):

        self.array = [[ 999999
            for y in range(defn.MAP_HEIGHT)]
                for x in range(defn.MAP_WIDTH)]

        for goal in self.goals:
            self.array[goal.x][goal.y] = 0

        done = False

        #new algorithm that goes in each direction - it works! Lightning-ish fast.
        
        while True:
            change = False
            for y in range(defn.MAP_HEIGHT):
                for x in range(defn.MAP_WIDTH):
                    if not defn.dungeon[x][y].blocked:
                        minimum_neighbor = self.lowest_neighbor_value(x,y)
                        if self.array[x][y] > minimum_neighbor + 1:
                            self.array[x][y] = minimum_neighbor + 1
                            change = True
            if not change:
                break

            change = False
            for x in reversed(range(defn.MAP_WIDTH)):
                for y in reversed(range(defn.MAP_HEIGHT)):
                    if not defn.dungeon[x][y].blocked:
                        minimum_neighbor = self.lowest_neighbor_value(x,y)
                        if self.array[x][y] > minimum_neighbor + 1:
                            self.array[x][y] = minimum_neighbor + 1
                            change = True
            if not change:
                break

            change = False
            for y in reversed(range(defn.MAP_HEIGHT)):
                for x in reversed(range(defn.MAP_WIDTH)):
                    if not defn.dungeon[x][y].blocked:
                        minimum_neighbor = self.lowest_neighbor_value(x,y)
                        if self.array[x][y] > minimum_neighbor + 1:
                            self.array[x][y] = minimum_neighbor + 1
                            change = True
            if not change:
                break

            change = False
            for x in range(defn.MAP_WIDTH):
                for y in range(defn.MAP_HEIGHT):
                    if not defn.dungeon[x][y].blocked:
                        minimum_neighbor = self.lowest_neighbor_value(x,y)
                        if self.array[x][y] > minimum_neighbor + 1:
                            self.array[x][y] = minimum_neighbor + 1
                            change = True
            if not change:
                break

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
        
