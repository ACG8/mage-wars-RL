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
import monster_dictionary as mdic
import equipment_dictionary as edic
import mage_dictionary as mgdic
import attack_dictionary as adic
import item_dictionary as idic
import input_text as iptext
import new_game

def main_menu():
    img = libtcod.image_load(random.choice(defn.title_screen_choices))
 
    while not libtcod.console_is_window_closed():
        #show the background image, at twice the regular console resolution
        libtcod.image_blit_2x(img, 0, 0, 0)

        #show the game's title, and some credits!
        libtcod.console_set_default_foreground(0, libtcod.light_yellow)
        libtcod.console_print_ex(0, defn.SCREEN_WIDTH/2, defn.SCREEN_HEIGHT/2-4, libtcod.BKGND_NONE, libtcod.CENTER,
            'Mage Wars RL')
        libtcod.console_print_ex(0, defn.SCREEN_WIDTH/2, defn.SCREEN_HEIGHT-2, libtcod.BKGND_NONE, libtcod.CENTER,
            'A Roguelike Adventure by ACG')
 
        #show options and wait for the player's choice
        choice = gui.menu('', ['Play a new game', 'Continue last game', 'Quit'], 24)

        if choice == 0:  #new game
            new_game.new_game()
            game.play_game()
        if choice == 1:  #load last game
            gui.msgbox('\n Sorry - I haven\'nt implemented a save/load feature yet.\n\n-ACG\n', 24)
            #try:
             #   load_game()
            #except:
             #   msgbox('\n No saved game to load.\n', 24)
              #  continue
            #game.play_game()
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
