import random, math, copy, csv
MAX_LEVEL=100
SHINY = 4096
USELESS = {'Fire':[], 'Water':[],'Electric':["Ground"],'Grass':[],
    'Ice':[],'Fighting':['Ghost'],'Poison':['Steel'],'Ground': ['Flying'],
    'Flying':[],'Psychic':['Dark'],'Bug':[],'Rock':[], 'Ghost':['Normal'],
    'Dragon':['Fairy'],'Dark':[],'Steel':[],'Fairy':[],
    'Normal':['Ghost'], 'None':[]}
WEAKNESSES ={'Fire':['Fire', 'Water', 'Rock', 'Dragon'], 
            'Water':['Water', 'Grass', 'Dragon'],
            'Electric':['Electric', 'Grass', 'Dragon'],
            'Grass':['Fire', 'Grass', 'Poison', 'Flying', 'Bug', 'Dragon', 'Steel'],
            'Ice':['Fire', 'Water', 'Ice', 'Steel'],
            'Fighting':['Poison', 'Flying','Psychic', 'Bug', 'Fairy'],
            'Poison':['Poison', 'Ground', 'Rock', 'Ghost'],
            'Ground': ['Ice', 'Bug'],
            'Flying':['Electric','Rock', 'Steel'],
            'Psychic':['Psychic', 'Steel'],
            'Bug':['Fire', 'Fighting', 'Poison','Flying', 'Ghost', 'Steel', 'Fairy'],
            'Rock':['Fighting', 'Ground', 'Steel'], 
            'Ghost':['Dark'],
            'Dragon':['Steel'],
            'Dark':['Fighting', 'Dark', 'Fairy'],
            'Steel':['Fire', 'Water', 'Electric', 'Steel'],
            'Fairy':['Fire', 'Poison', 'Steel'],
            'Normal':['Rock', 'Steel'], 'None':[]}
STRENGTHS ={'Fire':['Grass', 'Ice', 'Bug', 'Steel'], 
            'Water':['Fire', 'Ground', 'Rock'],
            'Electric':['Water', 'Flying'],
            'Grass':['Water', 'Ground', 'Rock'],
            'Ice':['Grass', 'Ground', 'Flying'],
            'Fighting':['Normal', 'Ice', 'Rock', 'Dark', 'Steel'],
            'Poison':['Grass', 'Fairy'],
            'Ground': ['Fire', 'Electric', 'Poison', "Rock", "Steel"],
            'Flying':['Grass', 'Poison', 'Bug'],
            'Psychic':['Fighting', 'Poison'],
            'Bug':['Grass', 'Psychic', 'Dark'],
            'Rock':['Fire', 'Ice', 'Flying', 'Bug'], 
            'Ghost':['Ghost', 'Psychic'],
            'Dragon':['Dragon'],
            'Dark':['Psychic', 'Ghost'],
            'Steel':['Ice', 'Rock', 'Fairy'],
            'Fairy':['Fighting', 'Dragon', 'Dark'],
            'Normal':[], 'None':[]}
ATTACKS = {'iron tail': [100, 15, 0.0, 1, 75, 'Normal', ('', 100),0],
           'thunder': [110, 10, 0.2, 1, 70, 'Electric', ('', 100),1],
           'Flamethrower': [90, 15, 0.0, 1, 100, 'Fire', ('Burned', 50),1],
           'rock crush': [70, 5, 0.1, 0, 100, 'Ground', ('', 100),0],
           'Scratch': [40, 35, 0, 1, 100, 'Normal', ('', 100),0],
           'Dragon Breath': [60, 20, 0, 1, 100, 'Dragon', ('Paralyzed', 30),0],
           'Fire Fang': [65, 15, 0, 1, 95, 'Fire', ("Burned",10),0],
           'Ember': [40, 25, 0, 1, 100, 'Fire', ('Burned', 10),1]}
POKEMON = {'pikachu': [120, 'Electric', ('Raichu', 20), 190, 24, 'iron tail', 'thunder', 'rock crush'],
           'charizard': [170, 'Fire', ('None', 0), 45, 5, 'flame thrower', 'rock crush']}
#pokeomon = {index: ["name", "type1/type2", hp, attack, defence, sp atk, sp def, speed, index of evolution, evo lvl, {lvl: [attack],...}]}
p2= {1:["Bulbasaur", "Grass/Poison", 45, 49, 49, 65, 65, 45, 2,16, {1: ("Tackle", "Growl"), 3: ("Vine Whip")}],
    2:["Ivysaur", "Grass/Poison", 45, 49, 49, 65, 65, 45, 3,32, {1: ["Tackle", "Growl"], 3: ["Vine Whip"]}]}
STATUSES ={'Burned': [-1,-1, 10, False, 100,"was hurt by it's burn.", ''],
           '':[-1,-1,0,False,100,'No status effect',''],
           'Confused':[-1,5,7,True, 60, "hurt itself in it's confusion.",'broke out of confusion'],
           'Fainted':[-1,-1,0,True, 100, "has fainted.", ''],
           'Paralyzed':[-1,-1,0,True,50,"can't move.",''],
           'Frozen':[-1,3,0,True,0,'is frozen.',"thawed out."],
           'Poisoned':[-1,-1,10,False,100,"was hurt by the poison.", ''],
           "Asleep":[2,5,0,True, 30,"is asleep", "woke up"]}
p1= {}
class PokemonNode:
    def __init__(self, index, name, type, stats, moves, basexp, growth_rate, catch_rate):
        self.index, self.name, self.type= index, name, type
        self.hp, self.atk, self.deff, self.sAtk, self.sDeff, self.spd = stats
        self.stats= stats
        self.out ={}
        self.attacks =[]
        self.tmMoves=[]
        self.basexp=basexp
        self.growth_rate= growth_rate
        self.catch_rate = catch_rate
        p1[index] = self
        for move, lvl, mode in moves:
            self.connect(Attack.make(self,move),lvl, mode)
    def connect(self, node, lvl, mode=1):
        if isinstance(node, Attack):
            if mode ==1:
                self.attacks.append(node)
            else:
                self.tmMoves.append(node)
        if mode ==1:
            if lvl in self.out:
                self.out[lvl].append(node)
            else:
                self.out[lvl] = [node]
        
    def make(self, lvl, catch_rate = None):
        if catch_rate is None:
            catch_rate= self.catch_rate
        return Pokemon(self.index,lvl, catch_rate)
class Pokemon:
    """
    Pokemon that can fight, level up and be potentially caught
    """
    def __init__(self, num, lvl, catchRate=0) -> None:
        pNode = p1[num]
        self.name, self.maxhp, self.hp, self.num, self.type = pNode.name, pNode.hp, pNode.hp, pNode.index-1, pNode.type
        self.level=0
        self.catch_rate=catchRate
        self.atk, self.deff, self.sAtk, self.sDeff, self.spd= pNode.stats[1:]
        self.attacks =[]
        i = 0
        self.xp= 0
        self.next_level=10
        self.node = pNode
        self.status = Status('')
        self.changes = [0,0,0,0,0]
        while self.level<lvl:
            nodes =self.level_up()
            if nodes !=[]:
                if isinstance(nodes[-1], PokemonNode):
                    i+=self.learn(nodes[:-1], i)
                else:
                    i+=self.learn(nodes, i)
        self.shiny = random.randint(1,SHINY) ==1
    def replace_attack(self, old_attack, new_attack):
        for attack in range(len(self.attacks)):
            if self.attacks[attack] == old_attack:
                self.attacks[attack] = new_attack
    def restore_stats(self):
        self.atk, self.deff, self.sAtk, self.sDeff, self.spd = self.stats
    def xp_for_level(self):
        lvl =self.level+1
        if self.node.growth_rate == "Medium Slow":
            return 6/5*(lvl**3)-15*(lvl**2)+100*lvl-140
        elif self.node.growth_rate == "Medium Fast":
            return lvl**3
        elif self.node.growth_rate == "Erratic":
            if lvl <50:
                return (100-lvl)/50*lvl**3
            elif 50<=lvl<68:
                return (150-lvl)/100*lvl**3
            elif 68<=lvl<98:
                return (1911-10*lvl)/1500*lvl**3
            return (160-lvl)/100*lvl**3
        elif self.node.growth_rate == "Fast":
            return 4/5*lvl**3
        elif self.node.growth_rate == "Slow":
            return 5/4*lvl**3
        else:#Fluctuating
            if lvl <15:
                num = lvl+1/3 +24
                return num/50*lvl**3
            elif 15<=lvl<36:
                num= (lvl+14)/50
                return num*lvl**3
            num = lvl/2 +32
            return num/50*lvl**3
    def level_up(self):
        self.level+=1
        self.atk+= self.atk/50
        self.deff+= self.deff/50
        self.sAtk+= self.sAtk/50
        self.sDeff+= self.sDeff/50
        self.spd+= self.spd/50
        hp= self.maxhp/50
        self.maxhp+=hp
        self.hp+=hp
        self.next_level = self.xp_for_level()
        self.stats = [self.atk, self.deff, self.sAtk, self.sDeff, self.spd]
        if self.level in self.node.out:
            return self.node.out[self.level]
        return []
    def evolve(self, node):
        new = node.make(self.level)
        self.hp += new.maxhp- self.maxhp
        self.name, self.maxhp, self.num, self.atk, self.deff, self.sAtk, \
            self.sDeff, self.spd=new.name, new.maxhp, new.num, new.atk, new.deff, new.sAtk, new.sDeff, new.spd
        
    def learn(self, attacks, index):
        for attack in attacks:
            if index>=len(self.attacks):
                self.attacks.append(copy.copy(attack))
            else:
                self.attacks[index] = copy.copy(attack)
            index+=1
            if index==4:
                index =0
        return index
    # def __init__(self, name, num,level,  catch_rate=-1):
    #     self.name = name
    #     self.shiny = random.randint(1,SHINY) ==1
    #     self.level = level
    #     pokemon = POKEMON[name]
    #     self.hp =pokemon[0]+(level-1)*2
    #     self.maxhp = self.hp
    #     self.type =pokemon[1]
    #     self.evolution = pokemon[2]
    #     self.attacks = []
    #     if catch_rate ==-1:
    #         self.catch_rate = pokemon[3]
    #     else:
    #         self.catch_rate = catch_rate
    #     if num is None:
    #         self.num = pokemon[4]
    #     else:
    #         self.num = num
    #     self.set_attacks(pokemon[5:])
    #     self.status = Status('')
    #     self.xp = 0
    #     self.next_level = self.level**3
    def __repr__(self):
        return self.name
    def add_xp(self, xp):
        self.xp += xp
        nodes = []
        while self.xp >= self.next_level:
            self.xp -= self.next_level
            nodes +=self.level_up()
        return nodes
    def set_attacks(self, attacks=None):
        if attacks is None:
            for attack in self.attacks:
                attack.damage += 2
            return
        for attack in attacks:
            a = ATTACKS[attack]
            self.attacks.append(Attack(attack, a[0]+(self.level-1)*4//3, a[1], a[2], a[3], a[4],a[5],a[6]))
    # def level_up(self):
    #     if self.level == MAX_LEVEL:
    #         return False
    #     self.level +=1
    #     self.set_attacks()
    #     self.next_level = self.level**3
    #     if self.level == self.evolution[1]:
    #         return True
    #     return False
    def set_hp(self, amount):
        if self.hp- amount >self.maxhp:
            self.hp = self.maxhp
        elif self.hp - amount <0:
            self.hp = 0
        else:
            self.hp = self.hp - amount
        if self.hp == 0:
            self.status = Status('Fainted')
    def dmgMulti(self, victim, attack):
        num =1
        types = victim.type.split("/")
        for t in types:
            if t in WEAKNESSES[attack.type]:
                num/2
            if t in STRENGTHS[attack.type]:
                num*2
        return num
    def attack(self,  victim, attack):
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
                if isinstance(attack, StatAttack):
                    if attack.user:
                        extra += attack.enact(self)
                    else:
                        extra += attack.enact(victim)
                elif attack.type == 'Heal':
                    self.status.name = ''
                    self.set_hp(attack.damage)
                    return extra +' and recovered some hp.',attack.damage
                else:
                    if attack.cat == 0:
                        damage = (2*self.level/5+2)*attack.damage*self.atk/victim.deff/50 +2
                    else:
                        damage = (2*self.level/5+2)*attack.damage*self.sAtk/victim.sDeff/50 +2
                    damage*= self.dmgMulti(victim, attack) 
                    victim.set_hp(math.trunc(damage))
                    sd = math.trunc(damage*attack.self_damage)
                    if sd != 0:
                        s = '.\n{} was hit with recoil during the attack'.format(self.name) +s
                        self.set_hp(sd)
                    extra += s
                    if attack.status[0] != '' and attack.status[1] >= random.randint(1,100):
                        victim.status = Status(attack.status[0])
                        extra += '.\n{} is now {}'.format(victim.name, victim.status.name)

            else:
                extra = '{} tried using {}, but {}.'.format(self.name, attack.name, self.status.description)
        else:
            extra = '{} tried using {}, but missed.'.format(self.name, attack.name)
        if status[0] != 0:
            self.set_hp(status[0])
            extra += '\n{} {}'.format(self.name, self.status.description)
        return extra
    def __str__(self):
        return "{},{},{},{},{},{},{}{}".format(self.name, self.level, self.hp,
                                                        self.xp, self.status.name, self.shiny, self.node.index, self.attack_str())
    def restore(self):
        self.hp = self.maxhp
        self.status = Status('')
        self.restore_stats()
        for attack in self.attacks:
            attack.pp= attack.max_pp
    def attack_str(self):
        if self.attacks == []:
            return ''
        s = ','
        for attack in self.attacks:
            s+= str(attack)+','
        return s[:-1]
    def attack_spd(self, attack):
        if attack.priority == 0:
            return math.trunc(self.spd*0.25)
        elif attack.priority == 2:
            return math.trunc(self.spd*2)
        return self.get_spd()
    def get_hp(self):
        return math.trunc(self.hp)
    def get_maxHp(self):
        return math.trunc(self.maxhp)
    def get_atk(self):
        return math.trunc(self.atk)
    def get_def(self):
        return math.trunc(self.deff)
    def get_sAtk(self):
        return math.trunc(self.sAtk)
    def get_sDef(self):
        return math.trunc(self.sDeff)
    def get_spd(self):
        return math.trunc(self.spd)

class Attack:
    '''
    name: name of attack
    damage: damage of attack to victim
    pp: how many time attack can be used
    self_damage: perctange of damage that gets inflicted onto user
    priorty: 0 means low priority, 2 means always go high priorty and 1 is normal
    accuracy: chance attack hits
    status: tuple of what status is possible from being hit from this attack
    and what is the likelyhood of the status working
    cat: 0 if the attack is phsyical and 1 if the attack is special
    '''
    def __init__(self,id, name, damage, pp, self_damage, speed,accuracy,type, status, cat, who):
        self.Id= id
        self.name = name
        self.damage = damage
        self.pp =self.max_pp= pp
        self.priority = speed
        self.type = type
        self.accuracy = accuracy
        self.self_damage = self_damage
        self.status = status[0], status[1]
        self.who = who
        self.cat = cat
    def make(self, name, pp=None):
        a = ATTACKS[name]
        atk =Attack(name, a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8])
        if pp is not None:
            atk.pp= pp
        return atk
    def use(self, player, pokemon, victim):
        status = pokemon.status.status_effect()
        s = []
        self.pp -= 1
        if status[1]:
            if pokemon.status.name !='':
                s.append(pokemon.status.snapOut)
            if self.accuracy >= random.randint(1,100) or self.effect ==18:
                s.append('{} used {}'.format(pokemon.name, self.name))
                if self.who == 13:
                    for p in player.bag.pokemons:
                        if p.get_hp()>0:
                            self.ennact(p,p)
                elif self.who == 10:
                    s.append(self.ennact(pokemon, victim))
                elif self.who == 7:
                    s.append(self.ennact(pokemon,pokemon))
            else:
                s.append('{} tried using {}, but missed.'.format(self.name, self.name))
        else:
            s.append('{} tried using {}, but {}.'.format(pokemon.name, self.name, self.status.description))
        if status[0] != 0:
            self.set_hp(status[0])
        return s

    def ennact(self, pokemon, victim):
        if self.effect ==2:
            victim.status = Status("Asleep")
        elif self.effect == 3:
            pass
        if isinstance(attack, StatAttack):
            if attack.user:
                extra += attack.enact(self)
            else:
                extra += attack.enact(victim)
        elif attack.type == 'Heal':
            self.status.name = ''
            self.set_hp(attack.damage)
            return extra +' and recovered some hp.',attack.damage
        else:
            if attack.cat == 0:
                damage = (2*self.level/5+2)*attack.damage*self.atk/victim.deff/50 +2
            else:
                damage = (2*self.level/5+2)*self.sAtk/victim.sDeff/50 +2
            damage*= self.dmgMulti(victim, attack) 
            victim.set_hp(math.trunc(damage))
            sd = math.trunc(damage*attack.self_damage)
            if sd != 0:
                s = '.\n{} was hit with recoil during the attack'.format(self.name) +s
                self.set_hp(sd)
            extra += s
            if attack.status[0] != '' and attack.status[1] >= random.randint(1,100):
                victim.status = Status(attack.status[0])
                extra += '.\n{} is now {}'.format(victim.name, victim.status.name)

    def __str__(self):
        return "({}/{})".format(self.Id, self.pp)
class StatAttack(Attack):
    def __init__(self, name, pp, accuracy, stat, boost,speed, user) -> None:
        Attack.__init__(self, name, 0, pp, 0,speed,accuracy,  "Normal",('',100), 0)
        self.stat = stat
        self.boost= boost
        self.user= user
        self.stats = {0:"Atk", 1:"Def", 2:"S.Atk", 3:"S.Def", 4:"Spd"}
    def lookup(self, pokemon, stat):
        if 6>=pokemon.changes[stat] >=0:
            return pokemon.stats[stat](1+pokemon.changes[stat]*0.5)
        elif pokemon.changes[stat] ==-1:
            return pokemon.stats[stat]*2/3
        elif pokemon.changes[stat] ==-2:
            return pokemon.stats[stat]*0.5
        elif pokemon.changes[stat] ==-3:
            return pokemon.stats[stat]*0.4
        elif pokemon.changes[stat] ==-4:
            return pokemon.stats[stat]/3 
        elif pokemon.changes[stat] ==-5:
            return pokemon.stats[stat]*0.285
        elif pokemon.changes[stat] ==-6:
            return pokemon.stats[stat]*0.25   
    def set_stat(self, pokemon, stat, num):
        if stat==0:
            pokemon.atk= num
        elif stat==1:
            pokemon.deff = num
        elif stat==2:
            pokemon.sAtk = num
        elif stat == 3:
            pokemon.sDeff= num
        else:
            pokemon.spd = num
    def enact(self, pokemon):
        if self.boost:
            pokemon.changes[self.stat] +=1
            s =self.lookup(pokemon, 0)
            if s is not None:
                self.set_stat(pokemon, self.stat,s)
                msg = "{}'s {} increased".format(pokemon.name, self.stats[self.stat])
            else:
                pokemon.changes[0] =6
                msg = "{}'s {} cannot be raised anymore".format(pokemon.name, self.stats[self.stat])
        else:
            pokemon.changes[self.stat]-=1
            s =self.lookup(pokemon, 0)
            if s is not None:
                self.set_stat(pokemon, self.stat,s)
                msg = "{}'s {} decreased".format(pokemon.name, self.stats[self.stat])
            else:
                pokemon.changes[0] =-6
                msg = "{}'s {} cannot be lowered anymore".format(pokemon.name, self.stats[self.stat])
        return msg        
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
        self.snapOut= s[6]
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
def makeAttack(num, pp = None):
    a = READATTACKS[num]
    atk =Attack(num, a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8], a[9])
    if pp is not None:
        atk.pp= pp
    return atk
from csv import reader
p3 ={}
with open('pokedex.csv', 'r',encoding="utf8") as file:
    csvReader = reader(file)
    header = next(csvReader)
    count = 0
    for row in csvReader:
        if count == 808:
            break
        index = int(row[1])
        if index in p1:
            continue
        name = row[2]
        if int(row[8]) ==2:
            Type = row[9]+'/'+row[10]
        else:
            Type = row[9]
        stats= [int(row[18]), int(row[19]), int(row[20]), int(row[21]), int(row[22]), int(row[23])]
        if row[24][-2:] == '.0':
            catch = int(row[24][:-2])
        else:
            catch= int(row[24])
        if row[26][-2:] == '.0':
            exp = int(row[26][:-2])
        else:
            exp= int(row[26])
        grow = row[27]
        count = index+1
        p3[name]= PokemonNode(index, name, Type, stats, [], exp, grow, catch)
TYPES= {1:"Normal", 2:"Fighting", 3:"Flying",
4:	'Poison',5:'Ground',6:	'Rock',7:'Bug',
8:	'Ghost',9:'Steel',10:	'Fire',
11:	'Water',12:'Grass',13:	'Electric',
14:	'Psychic',15:'Ice',16:	'Dragon',
17:	'Dark',18:'Fairy',10002:"Unknown"} 
EFFECTS={5:"Burned", 7:"Paralyzed", 6:"Frozen", 77:"Confused", 2:"Asleep"} 
READATTACKS= {} 
with open('moves.csv', 'r',encoding="utf8") as file:
    csvReader = reader(file)
    header = next(csvReader)
    count = 0
    for row in csvReader:
        if count >826:
            break
        cat = int(row[9])
        if cat ==2:
            cat = 0
        elif cat ==3:
            cat = 1
        else:
            cat = 2  
        name = row[1]
        Type = TYPES[int(row[3])]
        if row[4] == '':
            power =0
        else:
            power = int(row[4])
        pp= int(row[5])
        if row[6] == '':
            acc = 100
        else:
            acc = int(row[6])
        speed = int(row[7])
        if speed == 0:
            speed = 1
        elif speed > 0:
            speed = 2
        else:
            speed = 0
        sd = float(row[-3])
        effect = int(row[10])
        count = int(row[0])+1
        if int(row[10]) not in EFFECTS:
            effect = ('',100)
        else:
            if row[11] == '':
                row[11]= '100'
            effect = (EFFECTS[int(row[10])], int(row[11]))
        who =int(row[8])
        if power !=0:
            READATTACKS[count-1]= [name,power, pp, sd, speed, acc, Type, effect, cat,who]

with open('pokemon_moves.csv', 'r',encoding="utf8") as file:
    csvReader = reader(file)
    header = next(csvReader)
    count = 0
    savedPokemon = 0
    savedVersion =0
    for row in csvReader:
        pokemon = int(row[0])
        move    = int(row[2])
        method  = int(row[3])
        lvl     = int(row[4])
        if pokemon ==808:
            break
        if pokemon == savedPokemon and savedVersion!=int(row[1]):
            pass
        else:
            savedVersion= int(row[1])
            savedPokemon = pokemon
            r = row[:-1] +[row[-1][:-1]]
            if move in READATTACKS:
                p1[pokemon].connect(makeAttack(move), lvl, method!=4)
with open('evolution.csv', 'r',encoding="utf8") as file:
    csvReader = reader(file)
    header = next(csvReader)
    for row in csvReader:
        pokemon = row[0]  
        evoultion    = row[1]
        if row[2]!='':
            lvl  = int(row[2])
            p3[pokemon].connect(p3[evoultion], lvl)
print(Pokemon(270, 100))

        #print(row)
# bul = PokemonNode(1, p2[1][0], p2[1][1], p2[1][2:8],[])
# ivy = PokemonNode(2, p2[2][0], p2[2][1], p2[2][2:8],[])
# ven = PokemonNode(3,"Venusaur", "Grass/Poison", [80,82,83,100,100,80],[("iron tail",1),("thunder",1)])
# ch = PokemonNode(5, "Charmeleon", "Fire",[58,64,58,80,65,80],[("Scratch",1),("Ember",1),("Dragon Breath",12), ("Fire Fang",19)])
# PokemonNode(4, "Charmander", "Fire",[39,52,43,60,50,65],[("Scratch",1),("Ember",4),("Dragon Breath",12)]).connect(ch,16)
# ch.connect(PokemonNode(6, "Charizard", "Fire/Flying",[78,84,78,109,85,100],[("Scratch",1),("Ember",1),("Dragon Breath",12), ("Fire Fang",19), ("Flamethrower",30)]),36)
# war= PokemonNode(8,"Wartortle", "Water", [59,63,80,65,80,58],[])
# PokemonNode(7,"Squirtle", "Water", [44,48,65,50,64,43],[("Tackle",1), ("Water Gun",3), ("Rapid Spin", 9)]).connect(war,16)
# war.connect(PokemonNode(9,"Blastoise", "Water", [79,83,100,85,105,78],[("Tackle",1), ("Water Gun",3), ("Rapid Spin", 9)]),36)
# bul.connect(ivy, 16)
# list = ATTACKS["iron tail"]
# bul.connect(Attack("iron tail", list[0], list[1], list[2], list[3], list[4], list[5], list[6], list[7]), 1)
# print(bul.make(1), ivy.make(16), ch.make(30))
