import libtcodpy as libtcod
import gui

def resolve_attack(self, source, target):
    
    roll = roll_attack_dice(self.dice,0)
    print source.name
    print self.dice
    damage = max(roll[0] - target.creature.armor, 0) + roll[1]
    if damage > 0:
        #make the target take some damage
        gui.message (source.name.capitalize() + ' attacks ' + target.name + ' with ' + self.name + '. ' + str(damage) + ' damage!', libtcod.red)
        target.creature.take_damage(damage)
    else:
        gui.message (source.name.capitalize() + ' attacks ' + target.name + ' with ' + self.name + '. No damage!', libtcod.red)

def roll_attack_dice(dice, d12_bonus):
    #mage wars attack formula
    i=0
    norm_dmg=0
    crit_dmg=0
    while i < dice:
        dmg = libtcod.random_get_int(0,0,2)
        crit = dmg*libtcod.random_get_int(0,0,1)
        norm_dmg += dmg - crit
        crit_dmg += crit
        i += 1
    return [norm_dmg, crit_dmg, libtcod.random_get_int(0,1,12) + d12_bonus]

class Attack:
    #any attack made by one creature against another
    def __init__(self, name, dice, traits, effects, dice_bonus=0):
        self.base_dice = dice
        self.name = name
        self.dice_bonus = dice_bonus
        self.traits = traits
        self.effects = effects
        
    @property
    def dice(self):
        return self.base_dice + self.dice_bonus

    def target_creature(self, source, target):
        resolve_attack(self, source, target)
        #additional strikes. note that any bonuses will apply to each strike!
        if ['doublestrike'] in self.traits or ['triplestrike'] in self.traits:
            resolve_attack(self, source, target)
        if ['triplestrike'] in self.traits:
            resolve_attack(self, source, target)

def get_attack(name):
    arg = attk_dict[name]
    attack = Attack(arg['name'], arg['attack dice'], arg['traits'], arg['effects'])
    return attack

attk_dict = {}

#creature attacks

attk_dict['basic melee attack'] = {
    'name' : 'basic melee attack',
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
    'range' : ['ranged', 5]}
