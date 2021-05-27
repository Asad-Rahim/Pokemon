import random
from Pokemon import Status

class Item:
    def use(self, pokemon):
        raise NotImplementedError
class Healables(Item):
    # amount is amount of pp that will be restored for user,
    # restore == True then make their health full
    # all_cure == True then restore their status
    # if cure == None then doesn't cure anything
    def __init__(self, name, status_cure, amount,description, restore = False, all_cure = False):
        self.name = name
        self.cure = status_cure
        self.amount = amount
        self.description = description
        self.restore = restore
        self.all_cure = all_cure
    def use(self, pokemon):
        if (pokemon.status.name !='')and (self.all_cure or pokemon.status == self.cure):
            pokemon.status = Status('')
        if self.restore:
            pokemon.hp = pokemon.maxhp
        else:
            pokemon.set_hp(-1*self.amount)



class Ball(Item):
    def __init__(self, name, catch_rate, description):
        self.catch_rate = catch_rate
        self.name = name
        self.description = description
    def use(self, pokemon):
        """
        Use pokeball on pokemon to see if it is caught. Algorithim is copied from pokemon gen 3
        """
        if pokemon.catch_rate == 0:
            return 0
        a = max((3*pokemon.maxhp- 2*pokemon.hp)*self.catch_rate*pokemon.catch_rate/(3*pokemon.maxhp), 1)
        num = random.randint(1,255)
        if num <= a:
            return 4
        b = 65536 / (255/a)**0.1875
        count = 0
        while count !=4 and random.randint(1, 255)< b:
            count +=1
        return count

class MasterBall(Ball):
    def use(self, pokemon):
         return 4
ITEMS = {'Poke ball': Ball('Poke ball', 1, 'Used to catch wild pokemon.'),
         'Ultra ball': Ball('Ultra ball', 1.25, 'Used to catch wild pokemon.'),
         'Great ball': Ball('Great ball', 1.125, 'Used to catch wild pokemon.'),
         'Master ball': MasterBall('Master ball', 1, 'Can immediatly catch any wild pokemon.'),
         'Full Restore': Healables('Full Restore', None, 0, 'Cure all status effects and fully heal pokemon.', True,
                                   True)}