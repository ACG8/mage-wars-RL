#####LISTS#####
#This module contains functions for handling lists, such as inventory or spell lists, and the retrieval of items thereof.

#First, we define the list class. This is basically a list with some functions attached, and stackability. The contents of the list are the objects it contains.

class List:
    def __init__(self):
        self.contents = []

    #Adds *quantity* of *item* to the List

    def insert(self, item, quantity):
        if self.contents:
            for element in self.contents:
                if element[0] == item:
                    if quantity == 'infinite':
                        element[1] = 'infinite'
                        return 'pass'
                    if element[1] == 'infinite':
                        return 'pass'
                    element[1] += quantity
                    return 'pass'
        self.contents.append([item, quantity])
        return 'pass'

    #Removes *quantity* of *item* from the List if it has at least that much.

    def remove(self, item, quantity):
        if self.contents:
            for element in self.contents:
                if element [0] == item:
                    if quantity == 'infinite':
                        element[1] = 0
                        return 'pass'
                    if element[1] == 'infinite':
                        return 'pass'
                    if element[1] >= quantity:
                        element[1] -=quantity
                        return 'pass'
        return 'fail'

    #Returns the *quantity* of *item* in the List.

    def get_quantity(self, item):
        if self.contents:
            for element in self.contents:
                if element[0] == item:
                    return element[1]
        return 0

    #Returns the *item* of an element in the List, without the quantity.

    def get_item(self, element):
        return element[0]

    #Returns the *item* at *position* in List, with 0 being the start of the list.

    def get_item_at_position(self, position):
        if 0 <= position <= len(self.contents):
            return self.contents[position][0]
        return 'fail'
