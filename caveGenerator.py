#---------------------------------------------------------------------
# A simple random walk dungeon generator for making cave-like dungeons
#---------------------------------------------------------------------

import random

def generateCave(dimensions,area):
    """Generates a dungeon with specified area. Do not make area larger than area given"""
    X0,X1 = dimensions
    
    #Error if area too big
    if area>X0*X1:
        return None

    array = [[' ' for x1 in range(X1)] for x0 in range(X0)]

    s0,s1 = random.randrange(X0),random.randrange(X1)

    array[s0][s1] = '.'
    area -= 1

    directions = [[1,0],[-1,0],[0,1],[0,-1]]
    
    while area>0:
        direction = random.choice(directions)
        if (0<=s0+direction[0]<X0) and (0<=s1+direction[1]<X1):
            s0,s1 = s0+direction[0],s1+direction[1]
            if array[s0][s1] == ' ':
                array[s0][s1] = '.'
                area -= 1

    return array
