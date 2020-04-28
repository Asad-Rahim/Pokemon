LOCATION = {'a':[('charizard',100, 1, 0)]}
#Location maps to a list of all pokemon there with their spwan rate and their level
# probality of eveything in the list must equal one

import pygame
pygame.init()
import random


def str_to_status(str):
    s = STATUSES[str]
    return Status(str, s[0], s[1], s[2], s[3], s[4],s[5])
class Bag:
    def __init__(self):
        self.items ={}
        self.pokemons = []
    def add_pokemon(self, pokemon):
      #precondition len(self.pokemons)<6
        if self.main is None:
            self.main = pokemon
        self.pokemons.append(pokemon)
        return '{} has been added from your party.'.format(pokemon.name)
        #return "{} has been sent to the Professor, since you can't hold anymore pokemon."
    def remove_pokemon(self, pokemon):
        #precondtion pokemon is in self.pokemons
        if pokemon == self.main:
            return "{} is your main pokemon, please make another pokemon your main before removing".format(pokemon.name)
        self.pokemons.remove(pokemon)
        return '{} has been removed from your party.'.format(pokemon.name)
    def add_item(self, item):
        if item in self.items:
            self.poke_balls[item] +=1
        else:
            self.poke_balls[item] = 1
    def remove_item(self, item):
        self.poke_balls[item] -=1
    def consume_item(self, item, pokemon):
        if self.items[item] >0:
            self.remove_item(item)
            return item.use(pokemon)
        return "You don't have anymore of this item."

class Player:
    def __init__(self, name):
        self.name = name
        self.bag = Bag()
        self.inventory = []
        self.main = None
        self.x = 50
        self.y = 50
        self.height = 60
        self.width = 40
        self.vel = 5
    def add_pokemon(self, pokemon):
        if len(self.bag.pokemons) == 6:
            self.inventory.append(pokemon)
        else:
            self.bag.add_pokemon(pokemon)
            if self.main is None:
                self.change_main(pokemon)
    def change_main(self, pokemon):
        #pokemon must be in bag
        self.main = pokemon

class PVE_Encounter:
    def __init__(self,player,location):
        self.player = player
        self.player_pokemon = player.main
        self.get_enemy(location)
    def get_enemy(self, location):
        l = []
        for pokemon in LOCATION[location]:
            for i in range(pokemon[1]):
                l.append(pokemon)
        pokemon = l[random.randint(0,len(l)-1)]
        self.enemy = Pokemon(pokemon[0], pokemon[2], pokemon[3])
    def play(self):
        while self.game_on():
            print(self.player_pokemon.hp)
            print(self.enemy.hp)
            #i = input('0 for {}, 1 for {}'.format(self.player.attacks[0].name, self.player.attacks[1].name))
            i = 0
            p = self.player_pokemon.attacks[int(i)]
            en = self.enemy_move()
            if en.speed >p.speed:
                print(self.enemy.attack( self.player_pokemon, en))
                if self.game_on():
                    print(self.player_pokemon.attack( self.enemy, p))
            else:
                print(self.player_pokemon.attack( self.enemy, p))
                if self.game_on():
                    print(self.enemy.attack( self.player_pokemon, en))

    def game_on(self):
        return self.player_pokemon.hp >0 and self.enemy.hp >0
    def catch(self):
        ball = input('What ball do you want?\nP-Poke ball\nG-Great ball\nU-Ultra ball\nM-Master Ball')
        for key in self.player.bag.items.keys():
            if key.name[0] == ball:
                caught = self.player.bag.consume_item(key, self.enemy)
                for i in range(max(caught,3)):
                    self.shake()
                if caught == 4:
                    self.caught_animation()
                    self.player.add_pokemon(self.enemy)
                    return "Nice!{} was caught".format(self.enemy.name)
                self.break_out()
                return "Dammit.{} broke out".format(self.enemy.name)
        return 'Invalid ball.'
    def change_pokemon(self, pokemon):
        self.player_pokemon = pokemon
    def caught_animation(self):
        pass
    def shake(self):
        pass
    def break_out(self, ):
        pass
    def enemy_move(self):
        doable = []
        for attack in self.enemy.attacks:
            if attack.pp >0:
                doable.append(attack)
        if doable == []:
            return Attack('Strugle',15,1,30,1,100,'None',self.enemy)
        return doable[random.randint(0,len(doable)-1)]


POKEMON= {'pikachu':[120,'Electrike', ('Raichu', 20),190,'iron tail','thunder'],
          'charizard':[170,'Fire', ('None', 0), 45,'flame thrower', 'rock crush']}
ATTACKS={'iron tail': [30,15,0.0,70,100, 'Normal',('',100)], 'thunder':[65, 5, 0.2,80,80, 'Electrike',('',100)],
         'flame thrower':[40,15, 0.0, 70,95,'Fire',('Burned', 50)], 'rock crush':[55,5,0.1, 40,70, 'Ground',('',100)]}
WEAKNESSES ={'Fire':['Water'], 'Electrike':['Ground'], 'Normal': [],'Ground': []}
STRENGTHS ={'Fire':['Grass', 'Flying'], 'Electrike':[], 'Normal':[],'Ground': []}
MAX_LEVEL =999
class Pokemon:
    def __init__(self, name, level, catch_rate=None):
        self.name = name
        self.level = level
        pokemon = POKEMON[name]
        self.hp =pokemon[0]+(level-1)*2
        self.maxhp = self.hp
        self.type =pokemon[1]
        self.evolution = pokemon[2]
        self.attacks = []
        if catch_rate is None:
            self.catch_rate = pokemon[3]
        else:
            self.catch_rate = catch_rate
        self.set_attacks(pokemon[4:])
        self.status = str_to_status('')
        self.curr_xp = 0
        self.next_level = self.level**3
    def add_xp(self, xp):
        self.xp += xp
        evolution = False
        while self.xp >= self.next_level:
            self.xp -= self.next_level
            evolution = evolution or self.level_up()
        if evolution:
            ans = input("Do you want {} to evolve into {}?\n'Y' for yes, 'N' for no")
            if ans == 'Y':
                pokemon = Pokemon(self.evolution[0], self.evolution[1])
                self.swap_pokemon(pokemon)
    def evolve_into(self, other):
        self.name,self.maxhp, self.hp= other.name,other.maxhp, self.hp+(other.maxhp-self.maxhp)
        self.status = str_to_status('')
    def set_attacks(self, attacks=None):
        if attacks is None:
            for attack in self.attacks:
                attack.damage += 2
            return
        for attack in attacks:
            a = ATTACKS[attack]
            self.attacks.append(Attack(attack, a[0]+(self.level-1)*4//3, a[1], a[2], a[3], a[4],a[5],a[6]))
    def level_up(self):
        if self.level == MAX_LEVEL:
            return False
        self.level +=1
        self.set_attacks()
        self.next_level = self.level**3
        if self.level == self.evolution[1]:
            return True
        return False
    def set_hp(self, amount):
        if self.hp- amount >self.maxhp:
            self.hp = self.maxhp
        elif self.hp - amount <0:
            self.hp = 0
        else:
            self.hp = self.hp - amount
        if self.hp == 0:
            self.status = str_to_status('Fainted')
    def attack(self, victim, attack):
        status = self.status.status_effect()
        s = ''
        if attack.accuracy >= random.randint(1,100):
            attack.pp -= 1
            extra = '{} used {}'.format(self.name, attack.name)
            if status[1]:
                if attack.type == 'Heal':
                    self.status.name = ''
                    self.set_hp(attack.damage)
                    return (extra +' and recovered some hp.',attack.damage),
                else:
                    if attack.type in WEAKNESSES[attack.type]:
                        damage = attack.damage * 3 // 2
                        s='.\nIt was super effective!'
                    elif attack.type in STRENGTHS[attack.type]:
                        damage = attack.damage * 2 // 3
                        s='.\nIt was not very effective...'
                    else:
                        damage = attack.damage
                    victim.set_hp(damage)
                    sd = int(damage*attack.self_damage)
                    if sd != 0:
                        s = '.\n{} was hit with recoil during the attack'.format(self.name) +s
                        self.set_hp(sd)
                    extra += s
                    if victim.status.name == '' and attack.status[1] >= random.randint(1,100):
                        victim.status = str_to_status(attack.status[0])
                        extra += '.\n{} is now {}'.format(victim.name, )

            else:
                extra = '{} tried using {}, but is {}.'.format(self.name, attack.name, self.status.name)
        else:
            extra = '{} tried using {}, but missed.'.format(self.name, attack.name)
        if status[0] != 0:
            self.set_hp(status[0])
            extra += '\n{} {}'.format(self.name, self.status.description)
        return extra



STATUSES ={'Burned': [-1,-1, 10, False, 100,"was hurt by it's burn."],
           '':[-1,-1,0,False,100,'No status effect'],
           'Confused':[2,5,7,True, 60, "hurt itself in it's confusion."],
           'Fainted':[-1,-1,0,True, 100, "has fainted."]}
class Attack():
    '''
    name: name of attack
    damage: damage of attack to victim
    pp: how many time attack can be used
    self_damage: perctange of damage that gets inflicted onto user
    speed: speed of attack
    accuracy: chance attack hits
    status: tuple of what status is possible from being hit from this attack
    and what is the likelyhood of the status working
    '''
    def __init__(self,name, damage, pp, self_damage, speed,accuracy,type, status):
        self.name = name
        self.damage = damage
        self.pp =self.max_pp= pp
        self.speed = speed
        self.type = type
        self.accuracy = accuracy
        self.self_damage = self_damage
        self.status = status[0], status[1]
    #def __repr__(self):
    #    return '{} attack does {} damage with self staus:{} and enemy staus{}.{} pp left'.format(
    #        self.name, self.damage,self.self_status,self.enemy_status,self.pp)
class Status:
    '''
    The status of a pokemon
    name: what is there status, if '' then they have no status effect
    min_turn: the minnium turns the status will last
    max_turns: max turns status will last
    damage: amount of hp deducted from the pokemons hp
    stop: whether this status prevents them from attacking
    chance: what is trhe chance to break out of the status once, after the minnium turn
    description: what will be said once the status takes effect
    '''
    def __init__(self, name,min_turn, max_turn, damage, stop, chance, description):
        self.name = name
        self.max_turn = max_turn
        self.damage = damage
        self.curr_turn = 0
        self.min_turn = min_turn
        self.stop = stop
        self.chance = chance
        self.description = description
    def status_effect(self):
        if self.name == '' or self.curr_turn == self.max_turn:
            self.name = ''
            return 0, True
        elif self.curr_turn > self.min_turn:
            if random.randint(1,100) > self.chance:
                self.name = ''
                return 0, True
        self.curr_turn +=1
        return self.damage, not self.stop


class Item:
    def use(self, pokemon):
        raise NotImplementedError
class Healables(Item):
    # amount is amount of pp that will be restored for user,
    # restore == True then make their health full
    # all_cure == True then restore their status
    # is curee == None then doesn't cure anything
    def __init__(self, name, status_cure, amount,description, restore = False, all_cure = False):
        self.name = name
        self.cure = status_cure
        self.amount = amount
        self.description = description
        self.restore = restore
        self.all_cure = all_cure
    def use(self, pokemon):
        if (pokemon.status.name !='')and (self.all_cure or pokemon.status == self.cure):
            pokemon.status = str_to_status('')
        if self.restore:
            pokemon.hp = pokemon.maxhp
        else:
            pokemon.set_hp(-1*self.amount)



class Ball(Item):
    def __init__(self, name, catch_rate):
        self.catch_rate = catch_rate
        self.name = name
    def use(self, pokemon):
        a = max((3*pokemon.maxhp- 2*pokemon.hp)*self.catch_rate*pokemon.catch_rate/(3*pokemon.maxhp), 1)
        num = random.randint(1,255)
        if num <= a:
            return 4
        b = 65536 / (255/a)^0.1875
        count = 0
        while count !=4 and random.randint(1, 255)< b:
            count +=1
        return count

class MasterBall(Ball):
    def catch(self, pokemon):
         return 4


BALLS ={'P': Ball('Poke ball', 1), 'U':Ball('Ultra ball', 1.25), 'G':Ball('Great ball', 1.125),
 'M':MasterBall('Master ball', 1)}







if __name__ == '__main__':
    Asad = Player('Asad')
    run = True
    window = pygame.display.set_mode((550, 600))
    pygame.display.set_caption('Pokemon')
    while run:
        print('b')
        pygame.time.delay(100)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False


        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            print('a')
            Asad.x = max(Asad.x-Asad.vel, 0)
        if keys[pygame.K_d]:
            Asad.x = min(550, Asad.x+ Asad.vel)
        if keys[pygame.K_w]:

            Asad.y = max(0, Asad.y-Asad.vel)
        if keys[pygame.K_s]:
            Asad.y = min(600,Asad.y +Asad.vel)

        window.fill((0, 0, 0))
        pygame.draw.rect(window, (255, 0, 0), (Asad.x, Asad.y, Asad.width, Asad.height))
        pygame.display.update()
    pygame.quit()
    p = Pokemon('pikachu', 5)
    e = PVE_Encounter(p, 'a')
    e.play()
    print(e.player.hp)
    print(e.enemy.hp)