#actual size of the window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

MAP_WIDTH = 80
MAP_HEIGHT = 43

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 10

LIMIT_FPS = 20  #20 frames-per-second maximum

FOV_ALGO = 0  #default FOV algorithm
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

#sizes and coordinates relevant for the GUI
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT

MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

INVENTORY_WIDTH = 50
SPELLBOOK_WIDTH = 50

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

#list of title screen graphics
title_screen_choices = [
    'beastmaster_v_warlock.png',
    'forcemaster_v_warlord.png',
    'wizard_v_priestess.png',
    'druid_v_necromancer.png']

