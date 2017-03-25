import gui
import definitions as defn
import libtcodpy as libtcod

########
#This module allows the player to input text into the program.
########

def input_text(width, height, input_prompt, end_prompt):
    #width and height determine the dimensions of the prompt console.
    #input prompt is the message before the entry line
    #end_prompt is the message after the entry line

    text = ''

    while True:
        libtcod.console_flush()
        window = libtcod.console_new(width, height)
        libtcod.console_set_default_foreground(window, libtcod.white)
        libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, input_prompt + text + end_prompt)
        (x, y) = (defn.SCREEN_WIDTH/2 - width/2, defn.SCREEN_HEIGHT/2 - height/2)
        libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)
        libtcod.console_flush()
        key = libtcod.console_wait_for_keypress(True)
        index = key.c - ord('a')
        if 0 <= index <= 25 or -32 <= index <= -7 or index == -65:  #lowercase letters, capital letters, and spaces are allowed
            text += chr(key.c)
        elif len(text) > 0:
            if key.c == 8:
                text = text[:-1]
            if key.c == 13:
                break
        
        gui.clear_screen()

    return text
