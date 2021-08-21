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
            for i in range(int(pokemon[1])):
                if "-" in pokemon[0]:
                    rnge= pokemon[0].split("-")
                    for i in range (int(rnge[0]), int(rnge[1])):
                        l.append([i]+pokemon[1:] )
                else:
                    l.append([int(pokemon[0])]+ pokemon[1:])
        pokemon = l[random.randint(0,len(l)-1)]
        if pokemon[4] == "None":
            self.enemy = Pokemon(pokemon[0], random.randint(pokemon[2],pokemon[3]))
        else:
            self.enemy = Pokemon(pokemon[0], random.randint(pokemon[2],pokemon[3]), int(pokemon[4]))
    # def _play(self):
    #     while self.game_on():
    #         print(self.player_pokemon.hp)
    #         print(self.enemy.hp)
    #         #i = input('0 for {}, 1 for {}'.format(self.player.attacks[0].name, self.player.attacks[1].name))
    #         i = 0
    #         p = self.player_pokemon.attacks[int(i)]
    #         en = self.enemy_move()
    #         if en.speed >p.speed:
    #             print(self.enemy.attack( self.player_pokemon, en))
    #             if self.game_on()[0]==0:
    #                 print(self.player_pokemon.attack( self.enemy, p))
    #         else:
    #             print(self.player_pokemon.attack( self.enemy, p))
    #             if self.game_on()[0]==0:
    #                 print(self.enemy.attack( self.player_pokemon, en))
    def play(self, attack):
        """
        do a turn of the encounter given the attack the user choose. Return the text
        that should be printed in to the screen and the order
        """
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
        s= [['',None],['', None]]
        if self.enemy.attack_spd(en) > self.player_pokemon.attack_spd(attack):
            s[0][0]=self.enemy.attack(self.player_pokemon, en)
            if self.game_on()[0]==0 and self.game_on()[1]==0:
                s[1][0]=self.player_pokemon.attack(self.enemy, attack)
            elif self.game_on()[1]==1:
                s[1][0]= "{} has fainted".format(self.enemy.name)
            else:
                s[1][0]= "{} has fainted".format(self.player_pokemon.name)
            s[1][1] = 2
            s[0][1] = 1
        else:
            s[0][0]=self.player_pokemon.attack(self.enemy, attack)
            if self.game_on()[0]==0 and self.game_on()[1]==0:
                s[1][0]=self.enemy.attack(self.player_pokemon, en)
            elif self.game_on()[1]==1:
                s[1][0]= "{} has fainted".format(self.enemy.name)
            else:
                s[1][0]= "{} has fainted".format(self.player_pokemon.name)
            s[0][1] = 2
            s[1][1] = 1
        print(s)
        print("{} health:{}\t{} health:{}".format(self.player_pokemon.name, self.player_pokemon.get_hp(),
                                                          self.enemy.name, self.enemy.get_hp()))
        return s
    def game_on(self):
        '''
        return an int based on what state the encounter is still active
        0= pokemon is alive
        1= pokemon has fainted
        -1= all pokemon have fainted 
        3= enemy has been caught
        '''
        en = self.enemy.get_hp()==0
        if self.caught:
            en = 3
        return check(self.player,self.player_pokemon), en
    # def catch(self):
    #     ball = input('What ball do you want?\nP-Poke ball\nG-Great ball\nU-Ultra ball\nM-Master Ball')
    #     for key, item in self.player.bag.items.items():
    #         if key.name[0] == ball and item >0:
    #             caught = self.player.bag.consume_item(key, self.enemy)
    #             if type(caught) == str:
    #                 return caught
    #             for i in range(max(caught,3)):
    #                 self.shake()
    #             if caught == 4:
    #                 self.caught_animation()
    #                 self.player.add_pokemon(self.enemy)
    #                 return "Nice!{} was caught".format(self.enemy.name)
    #             self.break_out()
    #             return "Dammit.{} broke out".format(self.enemy.name)
    #     return 'Invalid ball.'
    def change_pokemon(self, pokemon)->None:
        """
        swap the user's current pokemon to the new pokemon
        """
        self.player_pokemon = pokemon
        self.used.append(pokemon)
    def xp_gain(self):
        """
        give the xp to all the pokemon used in the battle
        """
        a= 1
        if isinstance(self, PvP_Battle):
            a = 1.5
        b= self.enemy.node.basexp
        xp = self.enemy.level*a*b
        xp_per = int(xp//len(self.used))
        all = []
        for pokemon in self.used:
            if pokemon.hp>0:
                level = pokemon.level
                evolve = pokemon.add_xp(xp_per)
                s= "{} got {} xp for the battle".format(pokemon.name, xp_per)
                if pokemon.level !=level:
                    s+="\n{} grew to level {}".format(pokemon.name, pokemon.level)
                all.append([s, evolve, pokemon])
        return all
    def enemy_move(self)-> Attack:
        """
        pick the move the enemy pokemon will use
        """
        doable = []
        for attack in self.enemy.attacks:
            if attack.pp >0:
                doable.append(attack)
        if doable == []:
            return Attack(0,'Strugle',15,1,0.3,1,0,100,'Normal',0,10)
        return doable[random.randint(0,len(doable)-1)]
def check(player, curr):
    """
    check if the player can continue fighting and return whether they can continue, retire or swap
    
    -1: player must retire
    0: player can contiue with the curr pokemon
    1: the player must swap pokemon
    """
    i= 0
    if curr.get_hp()==0:
        i =-1
        for pokemon in player.bag.pokemons:
            if pokemon.get_hp()>0:
                i=1
    return i
class PvP_Battle(PVE_Encounter):
    """
    Battle between two pokemon trainers, one of them being the user and one of them AI
    """
    #dificulty is 1,2,3. 1 being no best moves, 2 is sometimes and 3 is always best
    def __init__(self, player, other, difficulty):
        self.player =player
        self.enemy_player = other
        self.player_pokemon , self.enemy= player.main, other.main
        self.turn =0
        self.used = [self.player_pokemon]
        self.difficulty=difficulty
        self.caught = False
    def game_on(self):
        """
        returns a tuple of what the each player has to do for the turn
        0 means they're pokemon are alive so they can do anything
        1 means they're current pokemon fainted and needs to be changed
        -1 means they have been defeated
        """
        return check(self.player, self.player_pokemon), check(self.enemy_player, self.enemy)
    def best_move(self):
        """
        determine the best move the AI can make based on the current pokemons hp and their attacks
        """
        best = [0,None]
        for attack in self.enemy.attacks:
            if attack.pp>0:
                if self.enemy.get_hp() <= 0.25*self.enemy.get_maxHp() and attack.type== 'Heal':
                    return attack
                temp = copy.copy(self.player_pokemon)
                dmg = temp.get_hp()
                self.enemy.attack(temp, attack)
                dmg -=temp.get_hp()
                if dmg> best[0]:
                    best= [dmg,attack]
                if dmg == best[0] and (best[1] is None or attack.priority >best[1].priority):
                    best = [dmg, attack]
        if best[1] is None:
            return Attack(0,'Strugle',15,1,0.3,1,0,100,'Normal',0,10)
        return best[1]
    def enemy_move(self):
        """
        returns the trainer's descison for the current turn
        """
        if self.difficulty==1 or (self.difficulty==2 and random.randint(1,8)>3):
            return super().enemy_move()
        return self.best_move()
    def new_enemy(self):
        """
        swap the enemy trainer's pokemon to an alive one
        """
        for pokemon in self.enemy_player.bag.pokemons:
            if pokemon.get_hp()> 0:
                self.enemy= pokemon
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