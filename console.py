import libtcodpy as lib

#-----------------------------------------------------------
# This general-purpose module renders an x-y array as tiles.
#-----------------------------------------------------------

def write_array_to_background(array,console):
    """Writes an array of colors to the background of a console"""
    #Get the dimensions array.
    map_width = len(array)
    map_height = len(array[0])
    #Iterate through the elements of the array and write them to the console.
    for x0 in range(map_width):
        for x1 in range(map_height):
            color = array[x0][x1]
            lib.console_set_char_background(console,x0,x1,color,lib.BKGND_SET)
    #return the resulting console for use in another function
    return console

def write_array_to_foreground(array,console):
    """Writes an array of [color,character] pairs to the foreground of a console"""
    #Define the dimensions of the screen.
    map_width = len(array)
    map_height = len(array[0])
    #Iterate through the elements of the array and write them to the console.
    for x0 in range(map_width):
        for x1 in range(map_height):
            color = array[x0][x1][0]
            character = str(array[x0][x1][1])
            lib.console_set_default_foreground(console, color)
            lib.console_put_char(console,x0,x1,character,lib.BKGND_NONE)
    #return the resulting console for use in another function
    return console

def initialize_console(font,dimensions,window_title,fps=20):
    """Creates the console window"""
    #Derive width and height
    width = dimensions[0]
    height = dimensions [1]
    #Initialize console
    lib.console_set_custom_font(font, lib.FONT_TYPE_GREYSCALE | lib.FONT_LAYOUT_TCOD)
    lib.console_init_root(width,height,window_title, False)
    lib.sys_set_fps(fps)

def tint_tile(coordinates,color,console):
    """Multiplies background color of one tile by another color. Does not affect foreground"""
    #Define location
    x0 = coordinates[0]
    x1 = coordinates[1]
    #Modify the background color
    lib.console_set_char_background(console,x0,x1,color,lib.BKGND_MULTIPLY)




###Test values###
def test():
    con = lib.console_new(4,4)
    red = lib.red
    blue = lib.blue
    black = lib.black
    font = 'terminal10x10_gs_tc.png'
    array = [[red,blue,red,blue],
             [blue,red,blue,red],
             [red,blue,red,blue],
             [blue,red,blue,red]]
    array2 = [[[blue,1],[red,0],[blue,1],[red,0]],
               [[red,0],[blue,1],[red,0],[blue,1]],
               [[blue,1],[red,0],[blue,1],[red,0]],
               [[red,0],[blue,1],[red,0],[blue,1]]]
    initialize_console(font,[4,4],'test')
    write_array_to_background(array,con)
    write_array_to_foreground(array2,con)
    tint_tile([0,0],lib.silver,con)
    while True:
        lib.console_flush()
        lib.console_blit(con,0,0,4,4,0,0,0)
        

#test()
