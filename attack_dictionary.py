#name, dice, traits, effects, target type, range

attk_dict = {}

#creature attacks

attk_dict['basic attack'] = {
    'name' : 'basic attack',
    'attack dice' : 3,
    'traits' : [],
    'effects' : [],
    'target type' : 'creature',
    'range' : ['melee',1]}

attk_dict['sword attack'] = {
    'name' : 'sword attack',
    'attack dice' : 4,
    'traits' : [],
    'effects' : [],
    'target type' : 'creature',
    'range' : ['melee', 1]}

attk_dict['triple bite'] = {
    'name' : 'triple bite',
    'attack dice' : 3,
    'traits' : [['triplestrike']],
    'effects' : [],
    'target type' : 'creature',
    'range' : ['melee', 1]}

#spell attacks

attk_dict['lightning bolt'] = {
    'name' : 'lightning bolt',
    'attack dice' : 5,
    'traits' : [['lightning'],['ethereal']],
    'effects' : [['daze',6],['stun',8]],
    'target type' : 'creature',
    'range' : ['ranged', 1]}
