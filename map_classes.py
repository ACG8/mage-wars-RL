import definitions as defn
import libtcodpy as libtcod

class Tile:
    #a tile of the map and its properties
    def __init__(self, x, y, name, color, blocked, block_sight = None):
        self.x = x
        self.y = y
        self.name = name
        self.color = color
        self.blocked = blocked
        self.explored = False
        self.scent = 0
        self.sound = 0
        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight
        #careful - the list of adjacent tiles can only be generated after all tiles have been created.
        self.adjacent_tiles = []
        #insane idea - why not define a static dijkstra map for every unblocked tile?

    def compute_adjacent_tiles(self):
        neighbors = []
        for y in range(defn.MAP_HEIGHT):
            for x in range(defn.MAP_WIDTH):
                if abs(x-self.x) <= 1 and abs(y-self.y) <=1:
                    neighbors.append(defn.dungeon[x][y])
        self.adjacent_tiles = neighbors

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
