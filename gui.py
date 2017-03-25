import libtcodpy as libtcod
import textwrap
import definitions as defn
import title_screen as tit

def msgbox(text, width=50):
    #use menu() as a sort of "message box"
    menu(text, [], width)

def clear_screen():
    for y in range(defn.SCREEN_HEIGHT):
        for x in range(defn.SCREEN_WIDTH):
            libtcod.console_set_char_background(defn.screen, x, y, libtcod.black, libtcod.BKGND_SET)
    libtcod.console_blit(defn.screen, 0, 0, defn.SCREEN_WIDTH, defn.SCREEN_HEIGHT, 0, 0, 0)

def message(new_msg, color = libtcod.white):
    #split the message if necessary, among multiple lines
    new_msg_lines = textwrap.wrap(new_msg, defn.MSG_WIDTH)
 
    for line in new_msg_lines:
        #if the buffer is full, remove the first line to make room for the new one
        if len(defn.game_msgs) == defn.MSG_HEIGHT:
            del defn.game_msgs[0]
 
        #add the new line as a tuple, with the text and the color
        defn.game_msgs.append((line, color))

def menu(header, options, width):
    #eliminate any other menus or messages
    libtcod.console_flush()
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')
    #calculate total height for the header (after auto-wrap) and one line per option
    header_height = libtcod.console_get_height_rect(defn.con, 0, 0, width, defn.SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
    height = len(options) + header_height
    
    #create an off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)
 
    #print the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    #print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

   #blit the contents of "window" to the root console
    x = defn.SCREEN_WIDTH/2 - width/2
    y = defn.SCREEN_HEIGHT/2 - height/2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    #present the root console to the player and wait for a key-press
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

    #convert the ASCII code to an index; if it corresponds to an option, return it
    index = key.c - ord('a')
    #convert the ASCII code to an index; if it corresponds to an option, return it
    #index = key.c - ord('a')
    if index >= 0 and index < len(options): return index
    return None

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    #render a bar (HP, experience, etc). first calculate the width of the bar
    bar_width = int(float(value) / maximum * total_width)
 
    #render the background first
    libtcod.console_set_default_background(defn.stats_panel, back_color)
    libtcod.console_rect(defn.stats_panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)
 
    #now render the bar on top
    libtcod.console_set_default_background(defn.stats_panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(defn.stats_panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    #finally, some centered text with the values
    libtcod.console_set_default_foreground(defn.stats_panel, libtcod.white)
    libtcod.console_print_ex(defn.stats_panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
        name + ': ' + str(value) + '/' + str(maximum))

def get_names_under_mouse():
 
    #return a string with the names of all objects under the mouse
    (x, y) = (defn.mouse.cx, defn.mouse.cy)
    
    #create a list with the names of all objects at the mouse's coordinates and in FOV
    names = [obj.name for obj in defn.objects
        if obj.x == x and obj.y == y and libtcod.map_is_in_fov(defn.fov_map, obj.x, obj.y)]

    names = ', '.join(names)  #join the names, separated by commas
    
    return names.capitalize()
