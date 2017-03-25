import libtcodpy as libtcod

class Attack:
    #any attack made by one creature against another
    def __init__(self, source, name, dice, traits=None, effect=None):
        self.base_dice = dice
        self.name = name
        self.traits = traits
        self.effect = effect
        
    @property
    def dice(self):
        bonus = 0 #for now, no bonuses sum(equipment.power_bonus for equipment in get_all_equipped(self.owner))
        return self.base_dice #+ bonus

    def target_creature(self, source, target):
        from gui import message

        #mage wars attack formula
        i=0
        norm_dmg=0
        crit_dmg=0
        while i < self.dice:
            dmg = libtcod.random_get_int(0,0,2)
            crit = dmg*libtcod.random_get_int(0,0,1)
            norm_dmg += dmg - crit
            crit_dmg += crit
            i += 1

        damage = crit_dmg + max(norm_dmg - target.creature.armor, 0)
 
        if damage > 0:
            #make the target take some damage
            message (source.owner.name.capitalize() + ' attacks ' + target.name + ', inflicing ' + str(damage) + ' damage.', libtcod.red)
            target.creature.take_damage(damage)
        else:
            message (source.owner.name.capitalize() + ' attacks ' + target.name + ' but fails to inflict any damage!', libtcod.red)

class Spell:
    def __init__(self, name, source, cost, use_function=None):
        self.name = name
        self.source = source
        self.use_function = use_function
        self.cost = cost
    #an spell that that can be learned and used.
    def use(self):
        if self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used.')
        #else:
            ##edit!
            #if self.use_function() != 'cancelled':
                #pass
                #self.source.creature.spend_mana(self.cost) != 'cancelled':
                
                
                #inventory.remove(self.source)  #destroy after use, unless it was cancelled for some reason
