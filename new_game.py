#This file contains the new game initialization functions

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
import spell_classes as spcl
import spell_dictionary as sdic
import monster_dictionary as mdic
import equipment_dictionary as edic
import mage_dictionary as mgdic
import attack_dictionary as adic
import item_dictionary as idic
import input_text

def reset_global_variables():

    #Reset all global variables to starting values
    defn.game_msgs = []
    defn.inventory = []
    defn.objects = []
    defn.dungeon = []
    defn.game = Game()
    defn.dungeon_level = 1
    defn.game_state = 'playing'
    defn.player_location_changed = True
    defn.autoplaying = None
    gui.message ('Press *?* for a list of commands', libtcod.white)

def create_character():

    #Choose a name for your character
    gui.clear_screen()
    name = input_text.input_text(50, 5, 'What is your name?\n\n', '\n\n(press *Enter* when done to continue)')
    gui.clear_screen()

    #Choose your mage class
    index = gui.menu('What sort of mage are you?', mgdic.mages, defn.SCHOOLS_WIDTH)
    mage = mgdic.mage_dict[mgdic.mages[index]]

    #Create player object
    mgdic.create_player(mage, 0, 0)
    defn.player.personal_name = name


# Generate the instances of spells present in the game. For now, we'll just include all spells.

def generate_spell_list():
    spell_list = []
    for spell in sdic.spell_dict.values():
        instance = sdic.get_spell(spell)
        spell_list.append(instance)

    return spell_list

#Define a game class to hold all of the game's information to simplify the coding of saving and loading

class Game:
    def __init__(self):
        self.spell_list = generate_spell_list()

        #Populate item_dict with appropriate books

        for spell in self.spell_list:
            idic.item_dict['book of ' + spell.name] = {
                
                'spawn chance' : [{'level' : 1, 'value' : 50/ spell.properties['level']}],  #will need to think about this part of the function
                'function' : idic.book,
                'parameters' : {
                    'spell' : spell},
                'properties' : {
                    'name' : 'book of ' + spell.name,
                    'graphic' : '#',
                    'color' : libtcod.lightest_green,
                    'description' : 'A detailed treatise on ' + spell.name + '.\n\n' + spell.properties['description']}}

def new_game():

    gui.clear_screen()
    #Show welcome message with backstory information
    gui.msgbox('Welcome to Etheria! You have been cruelly locked in the depths of a dungeon and slated to serve as an amusement in the next round of the Mage Wars. If you can escape the dungeon and defeat your captor in the arena, you will be given your freedom. Perhaps along the way you can learn a thing or two about magic...')
    
    #Player creates character
    create_character()

    #Reset global variables to avoid using data from previous games
    reset_global_variables()

    #Create the starting map and begin the game
    dgen.make_map()
    mpfn.initialize_fov()
    game.render_all()
