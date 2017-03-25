import definitions as defn
import libtcodpy as libtcod
import object_classes as obcl
import map_functions as mpfn
import inventory_functions as infn
import math
import textwrap
import random
import gui
import controls as ctrl
import dungeon_generator as dgen
import spell_functions as spfn
import title_screen as tit
import game

#############################################
# Initialization & Main Loop
#############################################
 
libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(defn.SCREEN_WIDTH, defn.SCREEN_HEIGHT, 'Etherian Chronicles', False)
libtcod.sys_set_fps(defn.LIMIT_FPS)

tit.main_menu()
