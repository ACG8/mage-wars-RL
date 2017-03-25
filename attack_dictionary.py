import libtcodpy as libtcod
import gui
import data_methods as data
import random
import definitions as defn

class Attack:
    #any attack made by one creature against another
    def __init__(self, name, dice, attack_range, traits, effects, speed):
        self.dice = dice
        self.range = attack_range
        self.name = name
        self.traits = traits
        self.effects = effects
        self.is_counterstrike = False
        self.speed = speed

    def declare_attack(self, source, target, dice_bonus, d12_bonus):
        #to avoid the corpse-counterattack problem, check if target is attackable.
        if target.creature:
            if source.creature and 'daze' in source.creature.conditions and libtcod.random_get_int(0,1,12) < 7:
                gui.message (source.title.capitalize() + ' is too dazed to attack!', libtcod.orange)
                source.creature.adjust_turn_counter(3)
            else:
                self.resolve_attack_roll(self.dice + dice_bonus, d12_bonus, source, target)
                #additional strikes do not gain any bonuses.
                if source.creature and (['doublestrike'] in self.traits or ['triplestrike']) in self.traits:
                    self.resolve_attack_roll(self.dice, d12_bonus, source, target)
                if source.creature and ['triplestrike'] in self.traits:
                    self.resolve_attack_roll(self.dice, d12_bonus, source, target)
            #remove daze (and potentially other conditions) at conclusion of attacks
            if source.creature:
                daze_removal = False
                for condition in source.creature.conditions:
                    if condition == 'daze':
                        source.creature.conditions.remove(condition)
                        daze_removal = True
                if daze_removal:
                    gui.message (source.title.capitalize() + ' is dazed no longer!', libtcod.orange)

    def resolve_attack_roll(self, dice, d12_bonus, source, target):

        #manage defenses
        avoided = False
        def_effect = None
        #still need to implement unavoidable attacks
        
        if target.creature.defenses:
            defense_choices = []
            for defense in target.creature.defenses:
                if defense and defense.uses > 0 and (defense.range == self.range['type'] or defense.range == 'any'):
                    defense_choices.append(defense)
            if defense_choices:
                defense = random.choice(defense_choices)
                #for now, no bonuses. Adding defense bonuses later should be easy.
                def_bonus = data.sum_values_from_list(source.traits, 'defense +')
                #daze reduction in defense roll
                for condition in target.creature.conditions:
                    if condition == 'daze':
                        def_bonus -= 2
                if defense.use(def_bonus):
                    gui.message (target.title.capitalize() + ' avoids ' + source.title + '\'s attack!', libtcod.red)
                    avoided = True
                    if defense.effect:
                        def_effect = defense.effect

        #mage wars attack formula
        if not avoided:
            normal_damage=0
            critical_damage=0

            dice_to_roll = dice
            
            #subtract dice if weak. Later can also add aegis here.
            if source.creature:
                for condition in source.creature.conditions:
                    if condition == 'weak' and 'magical' not in self.traits:
                        dice_to_roll -= 1
            
            if not ['no damage'] in self.traits:
                for i in range(max(dice_to_roll,1)):
                    roll = libtcod.random_get_int(0,0,2)
                    crit = roll * libtcod.random_get_int(0,0,1)
                    if ['incorporeal'] in target.traits and not ['ethereal'] in self.traits:
                        #unlike the game, this formula is the simplest way to implement this:
                        normal_damage += max(roll - crit -1, 0)
                        critical_damage += max(crit - 1,0)
                    else:
                        normal_damage += roll - crit
                        critical_damage += crit

            armor = max(target.creature.armor - data.sum_values_from_list(self.traits, 'piercing +'), 0)

            #sturdy (vet's belt effect)
            for trait in target.traits:
                if trait[0] == 'sturdy +':
                    if critical_damage >= trait[1]:
                        normal_damage += trait[1]
                        critical_damage -= trait[1]
                    else:
                        normal_damage += critical_damage
                        critical_damage = 0
            
            if ['resilient'] in target.traits:
                damage = critical_damage
            else:
                damage = max(normal_damage - armor, 0) + critical_damage

            if damage > 0:
                if not self.is_counterstrike:
                    gui.message (source.title.capitalize() + ' attacks ' + target.title + ' with ' + self.name + '! ' + str(damage) + ' damage!', libtcod.red)
                else:
                    gui.message (source.title.capitalize() + ' retaliates with ' + self.name + '! ' + str(damage) + ' damage!', libtcod.orange)
                target.creature.take_damage(damage)
            else:
                if not self.is_counterstrike:
                    gui.message (source.title.capitalize() + ' attacks ' + target.title + ' with ' + self.name + '. No damage!', libtcod.red)
                else:
                    gui.message (source.title.capitalize() + ' retaliates but fails to inflict any damage.', libtcod.orange)

            roll = libtcod.random_get_int(0,1,12)

            #rolling for effects
            effects = None
            if self.effects:
                for effect in self.effects:
                    if roll >= effect[1]:
                        effects = effect[0]

            #implement effects
            if effects and target.creature:
                #for now, don't worry about poison immunity.
                for effect in effects:
                    #poison immunity
                    if effect in ['rot', 'weak', 'cripple', 'tainted'] and ['poison immunity'] in target.traits:
                        gui.message (target.title + ' resists the poison!', libtcod.purple)
                        break
                    #long term should probably define a class of conditions or something so I don't have to maintain a list of what constitutes a condition.
                    if effect in ['rot','weak','burn','cripple']:
                        gui.message (source.title.capitalize() + ' inflicts ' + effect + ' on ' + target.title + '!', libtcod.purple)
                        target.creature.conditions.append(effect)
                    if effect == 'tainted':
                        gui.message (source.title.capitalize() + 's\' attack taints ' + target.title + '!', libtcod.purple)
                        target.creature.conditions.append('tainted')
                        target.creature.take_damage(3)
                    if effect == 'daze':
                        gui.message (target.title + ' is dazed!', libtcod.purple)
                        target.creature.conditions.append('daze')
                    if effect == 'stun':
                        gui.message (target.title + ' is stunned!', libtcod.purple)
                        target.creature.conditions.append('stun')

            #resolve counterstrikes. currently just takes the first counterstriking attack it finds.
            #note that counterstrikes currently use up time
            #something odd going on here; sometimes target.creature has no attack attribute.
            #problem occurs when creature is transformed into remains.
            #check if target still exists as a creature, e.g. has not been killed or so forth with 'if target.creature'
                #long run find a better way to fix this problem
                
        if target.creature:
            if target.creature.attacks and self.range['type'] == 'melee' and not self.is_counterstrike:
                for attack in target.creature.attacks:
                    #currently returns the first counterattack it finds. special case for shield bash, rather than giving defenses effects
                    if (['counterstrike'] in attack.traits) or (attack.name == 'shield bash' and def_effect == 'shield bash'):
                        attack.is_counterstrike = True
                        target.creature.attack(source,attack)
                        attack.is_counterstrike = False
                        break

def get_defense(dictionary):
    if dictionary:
        defense = Defense(
            dictionary['minimum roll'],
            dictionary['max uses'],
            dictionary['range'],
            dictionary['effect'])
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
def get_attack(dictionary):
    if dictionary:
        attack = Attack(
            name = dictionary['name'],
            attack_range = dictionary['range'],
            dice = dictionary['attack dice'],
            traits = dictionary['traits'],
            effects = dictionary['effects'],
            speed = dictionary['speed'])
        return attack
    return None
