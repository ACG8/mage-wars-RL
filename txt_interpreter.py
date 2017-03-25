#------------------------------------------------------------------------
# This module interprets txt files and outputs usable strings and arrays.
#------------------------------------------------------------------------

def importArray(filename):
    """Takes a txt character array and outputs a py array."""
    #Open the file
    raw = open(filename,'r')
    #Create an empty array.
    #Because of the order in which data are read, we will need to transpose it.
    transpose_array = []
    rownumber = 0
    #Fill up the transposed array, as a set of rows.
    for line in raw:
        row = []
        for char in range(len(line)):
            if line[char] != '\n':
                row.append(line[char])
        transpose_array.append(row)
        rownumber +=1
    #Get array dimensions
    X0 = len(transpose_array[0])
    X1 = len(transpose_array)
    #Untranspose array to get the array
    array = [[transpose_array[x1][x0] for x1 in range(X1)] for x0 in range(X0)]
    return array
