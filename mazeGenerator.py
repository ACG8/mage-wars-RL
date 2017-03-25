#---------------------------------
# This module generates a 2D maze.s
#---------------------------------

import random as rand

def generateMaze(dimensions):
    """Generates a maze, represented by a ( # . ) array"""
    X0,X1 = dimensions[0],dimensions[1]

    #Create an array of ?
    array = [['?' for x1 in range(X1)] for x0 in range(X0)]

    #Create an empty list of "frontier" cells
    frontier = []

    #Choose an origin at random
    origin = (rand.randint(0,X0-1),rand.randint(0,X1-1))
    frontier.extend(carve(origin,array))
    while len(frontier):
        rand.shuffle(frontier)
        choice = frontier[0]
        if check(choice,array):
            frontier.extend(carve(choice,array))
        else:
            harden(choice,array)
        frontier.remove(choice)

    #Harden remaining undetermined cells
    for i in range(X0):
        for j in range(X1):
            if array[i][j] == '?':
                harden((i,j),array)

    return array

def harden(coordinates,array,windowprob = 2):
    """Make the cell at location a wall, or occasionally a window"""
    x0,x1 = coordinates
    roll = rand.randrange(100)
    if roll < windowprob:
        array[x0][x1] = '#'
    else:
        array[x0][x1] = ' '

def carve(coordinates,array):
    """Make the cell at location a space and returns a list of adjacent frontier cells"""
    x0,x1 = coordinates
    X0,X1 = len(array),len(array[0])

    newfront = []
    array[x0][x1] = '.'
    
    
    for dx in [(1,0),(-1,0),(0,1),(0,-1)]:
        dx0,dx1 = dx
        if (0<x0+dx0<X0-1) and (0<x1+dx1<X1-1):
            if array[x0+dx0][x1+dx1] == '?':
                array[x0+dx0][x1+dx1] = ','
                newfront.append((x0+dx0,x1+dx1))

    rand.shuffle(newfront)
    return newfront

def check(coordinates,array):
    """Checks whether or not cell can become open. If it forms a square, it can't"""
    x0,x1 = coordinates
    X0,X1 = len(array),len(array[0])

    #Prohibit squares/diagonals
    for dx in [(1,1),(-1,-1),(-1,1),(1,-1)]:
        dx0,dx1 = dx
        if (0<=x0+dx0<X0) and (0<=x1+dx1<X1):
            if not (array[x0+dx0][x1] == '.' or array[x0][x1+dx1] == '.') and array[x0+dx0][x1+dx1] == '.':
                return False

    #Discourage linking existing passages
    connections = 0
    for dx in [(1,0),(-1,0),(0,1),(0,-1)]:
        dx0,dx1 = dx
        if (0<=x0+dx0<X0) and (0<=x1+dx1<X1):
            if array[x0+dx0][x1+dx1] == '.':
                connections += 1

    if connections != 1:
        return False
    
    return True
