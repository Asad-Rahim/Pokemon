#LOCATION = {'a':[('charizard',100, 1, 0)]}
LOCATION ={}
#Location maps to a list of all pokemon there with their spwan rate and their level
# probality of eveything in the list must equal one
TILE_LENGTH= 40
import pygame
pygame.init()
window = pygame.display.set_mode((550, 600))
pygame.display.set_caption('Pokemon')
import random

class Tile:
    def __init__(self, x, y, height = TILE_LENGTH, width= TILE_LENGTH):
        self.x, self.y, self.height, self.width = x, y, height, width
        self.left = self.right= self.up=self.down = None
    def walk_to(self, player):
        raise NotImplementedError
    def move_player(self, player):
        player.curr_tile = self
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
class Boundary_Tile(Tile):
    def __init__(self, x, y):
        Tile.__init__(self,x, y)
        self.colour = 46,46,46
    def walk_to(self, player):
        pass
class Wild_Tile(Tile):
    def __init__(self, x, y):
        Tile.__init__(self,x, y)
        self.colour = 0, 102, 9
    def walk_to(self, player):
        Tile.move_player(self, player)
        if random.randint(1,100) >75:
            print('Encounter')
            return PVE_Encounter(player,player.curr_location)

class Normal_Tile(Tile):
    def __init__(self, x, y):
        Tile.__init__(self, x, y)
        self.colour = 80, 240, 62
    def walk_to(self, player):
        self.move_player(player)
class Item_Tile(Tile):
    def __init__(self, x, y, item):
        Tile.__init__(self,x, y)
        self.colour = 237, 28, 46
        self.got = False
        self.item = item
    def walk_to(self, player):
        if not self.got:
            player.bag.add_item(self.item)
            print("You found a {}".format(self.item.name))
            self.got = True
            self.colour =  80, 240, 62
        else:
            self.move_player(player)
class Exit_Tile(Tile):
    def __init__(self,x,y,location):
        Tile.__init__(self,x,y)
        self.colour = 250, 235, 30
        self.new_location = location
    def walk_to(self, player):
        tile = self.new_location.exits[player.curr_location.id]
        player.curr_location = self.new_location
        player.curr_tile = self.safe_tile(tile)

    def safe_tile(self, tile):
        if tile.down is not None and not isinstance(tile.down, Boundary_Tile):
            return tile.down
        if tile.up is not None and not isinstance(tile.up, Boundary_Tile):
            return tile.up
        if tile.right is not None and not isinstance(tile.right, Boundary_Tile):
            return tile.right
        return tile.left


class Location:
    '''
    pokmeon:all possible pokemon that can be spawned and what their level can be
    location_id: uniue identifier number which will help correspond to
    where the end of each level ends
    '''
    def __init__(self, pokemon, file):
        self.pokemon = pokemon
        self.create_level(file)
    def create_level(self, file):
        f = open(file)
        text = f.readline()
        self.id = text.split(',')[2][0]
        self.width = int(text.split(',')[1])
        self.height = int(text.split(',')[0])
        l = []
        item_tiles =[]
        self.exits = {}
        for line in range(self.height):
            row = []
            text = f.readline()[:-1]
            for char in range(len(text)):
                if text[char] == '0':
                    tile = Boundary_Tile(char*TILE_LENGTH,line*TILE_LENGTH)
                elif text[char] == '1':
                    tile = Wild_Tile(char*TILE_LENGTH,line*TILE_LENGTH)
                elif text[char] == '2':
                    tile = Normal_Tile(char*TILE_LENGTH,line*TILE_LENGTH)
                elif text[char] == '*':
                    tile = Item_Tile(char * TILE_LENGTH, line * TILE_LENGTH, None)
                    item_tiles.append(tile)
                else:
                    tile = Exit_Tile(char * TILE_LENGTH, line * TILE_LENGTH,text[char])
                    self.exits[text[char]] = tile
                if len(row) >0:
                    row[-1].right, tile.left = tile, row[-1]
                if len(l) >0:
                    l[-1][len(row)].down, tile.up = tile, l[-1][len(row)]
                row.append(tile)
            l.append(row)
        text = f.readline()
        count = 0
        while text != 'EOF':
            for item in item_tiles:
                item.item = BALLS[text[1]]
            text = f.readline()
            count += 1
        LOCATION[self.id] = self
        self.start = l[0][0]
        f.close()
def str_to_status(str):
    s = STATUSES[str]
    return Status(str, s[0], s[1], s[2], s[3], s[4],s[5])
class Bag:
    def __init__(self):
        self.items ={}
        self.pokemons = []
    def add_pokemon(self, pokemon):
      #precondition len(self.pokemons)<6
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
            self.items[item] +=1
        else:
            self.items[item] = 1
    def remove_item(self, item):
        self.items[item] -=1
    def consume_item(self, item, pokemon):
        if self.items[item] >0:
            self.remove_item(item)
            return item.use(pokemon)
        return "You don't have anymore of this item."

class Player:
    def __init__(self, name, location, tile):
        self.name = name
        self.bag = Bag()
        self.inventory = []
        self.main = None
        self.x = 50
        self.y = 50
        self.height = 60
        self.width = 40
        self.curr_location = location
        self.curr_tile = tile
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
        self.used = [self.player_pokemon]
        self.location = location
        self.get_enemy()
        self.turn = 0
    def get_enemy(self):
        l = []
        for pokemon in self.location.pokemon:
            for i in range(pokemon[1]):
                l.append(pokemon)
        pokemon = l[random.randint(0,len(l)-1)]
        self.enemy = Pokemon(pokemon[0], pokemon[2], pokemon[3])
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
                if self.game_on():
                    print(self.player_pokemon.attack( self.enemy, p))
            else:
                print(self.player_pokemon.attack( self.enemy, p))
                if self.game_on():
                    print(self.enemy.attack( self.player_pokemon, en))
    def play(self, attack):
        self.turn +=1
        print("Turn #{}".format(self.turn))
        en = self.enemy_move()
        if en.speed > attack.speed:
            print(self.enemy.attack(self.player_pokemon, en))
            if self.game_on():
                print(self.player_pokemon.attack(self.enemy, attack))
        else:
            print(self.player_pokemon.attack(self.enemy, attack))
            if self.game_on():
                print(self.enemy.attack(self.player_pokemon, en))
        print("{} health:{}\t{} health:{}".format(self.player_pokemon.name, self.player_pokemon.hp,
                                                          self.enemy.name, self.enemy.hp))
    def game_on(self):
        return self.player_pokemon.hp >0 and self.enemy.hp >0
    def catch(self):
        ball = input('What ball do you want?\nP-Poke ball\nG-Great ball\nU-Ultra ball\nM-Master Ball')
        for key, item in self.player.bag.items.items():
            if key.name[0] == ball and item >0:
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
        self.used.append(pokemon)
    def xp_gain(self):
        xp = self.enemy.level*random.randint(90,110)
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
                    new_pokemon = Pokemon(pokemon.evolution[0], pokemon.evolution[1])
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


POKEMON= {'pikachu':[120,'Electrike', ('Raichu', 20),190,'iron tail','thunder', 'rock crush'],
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
        return evolution
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
                    if attack.status[0] != '' and attack.status[1] >= random.randint(1,100):
                        victim.status = str_to_status(attack.status[0])
                        extra += '.\n{} is now {}'.format(victim.name, victim.status.name)

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
    def catch(self, pokemon):
         return 4


BALLS ={'P': Ball('Poke ball', 1), 'U':Ball('Ultra ball', 1.25), 'G':Ball('Great ball', 1.125),
 'M':MasterBall('Master ball', 1)}




def print_tile(tile, direction):
    pygame.draw.rect(window, tile.colour,(tile.x,tile.y, tile.height,tile.width))
    if (direction and tile.right is None and tile.down is None) or \
            (not direction and tile.left is None and tile.down is None):
        return
    elif (direction and tile.right is None) or (not direction and tile.left is None):
        return print_tile(tile.down, not direction)
    if direction:

        return print_tile(tile.right, direction)
    return print_tile(tile.left, direction)


def UI_encounter(encounter):
    pygame.display.set_mode((550,700))
    while encounter.game_on():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
        pygame.time.delay(100)
        window.fill((0, 0, 0))
        pygame.draw.circle(window, (255, 255, 255), (120, 280), 80)
        pygame.draw.circle(window, (255, 255, 255), (400, 100), 80)
        #pygame.draw.rect(window, (255, 255, 255), (350, 450, 150, 80))
        font = pygame.font.Font('freesansbold.ttf', 18)
        font2 = pygame.font.Font('freesansbold.ttf', 14)
        run_txt = font.render("Run", True, (0,0,0),(255,255,255))
        runrect = run_txt.get_rect()
        runrect.center= (260,630)
        run_btn = pygame.draw.rect(window, (255, 255, 255), (200, 600, 120, 60))
        window.blit(run_txt, runrect)

        catch_txt = font.render("Catch", True, (0, 0, 0), (255, 255, 255))
        catch_rect = catch_txt.get_rect()
        catch_rect.center = (450, 630)
        catch_btn = pygame.draw.rect(window, (255, 255, 255), (430, 600, 120, 60))
        window.blit(catch_txt, catch_rect)
        attacks = []
        run_btn = pygame.draw.rect(window, (255, 255, 255), (200, 600, 120, 60))
        window.blit(run_txt, runrect)

        p_hp = font.render("{}/{}".format(encounter.player_pokemon.hp,
                                          encounter.player_pokemon.maxhp), True, (46,46,46),(255,255,255))
        e_hp = font.render("{}/{}".format(encounter.enemy.hp, encounter.enemy.maxhp),
                           True, (46,46,46),(255,255,255))
        e_rect = e_hp.get_rect()
        e_rect.center = (500,50)
        p_rect = p_hp.get_rect()
        p_rect.center = (100, 180)
        window.blit(p_hp, p_rect)
        window.blit(e_hp, e_rect)
        for i in  range(len(encounter.player_pokemon.attacks)):
            a = encounter.player_pokemon.attacks[i]
            big_text = font.render(a.name, True, (0, 0, 0), (255, 255, 255))
            lil_text = font2.render("{}    {}/{}".format(a.type, a.pp, a.max_pp), True, (0, 0, 0),
                                 (255, 255, 255))
            text1Rect = big_text.get_rect()
            text2Rect = lil_text.get_rect()
            x = 125 + (i%2)*250
            y = 450 +(i>1)*90
            text1Rect.center = (x, y)
            text2Rect.center = (x, y+20)
            attacks.append((pygame.draw.rect(window, (255, 255, 255), (x-75, y-30, 150, 70)), a))
            window.blit(big_text, text1Rect)
            window.blit(lil_text, text2Rect)
        '''
        for attack in range(len(encounter.player_pokemon.attacks)):
            if attack %2 == 0:
        attack1 =encounter.player_pokemon.attacks[0]
        attack2 =encounter.player_pokemon.attacks[1]
        
        
        
        text3Rect = text1.get_rect()
        text4Rect = text2.get_rect()

        # set the center of the rectangular object.
        text1Rect.center = (125 , 520)
        text2Rect.center = (425, 520)
        text3Rect.center = (125, 540)
        text4Rect.center = (425, 540)
        '''

        #window.blit(text2, text2Rect)
        #window.blit(text3, text3Rect)
        #window.blit(text4, text4Rect)
        pygame.display.update()
        pos = pygame.mouse.get_pos()
        pressed1, pressed2, pressed3 = pygame.mouse.get_pressed()
        if run_btn.collidepoint(pos) and pressed1:
            break
        if catch_btn.collidepoint(pos) and pressed1:
            temp = encounter.catch()
            print(temp)
            if temp[:5] == 'Nice!':
                break
        for a in attacks:
            if a[0].collidepoint(pos) and pressed1:
                encounter.play(a[1])



if __name__ == '__main__':
    import doctest
    doctest.testmod()
    Location([('charizard',100, 1, 100)], "test_A.txt")
    l = Location([('charizard',100, 1, 0)], 'test_level.txt')
    pygame.display.set_mode((l.width * TILE_LENGTH, l.height * TILE_LENGTH))
    print(LOCATION)
    for id, location in LOCATION.items():
        for key, tile in location.exits.items():
            tile.new_location = LOCATION[key]
    Asad = Player('Asad', l, l.start.right.down)
    s = POKEMON['pikachu']
    Asad.add_pokemon(Pokemon('pikachu', 5))
    print_tile(l.start, True)
    pygame.draw.circle(window, (30, 213, 230),(Asad.curr_tile.x+TILE_LENGTH//2, Asad.curr_tile.y+TILE_LENGTH//2),20)
    pygame.display.update()
    encounter = None
    run = True
    #e = PVE_Encounter(Asad, Asad.curr_location)
    #print(e.catch())
    #UI_encounter(PVE_Encounter(Asad, Asad.curr_location))
    curr = Asad.curr_location
    while run:
        pygame.time.delay(200)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False


        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            encounter = Asad.curr_tile.left.walk_to(Asad)
        elif keys[pygame.K_d]:
            encounter = Asad.curr_tile.right.walk_to(Asad)
        elif keys[pygame.K_w]:
            encounter = Asad.curr_tile.up.walk_to(Asad)
        elif keys[pygame.K_s]:
            encounter = Asad.curr_tile.down.walk_to(Asad)
        window.fill((0, 0, 0))
        if curr != Asad.curr_location:
            curr = Asad.curr_location
            pygame.display.set_mode((curr.width*TILE_LENGTH, curr.height*TILE_LENGTH))
        print_tile(Asad.curr_location.start, True)
        pygame.draw.circle(window, (30, 213, 230),
                           (Asad.curr_tile.x + TILE_LENGTH // 2, Asad.curr_tile.y + TILE_LENGTH // 2), 20)
        pygame.display.update()
        if encounter is not None:
            UI_encounter(encounter)
            encounter = None
            pygame.display.set_mode((curr.width * TILE_LENGTH, curr.height * TILE_LENGTH))
    pygame.quit()
    p = Pokemon('pikachu', 5)
    e = PVE_Encounter(p, 'a')
    e.play()
    print(e.player.hp)
    print(e.enemy.hp)