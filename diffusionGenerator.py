#----------------------------------------------------------
# This algorithm generates a normal dungeon using diffusion
#----------------------------------------------------------

import random

def generateMap(dimensions):
    """Creates a dungeon via diffusion"""
    #Definitions
    X0,X1 = dimensions
    array = [['?' for x1 in range(X1)] for x0 in range(X0)]
    #For now, hardcode room/corridor sizes,all have equal probabilities
    #minimum size of 3
    maxSize = 7
    numFeatures = 20

    #Create a seed of 1 square
    s0,s1 = random.randrange(X0),random.randrange(X1)
    array[s0][s1] = '.'
    
    
    for i in range(numFeatures):
        F0,F1 = random.randrange(maxSize)+3,random.randrange(maxSize)+3
        feature = createFeature((F0,F1))
        findLocation(array,feature)
        #placeFeature(array,feature)

    for i in range(X0):
        for j in range(X1):
            if array[i][j] == '?':
                array[i][j] = '#'

    return array

def createFeature(dimensions):
    F0,F1 = dimensions
    featureType = random.choice(['room','vcorridor','hcorridor'])
    feature = {
        'room' : [['.' for x1 in range(F1)] for x0 in range(F0)],
        'vcorridor' : [['.' for x1 in range(F1)]],
        'hcorridor' : [['.'] for x0 in range(F0)]
        }[featureType]
    return feature

def findLocation(array,feature):
    """Finds an acceptable location for the feature in the array and places it there"""
    X0,X1 = len(array),len(array[0])
    F0,F1 = len(feature),len(feature[0])

    s0,s1 = random.randrange(X0),random.randrange(X1)
    
    tries = 999
    directions = [[1,0],[-1,0],[0,1],[0,-1]]
    
    while tries>0:
        direction = random.choice(directions)
        if (0<=s0+direction[0]<X0) and (0<=s1+direction[1]<X1):
            s0,s1 = s0+direction[0],s1+direction[1]
            check = checkLocation((s0,s1),array,feature)
            if check:
                for i in range(F0):
                    for j in range(F1):
                        array[s0][s1] = feature[i][j]
                #create a door somewhere on the boundary, make the rest into walls
                random.shuffle(check)
                d0,d1 = check[0]
                array[d0][d1] = '+'
                check.remove((d0,d1))
                if len(check):
                    for location in check:
                        w0,w1 = location
                        #might add random window placement later
                        array[d0][d1] = '#'
                tries = 0
        tries -= 1
                        

def checkLocation(location,array,feature):
    """Checks to see if the given coordinates are legal for placement. If it is, returns the connection cells"""
    X0,X1 = len(array),len(array[0])
    x0,x1 = location
    F0,F1 = len(feature),len(feature[0])

    #First, make sure feature fits within map!
    if x0+F0>X0 or x1+F1>X1:
        return False

    #Next, check to make sure feature does not overlap existing features.
    for f0 in range(F0):
        for f1 in range(F1):
            c0,c1 = x0+f0,x1+f1
            if array[c0][c1] != '?':
                return False
    
    #Next, compile a list of open frontier cells
    frontier = []
    for f0 in range(F0):
        for f1 in range(F1):
            if not (0<f0<F0-1 or 0<f1<F1-1) and (feature[f0][f1] not in ['=','#']):
                frontier.append((f0,f1))
    
    #Now, compile a list of cells which are adjacent to open cells.
    connections = []
    directions = [(1,0),(-1,0),(0,1),(0,-1)]
    for cell in frontier:
        f0,f1 = cell
        c0,c1 = x0+f0,x1+f1
        for direction in directions:
            d0,d1 = direction
            e0,e1 = c0+d0,c1+d1
            if (0<=e0<X0 and 0<=e1<X1) and not (x0<=e0<=x0+F0 or x1<=e1<=x1+F1):
                if not ['?','=','#'].count(array[e0][e1]):
                    connections.append(cell)
    if len(connections):
        return connections
    
    return False
