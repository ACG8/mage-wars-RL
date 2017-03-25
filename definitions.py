import libtcodpy as libtcod

#############################################
# Static Values
#############################################

#actual size of the window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

MAP_WIDTH = 50 #80
MAP_HEIGHT = 38

#Dungeon Generation
ROOM_MAX_SIZE = 7
ROOM_MIN_SIZE = 3
MAX_ROOMS = 20

LIMIT_FPS = 20  #20 frames-per-second maximum

#Line of Sight
FOV_ALGO = 2  #shadowcasting FOV algorithm
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

#sizes and coordinates relevant for the GUI
BAR_WIDTH = 20

STATS_WIDTH = SCREEN_WIDTH - MAP_WIDTH
STATS_HEIGHT = MAP_HEIGHT #15
STATS_Y = 0 #SCREEN_HEIGHT - PANEL_HEIGHT
STATS_X = MAP_WIDTH

MSG_Y = MAP_HEIGHT #
MSG_X = 0 #BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH #SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = SCREEN_HEIGHT - MAP_HEIGHT # PANEL_HEIGHT - 1

stats_panel = libtcod.console_new(STATS_WIDTH, STATS_HEIGHT)
message_panel = libtcod.console_new(MSG_WIDTH,MSG_HEIGHT)

INVENTORY_WIDTH = 50
SPELLBOOK_WIDTH = 50
SCHOOLS_WIDTH = 50

HEAL_AMOUNT = 4

LIGHTNING_DAMAGE = 20
LIGHTNING_RANGE = 5

CONFUSE_NUM_TURNS = 10
CONFUSE_RANGE = 8

FIREBALL_RADIUS = 3
FIREBALL_DAMAGE = 12

#experience and level-ups
LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 150
LEVEL_SCREEN_WIDTH = 40

CHARACTER_SCREEN_WIDTH = 30

#ai
#maximum tiles to seach when pathfinding
MAX_TILE_SEARCH = 50


#list of title screen graphics
title_screen_choices = [
    'beastmaster_v_warlock.png',
    'forcemaster_v_warlord.png',
    'wizard_v_priestess.png',
    'druid_v_necromancer.png']

con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
screen = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

mouse = libtcod.Mouse()
key = libtcod.Key()

#############################################
# Global Variables
#############################################

fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
fov_recompute = True
dungeon_level = 1
global player, training, stairs, game_state, game_msgs, inventory, spellbook, objects, dungeon, dungeon_unblocked_list, player_location_changed
#define dijkstra maps
global dijkstra_player_map, dijkstra_monster_map
