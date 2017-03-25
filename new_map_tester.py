import map_generator as mgen
import console as con
import libtcodpy as lib
import txt_interpreter as txt
import arrayTools as arr
import mazeGenerator as maz
import caveGenerator as cave
import diffusionGenerator as diff

#roomModule = txt.importArray('vaults/vault1.txt')
#array = [['#' for x1 in range(36)] for x1 in range(48)]
#array = arr.overlayArray(array,roomModule,[3,3])
#array = arr.overlayArray(array,roomModule,[4,4])

array = maz.generateMaze([36,48])
#array = cave.generateCave((36,48),(36*24-20))
#array = diff.generateMap((36,48))

def test1():
    dic1 = {'.' : lib.sepia,
            '#' : lib.dark_grey,
            '=' : lib.light_blue,
            '?' : lib.black,
            '+' : lib.yellow
            }
    dic2 = {'.' : [lib.dark_sepia,'.'],
            '#' : [lib.darker_grey,'#'],
            '=' : [lib.blue,'='],
            '?' : [lib.black,' '],
            '+' : [lib.white,'+']
            }
    x = 48
    y = 38
    tmap = mgen.dMap()
    #tmap.makeMap(x,y,110,10,60)
    #array = txt.importArray('vaults/cross.txt')
    x = len(array)
    y = len(array[0])
    tmap.mapArr = array
    bArray = [[1 for x1 in range(y)] for x0 in range(x)]
    fArray = [[1 for x1 in range(y)] for x0 in range(x)]
    for k in range(y):
        for j in range(x):
            bArray[j][k] = dic1[tmap.mapArr[j][k]]
            fArray[j][k] = dic2[tmap.mapArr[j][k]]

    cons = lib.console_new(x,y)
    font = 'terminal10x10_gs_tc.png'
    con.initialize_console(font,[x,y],'test')
    con.write_array_to_background(bArray,cons)
    con.write_array_to_foreground(fArray,cons)
    while True:
        lib.console_flush()
        lib.console_blit(cons,0,0,x,y,0,0,0)

    
