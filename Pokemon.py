import random
MAX_LEVEL=100
SHINY = 4096
WEAKNESSES ={'Fire':['Water'], 'Electrike':['Ground'], 'Normal': [],'Ground': []}
STRENGTHS ={'Fire':['Grass', 'Flying'], 'Electrike':[], 'Normal':[],'Ground': []}
ATTACKS = {'iron tail': [30, 15, 0.0, 70, 100, 'Normal', ('', 100)],
           'thunder': [65, 5, 0.2, 80, 80, 'Electrike', ('', 100)],
           'flame thrower': [40, 15, 0.0, 70, 95, 'Fire', ('Burned', 50)],
           'rock crush': [55, 5, 0.1, 40, 70, 'Ground', ('', 100)]}
POKEMON = {'pikachu': [120, 'Electrike', ('Raichu', 20), 190, 0, 'iron tail', 'thunder', 'rock crush'],
           'charizard': [170, 'Fire', ('None', 0), 45, 4, 'flame thrower', 'rock crush']}
STATUSES ={'Burned': [-1,-1, 10, False, 100,"was hurt by it's burn."],
           '':[-1,-1,0,False,100,'No status effect'],
           'Confused':[2,5,7,True, 60, "hurt itself in it's confusion."],
           'Fainted':[-1,-1,0,True, 100, "has fainted."]}
class Pokemon:
    """
    Pokemon that can fight, level up and be potentially caught
    """
    def __init__(self, name, num,level,  catch_rate=-1):
        self.name = name
        self.shiny = random.randint(1,SHINY) ==1
        self.level = level
        self.sprite_num = num
        pokemon = POKEMON[name]
        self.hp =pokemon[0]+(level-1)*2
        self.maxhp = self.hp
        self.type =pokemon[1]
        self.evolution = pokemon[2]
        self.attacks = []
        if catch_rate ==-1:
            self.catch_rate = pokemon[3]
        else:
            self.catch_rate = catch_rate
        if num is None:
            self.num = pokemon[4]
        else:
            self.num = num
        self.set_attacks(pokemon[5:])
        self.status = Status('')
        self.xp = 0
        self.next_level = self.level**3
    def __repr__(self):
        return self.name
    def add_xp(self, xp):
        self.xp += xp
        evolution = False
        while self.xp >= self.next_level:
            self.xp -= self.next_level
            evolution = evolution or self.level_up()
        return evolution
        if evolution:
            ans = input("Do you want {} to evolve into {}?\n'Y' for yes, 'N' for no")
            if ans == 'Y':
                pokemon = Pokemon(self.evolution[0], self.evolution[1],self.level)
                self.swap_pokemon(pokemon)
    def evolve_into(self, other):
        self.name,self.maxhp, self.hp= other.name,other.maxhp, self.hp+(other.maxhp-self.maxhp)
        self.status = Status('')
    def set_attacks(self, attacks=None):
        if attacks is None:
            for attack in self.attacks:
                print(attack)
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
            self.status = Status('Fainted')
    def attack(self, victim, attack):
        """
        use attack on victim. Doesn't nessecarly mean damage victim. Also return a descriotion of what happened.
        Descpription will make the game feel more immerserve insread of seeing a health bar
        """
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
                    if attack.status[0] != '' and attack.status[1] >= random.randint(1,100):
                        victim.status = Status(attack.status[0])
                        extra += '.\n{} is now {}'.format(victim.name, victim.status.name)

            else:
                extra = '{} tried using {}, but is {}.'.format(self.name, attack.name, self.status.name)
        else:
            extra = '{} tried using {}, but missed.'.format(self.name, attack.name)
        if status[0] != 0:
            self.set_hp(status[0])
            extra += '\n{} {}'.format(self.name, self.status.description)
        return extra
    def __str__(self):
        return "{},{},{},{},{},{},{},{},{}".format(self.name, self.level, self.hp, self.maxhp,self.attack_str(),
                                                        self.xp, self.status.name, self.shiny, self.sprite_num)
    def attack_str(self):
        s = ''
        for attack in self.attacks:
            s+= str(attack)+','
        return s[:-1]
    def swap_pokemon(self, new):
        return

class Attack:
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
    def __str__(self):
        return "({}/{}/{})".format(self.name, self.damage, self.pp)
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
    def __init__(self, name):
        self.name = name
        s = STATUSES[name]
        self.curr_turn = 0
        self.min_turn = s[0]
        self.max_turn = s[1]
        self.damage = s[2]
        self.stop = s[3]
        self.chance = s[4]
        self.description = s[5]
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


