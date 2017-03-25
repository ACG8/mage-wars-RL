#--------------------------------------------------------
# This module contains functions for manipulating arrays.
#--------------------------------------------------------

def overlayArray(base,overlay,coordinates):
    """Overwrites part of the base array with the overlay array at given location. Spaces are treated as clear."""
    #Define dimensions and coordinates
    x0,x1 = coordinates[0],coordinates[1]
    bX0,bX1 = len(base),len(base[0])
    oX0,oX1 = len(overlay),len(overlay[0])

    #Return the original array if part of overlay is outside base
    if (x0+oX0>bX0) or (x1+oX1>bX1):
        return base

    for i in range(oX0):
        for j in range(oX1):
            if overlay[i][j] != ' ':
                base[x0+i][x1+j] = overlay[i][j]

    return base
