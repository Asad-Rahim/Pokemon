import random, pygame, copy
from Items import Ball, Healables, ITEMS
#from Inventory import ItemBagUI
from Pokemon import Pokemon, Attack, STRENGTHS, WEAKNESSES
#from Main import sprites, SCREEN_DETAILS, walk
class PVE_Encounter:
    """
    Pokemon battle between user and the 'AI'
    """
    def __init__(self,player,location):
        self.player = player
        self.player_pokemon = player.main
        self.used = [self.player_pokemon]
        self.location = location
        self.get_enemy()
        self.turn = 0
        self.caught = False
    def get_enemy(self):
        """
        choose a pokemon from the ones available in the location
        """
        l = []
        for pokemon in self.location.pokemon:
            for i in range(pokemon[2]):
                l.append(pokemon)
        pokemon = l[random.randint(0,len(l)-1)]
        self.enemy = Pokemon(pokemon[0], None, random.randint(pokemon[3],pokemon[4]), pokemon[5])
    def _play(self):
        while self.game_on():
            print(self.player_pokemon.hp)
            print(self.enemy.hp)
            #i = input('0 for {}, 1 for {}'.format(self.player.attacks[0].name, self.player.attacks[1].name))
            i = 0
            p = self.player_pokemon.attacks[int(i)]
            en = self.enemy_move()
            if en.speed >p.speed:
                print(self.enemy.attack( self.player_pokemon, en))
                if self.game_on()[0]==0:
                    print(self.player_pokemon.attack( self.enemy, p))
            else:
                print(self.player_pokemon.attack( self.enemy, p))
                if self.game_on()[0]==0:
                    print(self.enemy.attack( self.player_pokemon, en))
    def play(self, attack):
        self.turn +=1
        print("Turn #{}".format(self.turn))
        en = self.enemy_move()
        if isinstance(attack,Healables):
            s = "{} used a {}".format(self.player, attack.name)
            s += self.enemy.attack(self.player_pokemon, en)
            return s
        elif isinstance(attack, Ball):
            s = "{} threw a {}. But {} broke out".format(self.player, attack.name, self.enemy.name)
            s += self.enemy.attack(self.player_pokemon, en)
            return s
        if en.speed > attack.speed:
            print(self.enemy.attack(self.player_pokemon, en))
            if self.game_on()[0]==0:
                print(self.player_pokemon.attack(self.enemy, attack))
        else:
            print(self.player_pokemon.attack(self.enemy, attack))
            if self.game_on()[0]==0:
                print(self.enemy.attack(self.player_pokemon, en))
        print("{} health:{}\t{} health:{}".format(self.player_pokemon.name, self.player_pokemon.hp,
                                                          self.enemy.name, self.enemy.hp))
    def game_on(self):
        '''
        return an int based on what state the game is in:
        0= pokemon is alive
        1= pokemon has fainted
        -1= all pokemon have fainted 
        3= enemy has been caught
        '''
        en = self.enemy.hp==0
        if self.caught:
            en = 3
        return check(self.player,self.player_pokemon), en
    def catch(self):
        ball = input('What ball do you want?\nP-Poke ball\nG-Great ball\nU-Ultra ball\nM-Master Ball')
        for key, item in self.player.bag.items.items():
            if key.name[0] == ball and item >0:
                caught = self.player.bag.consume_item(key, self.enemy)
                if type(caught) == str:
                    return caught
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
        self.used.append(pokemon)
    def xp_gain(self, low=90, high=110):
        xp = self.enemy.level*random.randint(low,high)
        xp_per = xp//len(self.used)
        for pokemon in self.used:
            level = pokemon.level
            evolve = pokemon.add_xp(xp_per)
            print("{} got {} xp for the battle".format(pokemon.level, xp_per))
            if pokemon.level !=level:
                print("{} grew to level {}".format(pokemon.name, pokemon.level))
            if evolve:
                ans = input("Do you want {} to evolve into {}?\n'Y' for yes, 'N' for no")
                if ans == 'Y':
                    new_pokemon = Pokemon(pokemon.evolution[0], pokemon.evolution[1], pokemon.level)
                    pokemon.swap_pokemon(new_pokemon)
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
def check(player, curr):
    i= 0
    if curr.hp==0:
        i =-1
        for pokemon in player.bag.pokemons:
            if pokemon.hp>0:
                i=1
    return i
class PvP_Battle(PVE_Encounter):
    #dificulty is 1,2,3. 1 being no best moves, 2 is sometimes and 3 is always best
    def __init__(self, player, other, difficulty):
        self.player =player
        self.enemy_player = other
        self.player_pokemon , self.enemy= player.main, other.main
        self.turn =0
        self.difficulty=difficulty
    def game_on(self):
        """
        returns a tuple of what the each player has to do for the turn
        0 means they're pokemon are alive so they can do anything
        1 means they're current pokemon fainted and needs to be changed
        -1 means they have been defeated
        """
        return check(self.player, self.player_pokemon), check(self.enemy_player, self.enemy)
    def best_move(self):
        best = [0,None]
        for attack in self.enemy.attacks:
            print(attack)
            if attack.pp>0:
                if self.enemy.hp <= 0.25*self.enemy.maxhp and attack.type== 'Heal':
                    return attack
                temp =copy.copy(self.player_pokemon)
                dmg = temp.hp
                self.enemy.attack(temp, attack)
                dmg -=self.enemy.hp
                if dmg> best[0]:
                    best= [dmg,attack]
                if dmg == best[0] and (best[1] is None or attack.speed >best[1].speed):
                    best = [dmg, attack]
        if best[1] is None:
            print("struggle")
            return Attack('Strugle',15,1,30,1,100,'None',("", 100))
        print(best[1])
        return best[1]
    def enemy_move(self):
        if self.difficulty==1 or (self.difficulty==2 and random.randint(1,8)>3):
            return super().enemy_move()
        return self.best_move()
    def new_enemy(self):
        for pokemon in self.enemy_player.bag.pokemons:
            if pokemon.hp> 0:
                self.enemy
                return pokemon
    def catch(self):
        ball = input('What ball do you want?\nP-Poke ball\nG-Great ball\nU-Ultra ball\nM-Master Ball')
        for key, item in self.player.bag.items.items():
            if key.name[0] == ball and item >0:
                return "You threw a {} but {} swatted it away".format(key.name, self.enemy_player.name)
        return "Invalid ball"
    def cash_gain(self):
        lvl =0
        for pokemon in self.enemy_player.bag.pokemon:
            if lvl< pokemon.level:
                lvl =pokemon.level
        return self.difficulty*lvl*50