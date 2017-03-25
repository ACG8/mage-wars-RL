import map_generator as mgen
import console as con
import libtcodpy as lib

dic1 = {0 : lib.sepia,
        1 : lib.black,
        2 : lib.grey,
        3 : lib.blue,
        4 : lib.blue,
        5 : lib.red,
        6 : lib.green,
        7 : lib.white,
        }
dic2 = {0 : [lib.dark_sepia,'.'],
        1 : [lib.black,' '],
        2 : [lib.dark_grey,'#'],
        3 : [lib.dark_blue,'+'],
        4 : [lib.dark_blue,'+'],
        5 : [lib.dark_red,'+'],
        6 : [lib.dark_green,'\"'],
        7 : [lib.blue,'#'],
        }
x = 48
y = 38
tmap = mgen.dMap()
tmap.makeMap(x,y,110,10,60)
bArray = [[1 for x1 in range(y)] for x0 in range(x)]
fArray = [[1 for x1 in range(y)] for x0 in range(x)]
for k in range(y):
    for j in range(x):
        bArray[j][k] = dic1[tmap.mapArr[k][j]]
        fArray[j][k] = dic2[tmap.mapArr[k][j]]

cons = lib.console_new(x,y)
font = 'terminal10x10_gs_tc.png'
con.initialize_console(font,[x,y],'test')
con.write_array_to_background(bArray,cons)
con.write_array_to_foreground(fArray,cons)
while True:
    lib.console_flush()
    lib.console_blit(cons,0,0,x,y,0,0,0)
