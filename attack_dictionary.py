import libtcodpy as libtcod
import gui
import data_methods as data
import random

class Attack:
    #any attack made by one creature against another
    def __init__(self, name, dice, attack_range, traits, effects, dice_bonus=0, d12_bonus=0):
        self.base_dice = dice
        self.range = attack_range
        self.name = name
        self.dice_bonus = dice_bonus
        self.traits = traits
        self.effects = effects
        self.d12_bonus = d12_bonus
        self.is_counterstrike = False
        
    @property
    def dice(self):
        return self.base_dice + self.dice_bonus

    def declare_attack(self, source, target):
        #to avoid the corpse-counterattack problem, check if target is a monster.
        if target.creature:
            self.resolve_attack_roll(self.dice, self.d12_bonus, source, target)
            #additional strikes do not gain any bonuses.
            if source.creature and (['doublestrike'] in self.traits or ['triplestrike']) in self.traits:
                self.resolve_attack_roll(self.base_dice, self.d12_bonus, source, target)
            if source.creature and ['triplestrike'] in self.traits:
                self.resolve_attack_roll(self.base_dice, self.d12_bonus, source, target)

    def resolve_attack_roll(self, dice, d12_bonus, source, target):

        #manage defenses
        avoided = False
        def_effect = None
        #still need to implement unavoidable attacks
        
        if target.creature.defenses:
            defense_choices = []
            for defense in target.creature.defenses:
                if defense and defense.uses > 0 and (defense.range == self.range[0] or defense.range == 'any'):
                    defense_choices.append(defense)
            if defense_choices:
                defense = random.choice(defense_choices)
                #for now, no bonuses. Adding defense bonuses later should be easy.
                def_bonus = data.sum_values_from_list(source.traits, 'defense +')
                if defense.use(def_bonus):
                    gui.message (target.name.capitalize() + ' avoids ' + source.name + '\'s attack!', libtcod.red)
                    avoided = True
                    if defense.effect:
                        def_effect = defense.effect

        #mage wars attack formula
        if not avoided:
            normal_damage=0
            critical_damage=0
            
            if not ['no damage'] in self.traits:
                for i in range(max(dice,1)):
                    roll = libtcod.random_get_int(0,0,2)
                    crit = roll * libtcod.random_get_int(0,0,1)
                    normal_damage += roll - crit
                    critical_damage += crit
                        
            armor = max(target.creature.armor - data.sum_values_from_list(self.traits, 'piercing +'), 0)
            damage = max(normal_damage - armor, 0) + critical_damage

            roll = libtcod.random_get_int(0,1,12)

            #rolling for effects
            effects = None
            if self.effects:
                for effect in self.effects:
                    if roll >= effect[1]:
                        effects = effect[0]

            #need to implement attack effects

            if damage > 0:
                if not self.is_counterstrike:
                    gui.message (source.name.capitalize() + ' attacks ' + target.name + ' with ' + self.name + '! ' + str(damage) + ' damage!', libtcod.red)
                else:
                    gui.message (source.name.capitalize() + ' retaliates with ' + self.name + '! ' + str(damage) + ' damage!', libtcod.orange)
                target.creature.take_damage(damage)
            else:
                if not self.is_counterstrike:
                    gui.message (source.name.capitalize() + ' attacks ' + target.name + ' with ' + self.name + '. No damage!', libtcod.red)
                else:
                    gui.message (source.name.capitalize() + ' retaliates but fails to inflict any damage.', libtcod.orange)

            #resolve counterstrikes. currently just takes the first counterstriking attack it finds.
            #note that counterstrikes currently use up time
            #something odd going on here; sometimes target.creature has no attack attribute.
            #problem occurs when creature is transformed into remains.
            #check if target still exists as a creature, e.g. has not been killed or so forth with 'if target.creature'
                #long run find a better way to fix this problem
                

        if target.creature:
            if target.creature.attacks and self.range[0] == 'melee' and not self.is_counterstrike:
                for attack in target.creature.attacks:
                    #currently returns the first counterattack it finds. special case for shield bash, rather than giving defenses effects
                    if (['counterstrike'] in attk_dict[attack]['traits']) or (attk_dict[attack]['name'] == 'shield bash' and def_effect == 'shield bash'):
                        target.creature.attack(source,attack,is_counterstrike=True)
                        break

def get_defense(parameters):
    if parameters:
        defense = Defense(parameters['minimum roll'], parameters['max uses'], parameters['range'], parameters['effect'])
        return defense
    return None
    

#define defenses here (no point making a separate document yet)
class Defense:
    def __init__(self, minimum_roll, max_uses, defense_range, effect):
        self.minimum_roll = minimum_roll
        self.max_uses = max_uses
        self.uses = max_uses
        self.range = defense_range
        self.effect = effect

    def use(self, bonus):
        if self.uses > 0:
            roll = bonus + libtcod.random_get_int(0,1,12)
            self.uses -= 1
            if roll >= self.minimum_roll:
                return True
            
    def reset(self):
        self.uses = self.max_uses

#retrieve an attack from the dictionary
def get_attack(name):
    arg = attk_dict[name]
    attack = Attack(name = arg['name'], attack_range = arg['range'], dice = arg['attack dice'], traits = arg['traits'], effects = arg['effects'])
    return attack

attk_dict = {}

#note: effects should be listed in ascending order
#creature attacks

attk_dict['basic melee attack'] = {
    'name' : 'basic melee attack',
    'attack dice' : 3,
    'traits' : [],
    'effects' : [],
    'target type' : 'creature',
    'range' : ['melee',1],
    'speed' : ['quick', 2]}

attk_dict['razor edged slash'] = {
    'name' : 'razor edged slash',
    'attack dice' : 4,
    'traits' : [['piercing +', 2]],
    'effects' : [],
    'target type' : 'creature',
    'range' : ['melee', 1],
    'speed' : ['quick', 2]}

attk_dict['shield bash'] = {
    'name' : 'shield bash',
    'attack dice' : 3,
    'traits' : [['piercing +', 1]],
    'effects' : [],
    'target type' : 'creature',
    'range' : ['melee', 1],
    'speed' : ['quick', 2]}

attk_dict['triple bite'] = {
    'name' : 'triple bite',
    'attack dice' : 3,
    'traits' : [['triplestrike']],
    'effects' : [],
    'target type' : 'creature',
    'range' : ['melee', 1],
    'speed' : ['full', 4]}

attk_dict['snapping bite'] = {
    'name' : 'snapping bite',
    'attack dice' : 4,
    'traits' : [['counterstrike']],
    'effects' : [],
    'target type' : 'creature',
    'range' : ['melee', 1],
    'speed' : ['quick', 2]}

#spell attacks

attk_dict['lightning bolt'] = {
    'name' : 'lightning bolt',
    'attack dice' : 5,
    'traits' : [['lightning'],['ethereal']],
    'effects' : [[['daze'],6],[['stun'],8]],
    'target type' : 'creature',
    'range' : ['ranged', 5],
    'speed' : ['quick', 1]}
