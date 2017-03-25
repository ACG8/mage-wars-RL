import math

#for lists of lists, this function sums the values of desired elements.
def sum_values_from_list(target_list, desired_element):
    value = 0
    if target_list:
        for thing in target_list:
            if thing[0] == desired_element:
                value += thing[1]
    return value

def distance (x1,y1,x2,y2):
    return math.sqrt((x1-x2) ** 2 + (y1-y2) ** 2)
