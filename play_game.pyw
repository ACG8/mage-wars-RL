import definitions as defn
import libtcodpy as libtcod
import title_screen as tit
import sys

#avoid recursion limit on saving
sys.setrecursionlimit(99999)

#############################################
# Initialization & Main Loop
#############################################

libtcod.console_set_custom_font('terminal10x10_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(defn.SCREEN_WIDTH, defn.SCREEN_HEIGHT, 'Mage Wars RL', False)
libtcod.sys_set_fps(defn.LIMIT_FPS)

tit.main_menu()
