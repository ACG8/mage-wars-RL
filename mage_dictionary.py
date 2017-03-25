mages = [
    'pellian forcemaster']

mage_dict = {}

mage_dict['pellian forcemaster'] = {
    'name' : 'pellian forcemaster',
    'traits' : [],
    'attacks' : ['basic melee attack'],
    'defense' : {
        'minimum roll' : 7,
        'range' : 'any',
        'max uses' : 1,
        'effect' : 'no effect'}, #note: need to alter effect checking so that None is acceptable #note that this defense requires no energy, unlike in the game. Can be changed later.
    'spells' : ['force pull'],
    'training' : ['mind'],
    'antitraining' : ['creatures'],
    'life' : 32,
    'mana' : 30,
    'channeling' : 10}
    
    
    
