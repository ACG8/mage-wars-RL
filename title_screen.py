import definitions as defn
import libtcodpy as libtcod
import object_classes as obcl
import map_functions as mpfn
import inventory_functions as infn
import gui
import dungeon_generator as dgen
import random
import spell_functions as spfn
import game
import shelve
import spell_classes as spcl
import spell_dictionary as sdic
import creature_dictionary as cdic
import equipment_dictionary as edic
import mage_dictionary as mgdic
import attack_dictionary as adic

def main_menu():
    img = libtcod.image_load(random.choice(defn.title_screen_choices))
 
    while not libtcod.console_is_window_closed():
        #show the background image, at twice the regular console resolution
        libtcod.image_blit_2x(img, 0, 0, 0)

        #show the game's title, and some credits!
        libtcod.console_set_default_foreground(0, libtcod.light_yellow)
        libtcod.console_print_ex(0, defn.SCREEN_WIDTH/2, defn.SCREEN_HEIGHT/2-4, libtcod.BKGND_NONE, libtcod.CENTER,
            'Etherian Chronicles')
        libtcod.console_print_ex(0, defn.SCREEN_WIDTH/2, defn.SCREEN_HEIGHT-2, libtcod.BKGND_NONE, libtcod.CENTER,
            'By ACG')
 
        #show options and wait for the player's choice
        choice = gui.menu('', ['Play a new game', 'Continue last game', 'Quit'], 24)

        if choice == 0:  #new game
            new_game()
            game.play_game()
        if choice == 1:  #load last game
            try:
                load_game()
            except:
                msgbox('\n No saved game to load.\n', 24)
                continue
            game.play_game()
        elif choice == 2:  #quit
            break
    
#####Saving/Loading#####

def load_game():
    #open the previously saved shelve and load the game data
 
    file = shelve.open('savegame', 'r')
    defn.dungeon = file['map']
    defn.objects = file['objects']
    defn.player = defn.objects[file['player_index']]  #get index of player in objects list and access it
    defn.inventory = file['inventory']
    defn.game_msgs = file['game_msgs']
    defn.game_state = file['game_state']
    defn.stairs = defn.objects[file['stairs_index']]
    defn.dungeon_level = file['dungeon_level']
    file.close()
 
    mpfn.initialize_fov()

def save_game():
    #some recursive problem occurs, started after I rewrote the gui code
    #open a new empty shelve (possibly overwriting an old one) to write the game data
    file = shelve.open('savegame', 'n')
    file['map'] = defn.dungeon
    file['objects'] = defn.objects
    file['player_index'] = defn.objects.index(defn.player)  #index of player in objects list
    file['inventory'] = defn.inventory
    file['game_msgs'] = defn.game_msgs
    file['game_state'] = defn.game_state
    file['stairs_index'] = defn.objects.index(defn.stairs)
    file['dungeon_level'] = defn.dungeon_level
    file.close()

def new_game():

    #clear lists
    defn.game_msgs = []
    defn.inventory = []
    defn.spellbook = []
    defn.objects = []
    defn.dungeon = []

    gui.clear_screen()
    
    gui.msgbox('Welcome to Etheria! You have been cruelly locked in the depths of a dungeon and slated to serve as an amusement in the next round of the Mage Wars. If you can escape the dungeon and defeat your captor in the arena, you will be given your freedom. Perhaps along the way you can learn a thing or two about magic...')

    gui.clear_screen()

    chosen = None
    #while chosen == None:
    index = gui.menu('Before your adventure begins, we need to know a little more about you. What sort of mage are you?', mgdic.mages, defn.SCHOOLS_WIDTH)
    mage = mgdic.mage_dict[mgdic.mages[index]]
    mgdic.create_player(mage, 0, 0)

    dgen.make_map()
    mpfn.initialize_fov()
 
    #generate map (at this point it's not drawn to the screen)
 
    defn.game_state = 'playing'
    defn.player_location_changed = True

    game.render_all()

    # can add initialization tests here:   
