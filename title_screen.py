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
 
    #create object representing the player
    creature_component = obcl.Creature(hp=30, mana=30, armor=0, power=3, xp=0, death_function=obcl.player_death)
    defn.player = obcl.Object(0, 0, '@', 'player', libtcod.white, blocks=True, creature=creature_component)
 
    defn.player.level = 1
 
    #generate map (at this point it's not drawn to the screen)
    dgen.make_map()
    mpfn.initialize_fov()
 
    defn.game_state = 'playing'
 
    #a warm welcoming message!
    gui.message('Welcome to Etheria! May you last longer than your predecessor...', libtcod.red)

    #initial spell: a lightning bolt
    from action_classes import Spell
    effect = spfn.cast_lightning()
    spell = Spell('lightning bolt', source=defn.player, cost=1, use_function=effect)
    defn.spellbook.append(spell)

    #initial equipment: a dagger
    #equipment_component = obcl.Equipment(slot='right hand', power_bonus=2)
    #obj = Object(0, 0, '-', 'dagger', libtcod.sky, equipment=equipment_component)
    #inventory.append(obj)
    #equipment_component.equip()
    #obj.always_visible = True
