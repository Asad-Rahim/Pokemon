#LOCATION = {'a':[('charizard',100, 1, 0)]}
import math, copy
import pygame

from pygame.time import delay

LOCATION ={}
#Location maps to a list of all pokemon there with their spwan rate and their level
# probality of eveything in the list must equal one
TILE_LENGTH= 40
import ctypes
ctypes.windll.user32.SetProcessDPIAware()

import pygame
pygame.init()

WIDTH, HEIGHT = pygame.display.Info().current_w,pygame.display.Info().current_h
screen_w, screen_h = WIDTH-350, HEIGHT-200
#WIDTH, HEIGHT= 550, 600
#window = pygame.display.set_mode((WIDTH,HEIGHT))
window = pygame.display.set_mode((WIDTH,HEIGHT), pygame.FULLSCREEN)
#screen_dimensions = WIDTH-180//TILE_LENGTH,HEIGHT-120//TILE_LENGTH
pygame.display.set_caption('Pokemon')
import random
class SpriteSheet:
    def __init__(self, file, rows, collums):
        self.sheet = pygame.image.load(file)
        self.rows, self.collums, self.total = rows, collums, rows*collums
        self.rect = self.sheet.get_rect()

        self.cellWidth, self.cellHeight = self.rect.width/collums, self.rect.height/rows
        self.cells = list([(int(index%collums*self.cellWidth), int(index//collums*self.cellHeight),
                            self.cellWidth,self.cellHeight)for index in range(self.total)])
        h,w = -self.cellHeight/2, -self.cellWidth/2
        self.offset = [(0,0),(w,0),(2*w,0),(0,h),(w,h),(2*w,h),(0,2*h),(w,2*h),(2*w,2*h),(w/2,h)]
    def draw(self,surface, cellIndex, x,y, offset = 0, scale = 64):
        if scale != self.sheet.get_rect()[2]/self.collums:
            image = pygame.transform.scale(self.sheet, (scale*self.collums, scale*self.rows))
            scalar = scale/(self.sheet.get_rect()[2]/self.collums)
            cell = self.cells[cellIndex][0]*scalar, self.cells[cellIndex][1]*scalar,\
                   self.cells[cellIndex][2]*scalar, self.cells[cellIndex][3]*scalar
            return surface.blit(image,(x+scalar*self.offset[offset][0],y+self.offset[offset][1]*scalar), cell)
        else:
            return surface.blit(self.sheet,(x+self.offset[offset][0],y+self.offset[offset][1]),self.cells[cellIndex])


class Tile:
    """
    Basic tile class. Tiles are what the player walks around on in the screen
    """
    def __init__(self, spriteNum = None, height = TILE_LENGTH, width= TILE_LENGTH):
        self.height, self.width, self.num = height, width, spriteNum
        self.left = self.right= self.up=self.down = None
    def walk_to(self, player):
        raise NotImplementedError
    def move_player(self, player):
        player.curr_tile = self

class Boundary_Tile(Tile):
    """
    Tiles that cannot be steped on
    """
    def __init__(self,num, colour = None):
        Tile.__init__(self,num)
        if colour is None:
            self.colour = 46,46,46
        else:
            self.colour = colour
    def walk_to(self, player):
        pass
    def print(self):
        return "B,{}".format(self.num)
class Wild_Tile(Tile):
    """
    Tiles that can be stepped on. When walking on one of these tiles, there is a 25% a pokemon encounter will occur
    """
    def __init__(self,num, colour = None):
        Tile.__init__(self,num)
        if colour is None:
            self.colour = 0, 102, 9
        else:
            self.colour = colour
    def walk_to(self, player):
        Tile.move_player(self, player)
        if random.randint(1,100) >75:
            print('Encounter')
            return PVE_Encounter(player,player.curr_location)
    def print(self):
        return "W,{}".format(self.num)
class Normal_Tile(Tile):
    """
    Tile that can be walked on. Nothing special happens when walked on
    """
    def __init__(self, num, colour=None):
        Tile.__init__(self, num)
        if colour is None:
            self.colour = 80, 240, 62
        else:
            self.colour = colour
    def walk_to(self, player):
        self.move_player(player)

    def print(self):
        return "N,{}".format(self.num)
class Item_Tile(Tile):
    """
    Tile that holds an Item. If the user wants to walk on this tile and an item is on it, they will pick up the item and
    stay on that tile. Then this tile will become like a Normal Tile

    def __int__(self, tile,item, colour = None):
        self.tile = tile
        if colour is None:
            self.colour = 237, 28, 46
        else:
            self.colour = colour
        self.got = False
        self.item = item
    """
    def __init__(self, num, item,tile, colour = None):
        Tile.__init__(self,num)
        self.next_tile = tile
        if colour is None:
            self.colour = 237, 28, 46
        else:
            self.colour = colour
        self.got = False
        self.item = item

    def walk_to(self, player):
        if not self.got:
            player.bag.add_item(self.item)
            player.dialogue = "You found a {}".format(self.item.name)
            Asad.stopped = True
            print("You found a {}".format(self.item.name))
            self.got = True
            self.colour =  self.next_tile.colour
        else:
            self.next_tile.move_player(player)
            if player.curr_tile == self.next_tile:
                Tile.move_player(self, player)
    def print(self):
        if self.got:
            return self.next_tile.print()
        return 'I,{}/{}'.format(self.item.name, self.next_tile.print())
class Exit_Tile(Tile):
    """
    Tile that connects a level to the next
    """
    def __init__(self,num,location, colour = None):
        """
        Location is normally the Location object. But during intialization it is the id
        This is because not all the locations have been made yet. So, the exit tile can't point to the tiles yet.
        Once all the locations have been created, the location for each tile gets updated
        """
        Tile.__init__(self,num)
        if colour is None:
            self.colour = 250, 235, 30
        else:
            self.colour = colour
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

    def print(self):
        return '{},E,{}'.format(self.new_location.id, self.num)
class LoadSave:
    def __init__(self, file):
        f = open(file)
        self.file = f
        txt = f.readline().split(',')
        self.playerName, self.playerStance = txt[0], int(txt[1][:-1])
        txt = f.readline()
        self.party = []
        self.inventory = []
        if "]" in txt:
            partyPokemon = txt.split("]")
            self.party.append(self.readPokemon(partyPokemon[0]))
            for pokemon in partyPokemon[1:-1]:
                self.party.append(self.readPokemon(pokemon[1:]))
        txt = f.readline()
        if "]" in txt:
            inventoryPokemon = txt.split("]")
            self.inventory.append(self.readPokemon(inventoryPokemon[0]))
            for pokemon in inventoryPokemon[1:-1]:
                self.inventory.append(self.readPokemon(pokemon[1:]))
        txt = f.readline()
        self.items = {}
        if txt != "\n":
            items = txt.replace("\n", '').split(',')
            for item in items:
                info = item.split("/")
                self.items[ITEMS[info[0]]] = int(info[1])
        txt = f.readline()
        self.locations = {}
        while txt[:3] == 'SOL':
            l = Location( f)
            self.locations[l.id] = l
            txt = f.readline()
        self.spawn = None
        for id, location in self.locations.items():
            if location.spawn_point is not None:
                self.spawn = location, location.spawn_point
            for key, tile in location.exits.items():
                tile.new_location = self.locations[key]

    def readPokemon(self, text):
        info = text[1:].split(",")
        pokemon = Pokemon(info[0],int(info[-1]),int(info[1]))
        pokemon.hp, pokemon.maxhp =int(info[2]), int(info[3])
        pokemon.status = str_to_status(info[-3])
        pokemon.shiny = bool(info[-2])
        pokemon.xp = int(info[-4])
        pokemon.attacks =[]
        for potentialAttacks in info[4:8]:
            if potentialAttacks[0] == '(':
                pokemon.attacks.append(self.readAttack(potentialAttacks))
        return pokemon
    def readAttack(self, text):
        info = text[1:-1].split("/")
        a = ATTACKS[info[0]]
        attack = Attack(info[0], int(info[1]), int(a[1]), float(a[2]), int(a[3]), int(a[4]), a[5], a[6])
        attack.pp = int(info[2])
        return attack
    def loadPlayer(self, player):
        player.name, player.stance = self.playerName, self.playerStance
        player.bag.pokemons = self.party
        if len(self.party) >0:
            player.change_main(self.party[0])
        player.inventory = self.inventory
        player.bag.items = self.items
        player.curr_location, player.curr_tile = self.spawn
    def save(self, player):
        s= player.print()+'\n'
        for location in self.locations.values():
            s+= print_location(location, player)
        f = open("Save.txt", "w+")
        f.write(s +'EOF')
        f.close()
        return s+'EOF'
class Location:
    '''
    pokmeon:all possible pokemon that can be spawned and what their level can be
    location_id: uniue identifier number which will help correspond to
    where the end of each level ends
    '''

    def __init__(self, openfile):
        self.pokemon = []
        self.spawn_point = None
        self.create_level(openfile)
    def pokemon_list(self, f):
        text = f.readline()
        while text != "EOPL\n":
            t = text.split(",")
            t[-1] = t[-1][:-1]
            for i in range(1, len(t)):
                t[i] = int(t[i])
            self.pokemon.append(tuple(t))
            text = f.readline()
    def create_tile_dict(self, f):
        txt = f.readline()
        self.tileDict = {}
        while txt != "EOD\n":
            info = txt.replace('\n', '').split(',')
            if info[1] == 'I':
                self.tileDict[info[0]]= (info[1],info[2], info[3])
            else:
                self.tileDict[info[0]]= (info[1], info[2])
            txt = f.readline()

    def create_level(self, f):
        self.pokemon_list(f)
        self.create_tile_dict(f)
        text = f.readline()
        self.id = text.split(',')[2][0]
        self.width = int(text.split(',')[1])
        self.height = int(text.split(',')[0])
        l = []
        item_tiles ={}
        self.exits = {}
        for line in range(self.height):
            row = []
            text = f.readline()[:-1]
            char = 0
            while char < len(text):
                tile, char = self.get_tile(text, char, item_tiles)
                if len(row) >0:
                    row[-1].right, tile.left = tile, row[-1]
                if len(l) >0:
                    l[-1][len(row)].down, tile.up = tile, l[-1][len(row)]
                row.append(tile)
            l.append(row)
        for item, tiles in item_tiles.items():
            for tile in tiles:
                tile.item = ITEMS[item]
        self.start = l[0][0]

    def get_tile(self, text, i, item_tiles):
        if text[i] == "S":
            t = self.get_tile(text, i + 1, item_tiles)[0]
            self.spawn_point = t
            return t, i + 2
        elif self.tileDict[text[i]][0] == 'E':
            t = Exit_Tile(self.tileDict[text[i]][1],text[i])
            self.exits[text[i]] = t
            return t, i+1
        elif self.tileDict[text[i]][0] == 'B':
            return Boundary_Tile(self.tileDict[text[i]][1]), i+1
        elif self.tileDict[text[i]][0] == 'W':
            return Wild_Tile(self.tileDict[text[i]][1]), i+1
        elif self.tileDict[text[i]][0] == 'N':
            return Normal_Tile(self.tileDict[text[i]][1]), i+1
        elif self.tileDict[text[i]][0] == 'I':
            t = Item_Tile(None, None, self.get_tile(self.tileDict[text[i]][2], 0, [])[0])
            if self.tileDict[text[i]][1] in item_tiles:
                item_tiles[self.tileDict[text[i]][1]].append(t)
            else:
                item_tiles[self.tileDict[text[i]][1]] = [t]
            return t, i + 1
        else:
            t = Item_Tile(0,0, None,None)
            if text[i] in item_tiles:
                item_tiles[text[i]].append(t)
            else:
                item_tiles[text[i]]=[t]
            return t, i+1

def str_to_status(str):
    '''
    used to create statuses using the global dicts. made for simple use in testing
    '''
    s = STATUSES[str]
    return Status(str, s[0], s[1], s[2], s[3], s[4],s[5])
def print_location(location, player):
    d = {}
    tiles = ''
    available = '0123456789-=!@#$%^&*()_+'
    curr = 0
    left = location.start
    tile = location.start
    while tile is not None:
        if isinstance(tile, Item_Tile) and not tile.got:
            info = tile.print()
            if info.split('/')[1] in d:
                char = d[info.split('/')[1]]
            else:
                d[info.split('/')[1]] = available[curr]
                char = available[curr]
                curr += 1
            info = info.split('/')[0]+','+char
        else:
            info = tile.print()
        if isinstance(tile, Exit_Tile):
            char = tile.new_location.id
            d[info[2:]] = tile.new_location.id
        elif info in d:
            char = d[info]
        else:
            d[info] = available[curr]
            char = available[curr]
            curr +=1
        if tile is player.curr_tile:
            tiles+= 'S'
        tiles+= char
        if tile.right is not None:
            tile = tile.right
        else:
            tile = left.down
            left = left.down
            tiles+='\n'
    s = ''
    for pokemon in location.pokemon:
        s += '{},{},{},{},{},{}\n'.format(pokemon[0],pokemon[1],pokemon[2],pokemon[3],pokemon[4],pokemon[5])
    s += "EOPL\n"
    for key, item in d.items():
        s += "{},{}".format(item, key)+'\n'
    i = 'EOD\n{},{},{}\n'.format(location.height, location.width, location.id)
    return "SOL\n"+s+i+tiles





class Bag:
    """
    A bag which the player holds containg everything they have on them. Limited to 6 pokemon
    """
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
    def print_pokemons(self):
        s = ''
        for pokemon in self.pokemons:
            s+= '['+str(pokemon)+'],'
        return s[:-1]
    def print_items(self):
        s = ''
        for item, count in self.items.items():
            s += '{}/{}'.format(item.name, count)+','
        return s[:-1]
class Player:
    """
    Actual player
    """
    def __init__(self, name, location, tile):
        self.name = name
        self.bag = Bag()
        self.dialogue = ''
        self.stopped = False
        self.inventory = []
        self.main = None
        self.x = 50
        self.y = 50
        self.height = 60
        self.width = 40
        self.curr_location = location
        self.curr_tile = tile
        self.stance = None
    def add_pokemon(self, pokemon):
        if len(self.bag.pokemons) == 6:
            self.inventory.append(pokemon)
        else:
            self.bag.add_pokemon(pokemon)
            if self.main is None:
                self.change_main(pokemon)
    def change_main(self, pokemon):
        #pokemon must be in bag
        self.bag.pokemons[0], self.bag.pokemons[self.bag.pokemons.index(pokemon)]=\
            self.bag.pokemons[self.bag.pokemons.index(pokemon)], self.bag.pokemons[0]
        self.main = self.bag.main = pokemon
    def make_corners(self):
        """
        creatig the moving screen corners of the player using their current location.
        These cornors allow the screen to stop and start following at certain distances from the edge
        """
        x, y = screen_dimensions
        x, y = x-1,y-1
        left,right = self.curr_tile, self.curr_tile
        while x >0:
            if left.left is not None:
                left = left.left
                x -= 1
            if right.right is not None:
                right = right.right
                x -= 1
            if left.left is None and right.right is None:
                x = 0
        up_left, down_left, up_right, down_right = left, left, right,right
        while y>0:
            if up_left.up is not None:
                up_left = up_left.up
                y -=1
                up_right = up_right.up
            if down_left.down is not None:
                down_left = down_left.down
                down_right = down_right.down
                y -= 1
            if up_left.up is  None and down_left.down is  None:
                y = 0
        self.corners = [up_left, up_right, down_left, down_right]
    def print(self):
        s = self.bag.print_pokemons()+'\n'
        i = ''
        for pokemon in self.inventory:
            i += '[' + pokemon + '],'
        i= i[:-1]+'\n'
        return self.name+','+str(self.stance)+'\n'+s +i+ self.bag.print_items()

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
        self.enemy = Pokemon(pokemon[0], pokemon[1], random.randint(pokemon[3],pokemon[4]), pokemon[5])
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
                if self.game_on()==0:
                    print(self.player_pokemon.attack( self.enemy, p))
            else:
                print(self.player_pokemon.attack( self.enemy, p))
                if self.game_on()==0:
                    print(self.enemy.attack( self.player_pokemon, en))
    def play(self, attack):
        self.turn +=1
        print("Turn #{}".format(self.turn))
        en = self.enemy_move()
        if isinstance(attack, Healables):
            s = "{} used a {}".format(self.player, attack.name)
            s += self.enemy.attack(self.player_pokemon, en)
            return s
        elif isinstance(attack, Ball):
            s = "{} threw a {}. But {} broke out".format(self.player, attack.name, self.enemy.name)
            s += self.enemy.attack(self.player_pokemon, en)
            return s
        if en.speed > attack.speed:
            print(self.enemy.attack(self.player_pokemon, en))
            if self.game_on()==0:
                print(self.player_pokemon.attack(self.enemy, attack))
        else:
            print(self.player_pokemon.attack(self.enemy, attack))
            if self.game_on()==0:
                print(self.enemy.attack(self.player_pokemon, en))
        print("{} health:{}\t{} health:{}".format(self.player_pokemon.name, self.player_pokemon.hp,
                                                          self.enemy.name, self.enemy.hp))
    def game_on(self):
        '''
        return an int based on what state the game is in:
        0=enemmy and player pokemon are both alive
        1= enemy is alive but player pokemon has fainted
        2= player pokemon is alive but enememy has fainted
        3= enemy has been caught
        4= all pokemon in party have fainted
        '''
        if self.enemy.hp>0 and self.player.main.hp>0:
            return 0
        if self.player.pokemon.hp==0:
            for pokemon in self.player.bag.pokemons:
                if pokemon.hp>0:
                    return 1
            return 4
        if self.enemy.hp==0:
            return 2
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


POKEMON= {'pikachu':[120,'Electrike', ('Raichu', 20),190,0,'iron tail','thunder', 'rock crush'],
          'charizard':[170,'Fire', ('None', 0), 45,4,'flame thrower', 'rock crush']}
ATTACKS={'iron tail': [30,15,0.0,70,100, 'Normal',('',100)], 'thunder':[65, 5, 0.2,80,80, 'Electrike',('',100)],
         'flame thrower':[40,15, 0.0, 70,95,'Fire',('Burned', 50)], 'rock crush':[55,5,0.1, 40,70, 'Ground',('',100)]}
WEAKNESSES ={'Fire':['Water'], 'Electrike':['Ground'], 'Normal': [],'Ground': []}
STRENGTHS ={'Fire':['Grass', 'Flying'], 'Electrike':[], 'Normal':[],'Ground': []}
MAX_LEVEL =999
class Pokemon:
    """
    Pokemon that can fight, level up and be potentially caought
    """
    def __init__(self, name, num,level,  catch_rate=-1):
        self.name = name
        self.shiny = random.randint(1,1000) ==1
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
        self.status = str_to_status('')
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
                pokemon = Pokemon(self.evolution[0], self.evolution[1])
                self.swap_pokemon(pokemon)
    def evolve_into(self, other):
        self.name,self.maxhp, self.hp= other.name,other.maxhp, self.hp+(other.maxhp-self.maxhp)
        self.status = str_to_status('')
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
            self.status = str_to_status('Fainted')
    def attack(self, victim, attack):
        """
        use attack on victim. Doesn't nessecarly mean dmaage victim. Also return a descriotion of what happened.
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
    def __str__(self):
        return "{},{},{},{},{},{},{},{},{}".format(self.name, self.level, self.hp, self.maxhp,self.attack_str(),
                                                        self.xp, self.status.name, self.shiny, self.sprite_num)
    def attack_str(self):
        s = ''
        for attack in self.attacks:
            s+= str(attack)+','
        return s[:-1]
STATUSES ={'Burned': [-1,-1, 10, False, 100,"was hurt by it's burn."],
           '':[-1,-1,0,False,100,'No status effect'],
           'Confused':[2,5,7,True, 60, "hurt itself in it's confusion."],
           'Fainted':[-1,-1,0,True, 100, "has fainted."]}
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


BALLS ={'P': Ball('Poke ball', 1, 'Used to catch pokemon.'),
        'U':Ball('Ultra ball', 1.25, 'Used to catch pokemon.'), 'G':Ball('Great ball', 1.125, 'Used to catch pokemon.'),
 'M':MasterBall('Master ball', 1, 'Used to immediatly catch any pokemon.')}
ITEMS ={'Poke ball': Ball('Poke ball', 1, 'Used to catch pokemon.'),
        'Ultra ball':Ball('Ultra ball', 1.25, 'Used to catch pokemon.'), 'Great ball':Ball('Great ball', 1.125, 'Used to catch pokemon.'),
        'Master ball':MasterBall('Master ball', 1, 'Used to immediatly catch any pokemon.'),
        'Full Restore':Healables('Full Restore',None,0,'Cure all status effects and fully heal pokemon.',True,True)}
def swap_menu(encounter):
    player = encounter.player
    x = 660
    pygame.draw.rect(window, (89, 235, 240),(x,180,max(100*len(player.bag.pokemons),400),270))
    window.blit(
        font.render("Who would you like to send out?", True, (46, 46, 46), (89, 235, 240)),
        (x+20, 200))
    font2 = pygame.font.SysFont('georgia', 15)

    if encounter.player_pokemon.hp>0:
        close = window.blit(font.render("Cancel", True, (46, 46, 46), (89, 235, 240)), (660, 450))
    else:
        close = None
    pokemons = []
    sprites.draw(window, encounter.player_pokemon.num, x, 220, 0, 90)
    window.blit(font2.render("HP:{}/{}".format(encounter.player_pokemon.hp, encounter.player_pokemon.maxhp),
                             True, (46, 46, 46), (89, 235, 240)), (x, 220 + 90 + 10))
    window.blit(font2.render("Status:" + str(encounter.player_pokemon.status.name),
        True, (46, 46, 46), (89, 235, 240)), (x, 220 + 90 + 30))
    x+=100
    for i in range(len(player.bag.pokemons)):
        if player.bag.pokemons[i] != encounter.player_pokemon:
            sprites.draw(window, player.bag.pokemons[i].num, x, 220, 0, 90)
            window.blit(font2.render("HP:{}/{}".format(player.bag.pokemons[i].hp, player.bag.pokemons[i].maxhp),
                                     True, (46, 46, 46), (89, 235, 240)), (x, 220 + 90 + 10))
            window.blit(font2.render(
                "Status:" + str(player.bag.pokemons[i].status.name),
                True, (46, 46, 46), (89, 235, 240)), (x, 220 + 90 + 30))
            if player.bag.pokemons[i].hp>0:
                temp = window.blit(font.render("Swap To", True, (46, 46, 46), (89, 235, 240)), (x, 220 + 90 + 50))
                pokemons.append((temp, player.bag.pokemons[i]))
            x += 100
    pygame.display.update()
    loop = True
    while loop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                loop = run = False
        keys = pygame.key.get_pressed()
        pos = pygame.mouse.get_pos()
        pressed1, pressed2, pressed3 = pygame.mouse.get_pressed()

        if close is not None and close.collidepoint(pos) and pressed1:
            loop = run = False
        for box, pokemon in pokemons:
            if box.collidepoint(pos) and pressed1:
                if encounter.player_pokemon.hp ==0:
                    player.change_main(pokemon)
                encounter.player_pokemon = pokemon
                loop = run = False
def UI_encounter(encounter):
    run  =False
    cont = None
    while (encounter.game_on()== 0 or encounter.game_on()==1) and not encounter.caught:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = True
                break
        pygame.time.delay(100)
        window.fill((80, 240, 62))
        pygame.draw.circle(window, (0, 102, 9), (120, 280), 80)
        pygame.draw.circle(window, (0, 102, 9), (400, 100), 80)
        sprites.draw(window, encounter.player_pokemon.sprite_num,120,280,4,90)
        sprites.draw(window, encounter.enemy.sprite_num,400,100,4,90)
        pygame.draw.rect(window, (25, 187, 212), (20, 380, 510, 300))
        font = pygame.font.Font('freesansbold.ttf', 18)
        font2 = pygame.font.Font('freesansbold.ttf', 14)
        tempx, tempy = 260,260
        temp = [encounter.player_pokemon, encounter.enemy]
        for i in temp:
            pygame.draw.rect(window, (245, 245, 245), (tempx, tempy, 200, 100))
            name_txt = font.render(i.name, True, (0,0,0), (245, 245, 245))
            lvl_txt = font.render("lvl {}".format(i.level), True, (0,0,0), (245, 245, 245))
            status_txt = font.render(i.status.name, True, (0, 0, 0), (245, 245, 245))
            pygame.draw.rect(window, (0,0,0), (tempx+5, tempy+50, 120,10), 3)
            amount = int(i.hp/i.maxhp*120)
            if amount >50:
                colour = 9, 148, 37
            elif amount >20:
                colour = 250, 136, 15
            else:
                colour = 255, 0, 0
            pygame.draw.rect(window, colour, (tempx + 5, tempy + 50, amount, 10))

            window.blit(name_txt, (tempx+10,tempy+10))
            window.blit(lvl_txt, (tempx + 200-50, tempy + 10))
            window.blit(status_txt, (tempx + 10, tempy + 70))
            hp = font2.render("{}/{}".format(i.hp, i.maxhp), True, (46, 46, 46), (255, 255, 255))
            window.blit(hp, (tempx+135, tempy+50))
            tempx, tempy = 60,40
        run_txt = font.render("Run", True, (25, 187, 212),(232, 65, 65))
        runrect = run_txt.get_rect()
        runrect.center= (270,650)
        run_btn = pygame.draw.rect(window, (232, 65, 65), (210, 630, 120, 40))
        window.blit(run_txt, runrect)

        bag_txt = font.render("Bag", True, (25, 187, 212), (232, 65, 65))
        bag_rect = bag_txt.get_rect()
        bag_rect.center = (100, 650)
        bag_btn = pygame.draw.rect(window, (232, 65, 65), (40, 630, 120, 40))
        window.blit(bag_txt, bag_rect)

        party_txt = font.render("Swap", True, (25, 187, 212), (232, 65, 65))
        party_rect = party_txt.get_rect()
        party_rect.center = (440, 650)
        party_btn = pygame.draw.rect(window, (232, 65, 65), (400, 630, 110, 40))
        window.blit(party_txt, party_rect)
        attacks = []
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
        for i in range(len(encounter.player_pokemon.attacks)):
            a = encounter.player_pokemon.attacks[i]
            x = 140 + (i % 2) * 250
            y = 500 + (i > 1) * 90
            if a.pp == 0:
                big_text = font.render(a.name, True, (0, 0, 0), (69,66,66))
                lil_text = font2.render("{}    {}/{}".format(a.type, a.pp, a.max_pp), True, (255, 0, 0), (69, 66, 66))
                pygame.draw.rect(window, (69, 66, 66), (x - 80, y - 30, 180, 60))
            else:
                big_text = font.render(a.name, True, (0, 0, 0), (255, 255, 255))
                lil_text = font2.render("{}    {}/{}".format(a.type, a.pp, a.max_pp), True, (0, 0, 0), (255, 255, 255))
                attacks.append((pygame.draw.rect(window, (255, 255, 255), (x - 80, y - 30, 180, 60)), a))
            text1Rect = big_text.get_rect()
            text2Rect = lil_text.get_rect()
            text1Rect.center = (x, y-5)
            text2Rect.center = (x, y+20)

            window.blit(big_text, text1Rect)
            window.blit(lil_text, text2Rect)
        pygame.display.update()
        pos = pygame.mouse.get_pos()
        pressed1, pressed2, pressed3 = pygame.mouse.get_pressed()
        if cont is not None:
            window.blit(font.render(cont, True, (46, 46, 46), (250, 207, 172)), (100, HEIGHT - 100))
            window.blit(font.render('Press enter to continue', True, (46, 46, 46), (250, 207, 172)),
                        (100, HEIGHT - 50))
            pygame.display.update()
        while cont is not None:
            keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print('yikes')
                    cont = None
            delay(200)
            print(cont)
            if keys[pygame.K_RETURN]:
                if cont =='{} was Caught!'.format(encounter.enemy.name):
                    encounter.player.add_pokemon(encounter.enemy)
                    encounter.caught = True
                else:
                    encounter.play(ITEMS['Poke ball'])
                cont = None
                break
        if run_btn.collidepoint(pos) and pressed1:
            run = True
            break
        if bag_btn.collidepoint(pos) and pressed1:
            i =ItemBagUI(encounter.player,1,None,encounter.enemy,150,150,screen_w-200,screen_h-200)
            i.info = True
            catch = i.draw()
            if catch is not None:
                if catch ==4:
                    cont = '{} was Caught!'.format(encounter.enemy.name)
                else:
                    cont = '{} broke out'.format(encounter.enemy.name)
        if party_btn.collidepoint(pos) and pressed1:
            swap_menu(encounter)

        for a in attacks:
            if a[0].collidepoint(pos) and pressed1:
                encounter.play(a[1])
    if encounter.game_on()==1 and not encounter.caught:
        encounter.xp_gain()
            
def print_screen(player):
    """
    Print all the tiles in around the player using the corners of player
    """
    tile = player.corners[0]
    left_edge = player.corners[0]
    right_edge = player.corners[1]
    direction = True
    x, y = (screen_w-screen_dimensions[0] * TILE_LENGTH) // 2, (screen_h- screen_dimensions[1] * TILE_LENGTH) // 2
    playerx, playery =0,0
    while (direction and tile != player.corners[3])or (not direction and tile != player.corners[2]):
        if tile is None:
            i = 0
        pygame.draw.rect(window,tile.colour,(x,y, TILE_LENGTH, TILE_LENGTH))
        if tile == player.curr_tile:
            #pygame.draw.circle(window,  (30, 213, 230), (x+TILE_LENGTH//2,y+TILE_LENGTH//2), TILE_LENGTH//2)
            playerx, playery = x,y
        if (direction and (tile.right is None or tile==right_edge)) or \
                (not direction and (tile.left is None or tile==left_edge)):
            left_edge = left_edge.down
            right_edge = right_edge.down
            y += TILE_LENGTH
            tile = tile.down
            direction = not direction
        elif direction and tile.right is not None:
            x += TILE_LENGTH
            tile = tile.right
        elif not direction and tile.left is not None:
            x -= TILE_LENGTH
            tile = tile.left
    pygame.draw.rect(window, tile.colour, (x, y, TILE_LENGTH, TILE_LENGTH))
    walk.draw(window, player.stance, playerx, playery, -1)
    pygame.draw.rect(window, (255,255,255),(screen_w,0,350,HEIGHT))
    pygame.draw.rect(window, (255, 255, 255), (0, screen_h, WIDTH, 200))
    i = 0
    rows = 0
    font = pygame.font.SysFont('georgia', 30)

    while i < len(player.dialogue):
        txt = font.render("{}".format(player.dialogue[i:i+30]), True, (46, 46, 46), (255, 255, 255))
        window.blit(txt, (20, screen_h+20+rows*20))
        i +=30
        rows +=1
    txt = font.render("Press enter to continue",  True, (46, 46, 46), (255, 255, 255))
    bag = font.render("BAG",  True, (46, 46, 46), (255, 255, 255))
    continueBtns[2] = window.blit(bag, (screen_w+50, 160))
    continueBtns[3] =  window.blit(font.render("Inventory",  True, (46, 46, 46), (255, 255, 255)), (screen_w+50, 250))
    continueBtns[4] = window.blit(font.render("Save and Quit", True, (46, 46, 46), (255, 255, 255)),
                                  (WIDTH - 250, 15))
    if player.stopped:
        continueBtns[0]=window.blit(txt,(20, HEIGHT-40))
        continueBtns[1]=window.blit(txt, (screen_w-400, HEIGHT - 40))
class ItemBagUI:
    def __init__(self, player,pageNum= 1, items= None, pokemon= None, startx= 0, starty= 0, width= screen_w, height= screen_h):
        self.player, self.page, self.x, self.y, self.width, self.height = player, pageNum, startx, starty, width, height
        if items is None:
            self.items = player.bag.items
        else:
            self.items = items
        if startx != 0:
            self.rows, self.collums , self.info= 3,2, False
        else:
            self.rows, self.collums, self.info = 4, 2, True
        self.pokemon, self.use = pokemon, None
    def draw(self):
        pygame.draw.rect(window, (46,46,46), (self.x, self.y, self.width, self.height))
        font = pygame.font.SysFont('georgia', 30)
        back = window.blit(font.render("Back", True,(46,46,46),(255,255,255)), (self.x+10,self.y+10))
        prevBox = nextBox= None
        items =[]
        x = (self.width-(self.collums+1)*100)//self.collums
        y = (self.height-180-self.rows*30)//self.rows
        #bagDict = list(player.bag.items.items())
        page = window.blit(font.render("Page {}/{}".format(self.page,max(math.ceil(len(self.items)/(self.rows*self.collums)), 1)), True,(46,46,46),(250, 207, 172)),
                           (self.x+ self.width-350, self.y+self.height-55))
        if max(math.ceil(len(self.items)/(self.rows*self.collums)), 1)!= self.page:
            nextBox= pygame.draw.rect(window,(250, 207, 172), (self.x+self.width-200,self.y+self.height-55, 170,50))
            window.blit(font.render("Next Page", True,(46,46,46),(250, 207, 172)), (self.x+self.width-180, self.y+self.height-55))
        if self.page != 1:
            prevBox = pygame.draw.rect(window,(250, 207, 172), (self.x+self.width-600,self.y+self.height-55, 220,50))
            window.blit(font.render("Previous Page", True, (46, 46, 46), (250, 207, 172)),
                        (self.x+self.width - 580,self.y+self.height - 55))
        l = list(self.items.items())
        for i in range(self.collums):
            for k in range(self.rows):
                if (self.page-1)*(self.rows*self.collums)+ i*self.rows +k <len(self.items):
                    item = l[(self.page-1)*(self.rows*self.collums)+i*self.rows + k]
                    item_box = pygame.draw.rect(window,(250, 207, 172),(self.x+(i+1)*100+i*x,self.y+30+(k+1)*30+k*150,x,y))
                    window.blit(font.render(str(item[0].name), True, (46, 46, 46), (250, 207, 172)),
                                ((i + 1) * 100 + i * x + 150+self.x,self.y+ 30 + (k + 1) * 30 + k * 150 + 10))
                    window.blit(font.render("Availability:{}".format(item[1]), True, (46, 46, 46), (250, 207, 172)),
                        ((i+1)*100+i*x+150+self.x,self.y+30+(k+1)*30+k*150+y-40))
                    items.append((item_box,item[0]))
        pygame.display.update()
        remake= stop = False
        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            keys = pygame.key.get_pressed()
            pos = pygame.mouse.get_pos()
            pressed1, pressed2, pressed3 = pygame.mouse.get_pressed()
            if nextBox is not None and nextBox.collidepoint(pos) and pressed1 and not remake:
                remake = True
                self.page +=1
            elif prevBox is not None and prevBox.collidepoint(pos) and pressed1 and not remake:
                remake = True
                self.page -= 1
            elif back.collidepoint(pos) and pressed1:
                stop = True
            elif (continueBtns[4] is not None and continueBtns[4].collidepoint(pos) and pressed1) or keys[pygame.K_q]:
                l.save(Asad)
                run = main_run= False
            elif (continueBtns[3] is not None and continueBtns[3].collidepoint(pos) and pressed1) or keys[pygame.K_i]:
                run= False
                i = InventoryUI(self.player)
                i.draw()
            elif remake and not pressed1:
                run = False
                self.draw()
            elif stop and not pressed1:
                run = False
            elif self.use is not None and self.use.collidepoint(pos) and pressed1:
                if isinstance(self.item, Ball):
                    return self.item.use(self.pokemon)
                pygame.draw.rect(window, (89, 235, 240),(150,200,640,400))
                window.blit(font.render("Who would you like to use the {} on?".format(self.item.name),True, (46, 46, 46), (89, 235, 240)),(160, 200))
                font2 = pygame.font.SysFont('georgia', 15)
                x = 160
                close =  window.blit(font.render("Cancel",True, (46, 46, 46), (89, 235, 240)),(640, 600))
                pokemons = []
                for i in range(len(self.player.bag.pokemons)):
                    sprites.draw(window,self.player.bag.pokemons[i].num, x,220,0,90)
                    window.blit(font2.render("HP:{}/{}".format(self.player.bag.pokemons[i].hp, self.player.bag.pokemons[i].maxhp),
                                    True, (46, 46, 46), (89, 235, 240)),(x, 220+90+10))
                    window.blit(font2.render(
                        "Status:"+str(self.player.bag.pokemons[i].status.name),
                        True, (46, 46, 46), (89, 235, 240)), (x, 220 + 90 + 30))
                    if usuable_item(self.player.bag.pokemons[i], self.item):
                        temp = window.blit(font.render("Use",True, (46, 46, 46), (89, 235, 240)), (x, 220 + 90 + 50))
                        pokemons.append((temp, self.player.bag.pokemons[i]))
                    x+=100
                pygame.display.update()
                loop = True
                while loop:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            loop = run = False
                    keys = pygame.key.get_pressed()
                    pos = pygame.mouse.get_pos()
                    pressed1, pressed2, pressed3 = pygame.mouse.get_pressed()
                    if (continueBtns[4] is not None and continueBtns[4].collidepoint(pos) and pressed1) or keys[
                        pygame.K_q]:
                        l.save(Asad)
                        loop = run = main_run = False
                    elif (continueBtns[3] is not None and continueBtns[3].collidepoint(pos) and pressed1) or keys[
                        pygame.K_i]:
                        loop= run = False
                        i = InventoryUI(self.player)
                        i.draw()
                    elif close.collidepoint(pos) and pressed1:
                        loop = run = False
                        self.draw()

                    for box, pokemon in pokemons:
                        if box.collidepoint(pos) and pressed1:
                            self.player.bag.consume_item(self.item, pokemon)
                            loop = run = False
                            self.draw()
            for item in items:
                if item[0].collidepoint(pos) and pressed1:
                    if self.info:
                        '''
                        self.player.dialogue = item[1].description
                        loop = True
                        if isinstance(item[1], Ball):
                            if item[0][0] == self.x + 100:
                                pygame.draw.rect(window, (252, 186, 3),
                                                 (self.x + 100 + x + 85, self.y + 60, 400, self.height - 180))
                                pygame.draw.rect(window, (252, 186, 3), (self.x + 100 + x, item[0][1] + 10, 85, 70))
                                window.blit(font.render("Can't use {} right now".format(item[1].name), True, (46, 46, 46), (252, 186, 3)),
                                        (self.x + 100 + x + 85 + 100, item[0][1] + 60))
                            else:
                                pygame.draw.rect(window, (252, 186, 3),
                                                 (self.x + x - 400 + 85, self.y + 60, 400, self.height - 180))
                                pygame.draw.rect(window, (252, 186, 3), (self.x + x + 85, item[0][1] + 10, 125, 70))
                            pygame.display.update()
                        while loop and self.player.bag.items[item[1]] >0 and isinstance(item[1], Healables):
                            if item[0][0] ==self.x+100:
                                pygame.draw.rect(window, (252, 186, 3),(self.x+100+x+85, self.y +60,400,self.height-180))
                                pygame.draw.rect(window, (252, 186, 3),(self.x+100+x, item[0][1]+10,85,70))
                                close = window.blit(font.render(" Close ", True, (46, 46, 46), (252, 186, 3)),
                                        (self.x+100+x+85+100, self.y +60+self.height-180))
                                gap,count = (self.height-180)//6,0
                                pokemon = []
                                for p in self.player.bag.pokemons:
                                    pokemon.append((sprites.draw(window, p.num,self.x+100+x+85,self.y +60+gap*count,0,gap),p))
                                    window.blit(font.render("HP:{}/{}".format(p.hp,p.maxhp), True, (46, 46, 46), (250, 207, 172)),
                                        (self.x+100+x+85+gap, self.y +60+gap*count+15))
                                    window.blit(font.render("Status:{}".format(p.status.name), True, (46, 46, 46),(250, 207, 172)),
                                        (self.x + 100 + x + 85 + gap, self.y +60+ gap * count+65))
                                    count +=1
                            else:
                                pygame.draw.rect(window, (252, 186, 3),(self.x+x-400+ 85, self.y + 60, 400, self.height - 180))
                                pygame.draw.rect(window, (252, 186, 3), (self.x+x+85, item[0][1] + 10, 125, 70))
                                close = window.blit(font.render(" Close ", True, (46, 46, 46), (252, 186, 3)),
                                                    (self.x+x-400+ 85+100, self.y + 60 + self.height - 180))
                                gap, count = (self.height - 180) // 6, 0
                                pokemon = []
                                for p in self.player.bag.pokemons:
                                    pokemon.append(
                                        (sprites.draw(window, p.num, self.x+x-400+85, self.y + 60 + gap * count, 0,gap),p))
                                    window.blit(
                                        font.render("HP:{}/{}".format(p.hp, p.maxhp), True, (46, 46, 46), (250, 207, 172)),
                                        (self.x+x-400+85 + gap, self.y + 60 + gap * count + 15))
                                    window.blit(
                                        font.render("Status:{}".format(p.status.name), True, (46, 46, 46), (250, 207, 172)),
                                        (self.x+x-400+85+ gap, self.y + 60 + gap * count + 65))
                                    count += 1
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    run = False
                            keys = pygame.key.get_pressed()
                            pos = pygame.mouse.get_pos()
                            pressed1, pressed2, pressed3 = pygame.mouse.get_pressed()
                            if close is not None and close.collidepoint(pos) and pressed1:
                                loop = run=False
                                self.draw()
                            for box, p in pokemon:
                                if box is not None and box.collidepoint(pos) and pressed1:
                                    item[1].use(p)
                                    self.items[item[1]] -=1
                                    loop =run = False
                                    self.draw()'''
                        self.use , self.item = draw_item_info(self.player, item[1]), item[1]
                        if self.pokemon is not None and self.pokemon not in self.player.bag.pokemons:
                            self.use = window.blit(font.render("Use on the enemy", True, (46, 46, 46), (73, 122, 201)), (screen_w-200,screen_h+40))

                        pygame.display.update()
                    else:
                        self.player.bag.consume_item(item[1], self.pokemon)
                        run = False

def usuable_item(pokemon, item):
    temp = copy.copy(pokemon)
    item.use(temp)
    if pokemon.hp == temp.hp and pokemon.status.name == temp.status.name:
        return False
    return True

fullscreen = False
continueBtns = [None,None, None, None, None]
class InventoryUI():
    def __init__(self, player, page=1):
        self.player, self.page = player, page
        self.pokemon = self.move = self.item = self.prestege =self.swap =self.cancel= None
        self.store, self.attacks = None, []
    def draw(self):
        pygame.draw.rect(window, (217, 179, 98), (screen_w - 350, 0, 350, screen_h))
        pygame.draw.rect(window, (73, 122, 201), (0, 0, screen_w-350, screen_h))
        font = pygame.font.SysFont('georgia', 30)
        # Blue 73, 122, 201
        window.blit(font.render("Party Pokemon", True, (46, 46, 46), (217, 179, 98)), (screen_w-350 + 70, 10))
        window.blit(font.render("Inventory Pokemon", True, (46, 46, 46), (73, 122, 201)), (400, 10))
        back = window.blit(font.render("Back", True, (46, 46, 46), (247, 10, 10)), (10, 10))
        window.blit(font.render("Page {}/{}".format(self.page, max(math.ceil(len(self.player.inventory) / 60),1)),
                                True, (0, 0, 0), (73, 122, 201)), (screen_w- 700 , screen_h - 70))
        prevBox = nextBox = None
        if max(math.ceil(len(self.player.inventory) / 60),1) != self.page:
            nextBox = pygame.draw.rect(window, (247, 10, 10), (screen_w - 350 - 200, screen_h - 80, 170, 50))
            window.blit(font.render("Next Page", True, (0, 0, 0), (247, 10, 10)),
                        (screen_w- 350 - 180, screen_h - 70))
        if self.page != 1:
            prevBox = pygame.draw.rect(window, (247, 10, 10), (screen_w - 350 - 600, screen_h - 80, 220, 50))
            window.blit(font.render("Previous Page", True, (0, 0, 0), (247, 10, 10)),
                        (screen_w-350 - 580, screen_h - 70))
        party = []
        inventory = []
        x = -50
        for i in range(len(self.player.bag.pokemons)):
            pokemon = sprites.draw(window, self.player.bag.pokemons[i].sprite_num, screen_w-350 + x + 60,
                                   50 + i * ((screen_h-100 + 50) // 6), 0, 135)
            party.append((pokemon, self.player.bag.pokemons[i]))
            x = 0
        for i in range(6):
            for k in range(10):
                if i * 10 + k < len(self.player.inventory):
                    pokemon = sprites.draw(window, self.player.inventory[i * 10 + k].sprite_num, 80 + k * (110),
                                           100 + (120) * i, 0, 105)
                    inventory.append((pokemon, self.player.inventory[i * 10 + k]))

        pygame.display.update()
        run, remake= True, False
        current = [None, None, None]
        selected = [None, None, None]
        if self.pokemon is not None:
            self.item, self.swap, self.prestege, self.move, self.attacks = draw_pokemon_info(self.player, self.pokemon[0])
            print(self.pokemon, self.pokemon[0].name)
            pygame.draw.circle(window, (247, 10, 10), self.pokemon[1].center, self.pokemon[1][2] // 2 + 3, 2)
            selected = self.pokemon
            self.pokemon = None
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            pos = pygame.mouse.get_pos()
            pressed1, pressed2, pressed3 = pygame.mouse.get_pressed()
            for attack in self.attacks:
                if attack[0].collidepoint(pos) and pressed1:
                    pygame.draw.rect(window, (217, 179, 98), (200 + 530, screen_h + 45, 300, 140))
                    attacktxt(attack[1].name, 200 + 530, screen_h+45)
                    attacktxt("Damage:{}".format(attack[1].damage), 200 + 530, screen_h+ 75)
                    attacktxt("PP:{}/{}".format(attack[1].pp, attack[1].max_pp), 200 + 530+150, screen_h + 75)
                    attacktxt("Type:{}".format(attack[1].type), 200 + 530, screen_h + 95)
                    attacktxt("Accuracy:{}".format(attack[1].accuracy), 200 + 530+150, screen_h+ 95)
                    attacktxt("Speed:{}".format(attack[1].speed), 200 + 530, screen_h+ 115)
                    attacktxt("Self Damage:{}%".format(int(attack[1].self_damage*100)), 200 + 530+150, screen_h + 115)
                    if attack[1].status[0] != '':
                        attacktxt("Has a {}% chance of inflicting {} on victim".format(attack[1].status[1], attack[1].status[0]), 200 + 530, screen_h + 145)
            if back.collidepoint(pos) and pressed1:
                run = False
            elif remake and not pressed1:
                run = False
                self.draw()
            elif (continueBtns[2] is not None and continueBtns[2].collidepoint(pos) and pressed1) or keys[pygame.K_b]:
                run = False
                i = ItemBagUI(Asad)
                i.draw()
            elif (continueBtns[4] is not None and continueBtns[4].collidepoint(pos) and pressed1) or keys[pygame.K_q]:
                l.save(Asad)
                run = main_run= False
            elif nextBox is not None and nextBox.collidepoint(pos) and pressed1 and not remake:
                remake = True
                self.page +=1
            elif prevBox is not None and prevBox.collidepoint(pos) and pressed1 and not remake:
                remake = True
                self.page -= 1
            elif self.swap is not None and self.swap.collidepoint(pos) and pressed1:
                pygame.draw.rect(window, (217, 179, 98), self.swap)
                self.cancel = window.blit(font.render("Cancel swap", True, (46, 46, 46), (247, 10, 10)),
                                          (screen_w - 300, screen_h + 15))
                self.swap, self.store = None, self.swap
            elif self.cancel is not None and self.cancel.collidepoint(pos) and pressed1:
                pygame.draw.rect(window, (217, 179, 98), self.cancel)
                self.swap = window.blit(font.render("Swap {}".format(selected[0].name), True, (46, 46, 46), (247, 10, 10)),
                                          (screen_w - 300, screen_h + 15))
                self.cancel, self.store = None, None
            elif self.prestege is not None and self.prestege.collidepoint(pos) and pressed1:
                pygame.draw.rect(window, (255, 250, 145), (150, 150, 900, 650))
                bigFont = pygame.font.SysFont('georgia', 50)
                window.blit(bigFont.render("Prestege Menu", True, (46, 46, 46), (255, 250, 145)), (450, 150))
                window.blit(
                    font.render("Presteging a pokemon can only be done by excpetional trainers.", True, (46, 46, 46),
                                (255, 250, 145)), (180, 230))
                window.blit(font.render("It takes patience, skill, trust and love from both the trainer and ", True,
                                        (46, 46, 46), (255, 250, 145)), (180, 270))
                window.blit(font.render("pokemon. Once a a trainer and pokemon reach this level, the ", True,
                                        (46, 46, 46), (255, 250, 145)), (180, 310))
                window.blit(font.render("pokemon goes through changes at the molecular level. Allowing", True,
                                        (46, 46, 46), (255, 250, 145)), (180, 350))
                window.blit(font.render("them to change their apperance to their shiny variant! However,", True,
                                        (46, 46, 46), (255, 250, 145)), (180, 390))
                window.blit(font.render("this metamorphus is extremely taxing and will cause your", True,
                                        (46, 46, 46), (255, 250, 145)), (180, 430))
                window.blit(font.render("pokemon's level and stats to reset to level 1. This shouldn't ", True,
                                        (46, 46, 46), (255, 250, 145)), (180, 470))
                window.blit(font.render("be an issue for an excellent trainer as yourself though.", True,
                                        (46, 46, 46), (255, 250, 145)), (180, 510))
                if selected[0].level == 15:
                    window.blit(font.render("You and {} have reached prestege rank!".format(selected[0].name), True,
                                            (46, 46, 46), (255, 250, 145)), (180, 600))
                    window.blit(
                        font.render("Do you want to prestege {}?(there's no turning back)".format(selected[0].name), True,
                                    (46, 46, 46), (255, 250, 145)), (180, 640))
                    yes = window.blit(font.render("  YES  ", True, (46, 46, 46), (38, 212, 61)), (400, 700))
                    no = window.blit(font.render("  NO  ", True, (46, 46, 46), (247, 10, 10)), (650, 700))
                else:
                    window.blit(font.render("You and {} haven't reached prestege rank yet.".format(selected[0].name), True,
                                            (46, 46, 46), (255, 250, 145)), (180, 600))
                    no = window.blit(font.render("  Close  ", True, (46, 46, 46), (247, 10, 10)), (530, 680))
                loop = True
                while loop:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            run = False
                    pos = pygame.mouse.get_pos()
                    pressed1, pressed2, pressed3 = pygame.mouse.get_pressed()
                    if back.collidepoint(pos) and pressed1:
                        run = loop = False
                    elif no.collidepoint(pos) and pressed1:
                        self.pokemon = selected
                        loop = False
                        remake = True

                    pygame.display.update()

            elif self.move is not None and self.move.collidepoint(pos) and pressed1:
                if selected[0] in self.player.inventory:
                    self.player.inventory.remove(selected[0])
                    self.player.bag.add_pokemon(selected[0])
                elif selected[0] in self.player.bag.pokemons:
                    self.player.bag.pokemons.remove(selected[0])
                    self.player.inventory.append(selected[0])
                remake= True
                self.draw()
            elif self.item is not None and self.item.collidepoint(pos) and pressed1:
                items = []
                for i, k in self.player.bag.items.items():
                    if isinstance(i, Healables):
                        items.append((i, k))
                i = ItemBagUI(self.player, 1, None, selected[0], 200, 200, screen_w - 350 - 50, screen_h - 250)
                i.draw()
                run = False
                self.draw()
            else:
                temp = selecting_pokemon(party, inventory)
                if temp[0] == selected[0] and temp[0] is not None:
                    pass
                elif temp[3]:
                    if self.store is not None:
                        if selected[0] in self.player.inventory:
                            list1, index1 = self.player.inventory, self.player.inventory.index(selected[0])
                        else:
                            list1, index1 = self.player.bag.pokemons, self.player.bag.pokemons.index(selected[0])
                        if temp[0] in self.player.inventory:
                            list2, index2 = self.player.inventory, self.player.inventory.index(temp[0])
                        else:
                            list2, index2 = self.player.bag.pokemons, self.player.bag.pokemons.index(temp[0])
                        list1[index1], list2[index2] = list2[index2] , list1[index1]
                        if selected[0] is self.player.main:
                            self.player.change_main(temp[0])
                        elif temp[0] is self.player.main:
                            self.player.change_main(selected[0])
                        self.store = None
                        self.pokemon =temp[0], temp[1], temp[2]
                        run = False
                        self.draw()
                    else:
                        if selected[0] is not None:
                            pygame.draw.circle(window, selected[2], selected[1].center, selected[1][2] // 2 + 3, 2)
                        pygame.draw.circle(window, (247, 10, 10), temp[1].center, temp[1][2] // 2 + 3, 2)
                        selected = current = temp[0], temp[1], temp[2]
                        self.item, self.swap, self.prestege, self.move ,self.attacks= draw_pokemon_info(self.player, temp[0])
                else:
                    if current[0] is not None and current[0] is not selected[0]:
                        pygame.draw.circle(window, current[2], current[1].center, current[1][2] // 2 + 3, 2)
                        curent = None, None, None
                    if temp[0] is not None:
                        pygame.draw.circle(window, (61, 224, 69), temp[1].center, temp[1][2] // 2 + 3, 2)
                        current = temp[0], temp[1], temp[2]
                pygame.display.update()


def selecting_pokemon(party, inventory):
    #print(selected[0])
    pos = pygame.mouse.get_pos()
    pressed1, pressed2, pressed3 = pygame.mouse.get_pressed()
    for box, pokemon in party:
        if box.collidepoint(pos) and pressed1:
            return pokemon, box, (217, 179, 98), True
        elif box.collidepoint(pos):
            return pokemon, box, (217, 179, 98), False
    for box, pokemon in inventory:
        if box.collidepoint(pos) and pressed1:
            return pokemon, box, (73, 122, 201), True
        elif box.collidepoint(pos):
            return pokemon, box, (73, 122, 201), False
    return None, None, None, False
def draw_item_info(player, item):
    pygame.draw.rect(window, (217, 179, 98), (0, screen_h, WIDTH, 200))
    item.sprite_num = 0
    sprites.draw(window, item.sprite_num, 0, screen_h, 0, 180)
    font = pygame.font.SysFont('georgia', 30)
    window.blit(font.render(item.name, True, (46, 46, 46), (217, 179, 98)), (15, HEIGHT - 35))
    window.blit(font.render('Use:', True, (46, 46, 46), (217, 179, 98)), (215, screen_h+10))

    if isinstance(item, Ball):
        window.blit(font.render(' Thrown at wild pokemon to catch them', True, (46, 46, 46), (217, 179, 98)), (285, screen_h+10))
        window.blit(font.render('Effectiveness:{}'.format(item.description), True, (46, 46, 46), (217, 179, 98)), (215, screen_h + 50))
    else:
        window.blit(font.render(' Given to party pokemon to heal', True, (46, 46, 46), (217, 179, 98)),
                    (285, screen_h + 10))
        txt = ''
        if item.restore:
            txt = 'Heal pokemon to full hp'
        else:
            txt = str(item.amount)
        window.blit(font.render('HP Healed:{}'.format(txt), True, (46, 46, 46), (217, 179, 98)),
                    (215, screen_h + 50))
        txt = 'No cure effect'
        if item.all_cure:
            txt='Cures all statuses'
        elif item.cure is not None:
            txt = 'Cures {}'.format(item.cure.name)
        window.blit(font.render('Effect:{}'.format(txt), True, (46, 46, 46), (217, 179, 98)),
                    (215, screen_h + 90))
        return window.blit(font.render("Use {} on a pokemon".format(item.name), True, (46, 46, 46), (247, 10, 10)),
                    (300 + 740, screen_h + 25))

def draw_pokemon_info(player, pokemon):
    pygame.draw.rect(window, (217, 179, 98), (0, screen_h, WIDTH, 200))
    sprites.draw(window,pokemon.sprite_num,0,screen_h,0,180)
    font = pygame.font.SysFont('georgia', 30)
    window.blit(font.render(pokemon.name, True, (46, 46, 46), (217, 179, 98)), (15, HEIGHT-35) )
    window.blit(font.render("Level:{}".format(pokemon.level), True, (46, 46, 46), (217, 179, 98)), (200, screen_h+5))
    window.blit(font.render("Type:{}".format(pokemon.type), True, (46, 46, 46), (217, 179, 98)),(200, screen_h + 55))
    if pokemon.shiny:
        txt = "Shiny:Yes!"
    else:
        txt = "Shiny:No"
    window.blit(font.render(txt, True, (46, 46, 46), (217, 179, 98)), (200, screen_h+105))
    window.blit(font.render("Status:{}".format(pokemon.status.name if pokemon.status.name != "" else "Normal" ),
                            True, (46, 46, 46), (217, 179, 98)), (200, screen_h+155))
    window.blit(font.render("HP:{}/{}".format(pokemon.hp, pokemon.maxhp), True, (46, 46, 46), (217, 179, 98)),
                (200+220, screen_h + 5))
    window.blit(font.render("XP to level up:{}".format(pokemon.next_level-pokemon.xp), True, (46, 46, 46), (217, 179, 98)),
                (200 + 220, screen_h+ 55))
    window.blit(font.render("Attacks:", True, (46, 46, 46), (217, 179, 98)),
                (200 + 530, screen_h + 5))
    pygame.draw.rect(window,(217, 179, 98), (200 + 530, screen_h + 55,250,140))
    pygame.draw.rect(window, (217, 179, 98), (200 + 530, screen_h + 45, 300, 140))
    attacktxt("Click an attack to get more info on it")
    item = window.blit(font.render("Use an Item",True, (46, 46, 46), (247, 10, 10)), (420, screen_h+125))
    swap = window.blit(font.render("Swap {}".format(pokemon.name), True, (46, 46, 46), (247, 10, 10)), (screen_w-300, screen_h+15))
    prestege = window.blit(font.render("Prestege {}".format(pokemon.name), True, (46, 46, 46), (247, 10, 10)), (screen_w-300, screen_h+65))
    move = None
    if pokemon in player.inventory:
        if len(player.bag.pokemons) != 6:
            move = window.blit(font.render("Put In Party",True, (46, 46, 46), (247, 10, 10)),
                               (screen_w- 300, screen_h+ 125))
    elif pokemon is not player.main:
        move = window.blit(font.render("Put In Inventory", True, (46, 46, 46), (247, 10, 10)),
                           (screen_w - 300, screen_h+ 125))
    attacks = []
    for i in range(len(pokemon.attacks)):
        temp = window.blit(font.render(pokemon.attacks[i].name,True, (46, 46, 46), (247, 10, 10)), (300+740, screen_h+5+i*45))
        attacks.append((temp, pokemon.attacks[i]))
    pygame.display.update()
    return item, swap, prestege, move, attacks
def attacktxt(text, x= 200 + 530, y = HEIGHT - 200 + 45):
    attackfont = pygame.font.SysFont('georgia', 17)
    words = text.split(" ")
    w = window.blit(attackfont.render(words[0], True, (46, 46, 46), (217, 179, 98)),
                (x, y))
    for word in words[1:]:
        if w[2] + x >200 + 530+250:
            x, y = 200 + 530, y +20
        else:
            x, y = x+ w[2] +3,y
        w = window.blit(attackfont.render(word, True, (46, 46, 46), (217, 179, 98)),
                        (x, y))
def print_text(text,x=10,y=screen_h+10,width=screen_w,height=HEIGHT-10):
    font = pygame.font.SysFont('georgia', 25)
    words = text.split(" ")
    w = window.blit(font.render(words[0], True, (46, 46, 46), (255, 255, 255)),
                    (x, y))
    for word in words[1:]:
        if w[2] + x > width:
            x, y = 10, y + 20
        else:
            x, y = x + w[2] + 3, y
        w = window.blit(font.render(word, True, (46, 46, 46), (255, 255, 255)),
                        (x, y))
def beggining(player):
    return player.bag.pokemons == []
class Event:
    def __init__(self, condition, opening_text, end_text, encounter):
        self.condition, self.opening_text, self.end_text, self.encounter = condition, opening_text, end_text, encounter
    def check(self, player):
        if self.self.condition(player):
            pass
def command(player, text):
    txt = text.split('.')
    if txt[0] == 'spawn':
        if len(txt) ==3 and txt[1] in POKEMON.keys():
            if txt[2].isnumeric() and 1<=int(txt[2])<=100:
                info = POKEMON[txt[1]]
                p = Pokemon(txt[1],info[4],int(txt[2]))
                e = PVE_Encounter(player,player.curr_location)
                e.enemy = p
                return True, e
        elif len(txt) ==4 and txt[1] in POKEMON.keys():
            if txt[2].isnumeric() and 1<=int(txt[2])<=100 and txt[3] == 'shiny':
                info = POKEMON[txt[1]]
                p = Pokemon(txt[1],info[4],int(txt[2]))
                p.shiny = True
                e = PVE_Encounter(player,player.curr_location)
                e.enemy = p
                return True, e
    elif txt[0] == 'give':
        if len(txt) ==2 and txt[1] in ITEMS:
            player.bag.add_item(ITEMS[txt[1]])
            return True, None
        elif len(txt) ==3 and txt[1] in ITEMS and txt[2].isnumeric():
            if int(txt[2]) > 0:
                for i in range(int(txt[2])):
                    player.bag.add_item(ITEMS[txt[1]])
                return True, None
    return False, None


main_run = True
walk = SpriteSheet('PlayerSprite.png',4,4)
sprites = SpriteSheet('spritesheet.png',1,4)
if __name__ == '__main__':
    import doctest
    doctest.testmod()
    l = LoadSave('Save.txt')
    Asad = Player(None, None, None)
    l.loadPlayer(Asad)
    #l2 = Location([('charizard',3,100, 1, 100)], "test_A.txt")
    #l = Location([('charizard',3,100, 1, 0)], 'test_level.txt')

    #pygame.display.set_mode((WIDTH,HEIGHT),pygame.RESIZABLE)
    window.fill((46, 46, 46))

    #print_text('Welcome to the pokemon world! Please enter your name')

   # s = POKEMON['pikachu']
   # p = Pokemon('pikachu', 0,5)
   # p.set_hp(40)
    #Asad.add_pokemon(p)

    #for i in range(26):
     #   Asad.add_pokemon(Pokemon('charizard', 3, 5))
    #Asad.inventory[1].shiny = True
    #print(l2.height, l2.width)
    #print_tile(l.start, True, (WIDTH -l.width*40)//2,(HEIGHT-l.height*40)//2)
    #print_player(Asad)
    screen_dimensions = min((screen_w) // TILE_LENGTH, Asad.curr_location.width), min((screen_h) // TILE_LENGTH,
                                                                                           Asad.curr_location.height)
    Asad.make_corners()
    for i in range(10):
        ball = ITEMS['Full Restore']
        Asad.bag.add_item(ball)
    #print_screen(Asad)
    #i = InventoryUI(Asad)
    #i.draw()
    pygame.display.update()
    encounter = None

    font = pygame.font.SysFont('georgia', 20)
    #e = PVE_Encounter(Asad, Asad.curr_location)
    #print(e.catch())
    #UI_encounter(PVE_Encounter(Asad, Asad.curr_location))
    curr = Asad.curr_location
    left = right= up= down = False
    pressed = cheat = False
    count = 0
    text = ''
    #i = ItemBagUI(Asad)
    #i.draw()
    time = 200
    while main_run:
        pygame.time.delay(time)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                main_run = False
        keys = pygame.key.get_pressed()
        pos = pygame.mouse.get_pos()
        pressed1, pressed2, pressed3 = pygame.mouse.get_pressed()
        window.fill((0, 0, 0))
        print_screen(Asad)
        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
            time = 100
        else:
            time = 200
        if cheat:
            char = None
            pygame.draw.rect(window, (104, 107, 105), (0, screen_h - 100, screen_w, 100))
            window.blit(font.render("Command Prompt", True, (46, 46, 46), (104, 107, 105)), (10, screen_h - 100))
            window.blit(font.render("Press Ctrl to close", True, (46, 46, 46), (104, 107, 105)), (300, screen_h - 100))

            while cheat:
                pygame.time.delay(10)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        cheat = main_run = False
                if not pressed and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    cheat = not cheat
                    pressed = True
                if event.type == pygame.KEYUP:
                    pressed = False
                pygame.draw.rect(window, (104, 107, 105),(10,screen_h-70,screen_w-10,30))
                window.blit(font.render(text, True, (46, 46, 46), (104, 107, 105)), (10, screen_h - 70))
                if (continueBtns[4] is not None and continueBtns[4].collidepoint(pos) and pressed1):
                    l.save(Asad)
                    cheat = False
                    main_run = False
                elif event.type == pygame.KEYDOWN:
                    char = event
                    pressed = True
                if event.type == pygame.KEYUP and not pressed and char is not None:
                    if char.key == pygame.K_RETURN:
                        worked, encounter = command(Asad, text)
                        if worked:
                            colour = (20, 245, 12)
                        else:
                            colour = (240, 22, 40)
                        pygame.draw.rect(window ,(104, 107, 105), (0, screen_h - 50, screen_w, 50))
                        window.blit(font.render(text, True, colour, (104, 107, 105)),
                                    (10, screen_h - 30))
                        text = ''
                    elif char.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += char.unicode
                    char = None
                pygame.display.update()
        elif Asad.stopped:
            if keys[pygame.K_RETURN] or ((continueBtns[1].collidepoint(pos) or continueBtns[0].collidepoint(pos))
                                         and pressed1) :
                Asad.stopped = False
                Asad.dialogue = ''
        elif (continueBtns[2] is not None and continueBtns[2].collidepoint(pos) and pressed1) or keys[pygame.K_b]:
            i =ItemBagUI(Asad)
            i.draw()
        elif (continueBtns[3] is not None and continueBtns[3].collidepoint(pos) and pressed1) or keys[pygame.K_i]:
            i =InventoryUI(Asad)
            i.draw()
        elif (continueBtns[4] is not None and continueBtns[4].collidepoint(pos) and pressed1) or keys[pygame.K_q]:
            l.save(Asad)
            main_run = False
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            left = True
            Asad.stance = 2 * (count % 2) + 5
            count += 1
            if Asad.corners[0].left is not None:
                #if Asad.corners[1].x- Asad.curr_tile.x== Asad.curr_tile.x -Asad.corners[0].x:
                for corner in range(len(Asad.corners)):
                     Asad.corners[corner] = Asad.corners[corner].left

            encounter = Asad.curr_tile.left.walk_to(Asad)
        elif keys[pygame.K_d]or keys[pygame.K_RIGHT]:
            right = True
            Asad.stance = 2 * (count % 2) + 9
            count += 1
            if Asad.corners[1].right is not None:
                #if Asad.corners[1].x- Asad.curr_tile.x== Asad.curr_tile.x -Asad.corners[0].x:
                for corner in range(len(Asad.corners)):
                    Asad.corners[corner] = Asad.corners[corner].right

            encounter = Asad.curr_tile.right.walk_to(Asad)
        elif keys[pygame.K_w]or keys[pygame.K_UP]:
            up = True
            Asad.stance = 2 * (count % 2) + 13
            count += 1
            if Asad.corners[0].up is not None:
                #if Asad.corners[3].y- Asad.curr_tile.y== Asad.curr_tile.y -Asad.corners[0].y:
                for corner in range(len(Asad.corners)):
                    Asad.corners[corner] = Asad.corners[corner].up

            encounter = Asad.curr_tile.up.walk_to(Asad)
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            down = True
            Asad.stance = 2 * (count % 2) + 1
            count += 1
            if Asad.corners[2].down is not None:
                #if Asad.curr_tile.y - Asad.corners[0].y == Asad.corners[3].y - Asad.curr_tile.y:
                for corner in range(len(Asad.corners)):
                    Asad.corners[corner] = Asad.corners[corner].down

            encounter = Asad.curr_tile.down.walk_to(Asad)
        else:
            count = 0
            if left:
                Asad.stance =4
            elif right:
                Asad.stance = 8
            elif up:
                Asad.stance = 12
            elif down:
                Asad.stance = 0
            up = down= right =left = False
        if curr != Asad.curr_location:
            curr = Asad.curr_location
            screen_dimensions = min((WIDTH -350)// TILE_LENGTH, Asad.curr_location.width), min((HEIGHT -200)// TILE_LENGTH,
                                                                                         Asad.curr_location.height)
            Asad.make_corners()
            i = 1

        if event.type == pygame.KEYUP:
            pressed = False
        if not pressed and pygame.key.get_mods() & pygame.KMOD_CTRL:
            cheat = not cheat
            pressed = True
        #item_bag_UI(Asad)
        #aaaaaaprint_tile(Asad.curr_location.start, True, (WIDTH -Asad.curr_location.width*40)//2,(HEIGHT-Asad.curr_location.height*40)//2)
        #pygame.draw.circle(window, (30, 213, 230),
        #                   (Asad.curr_tile.x +20+ (WIDTH -Asad.curr_location.width*40)//2, Asad.curr_tile.y + 20+(HEIGHT-Asad.curr_location.height*40)//2), 20)
        pygame.display.update()
        if encounter is not None and Asad.main.hp>0:
            UI_encounter(encounter)
            encounter = None
            #pygame.display.set_mode((curr.width * TILE_LENGTH, curr.height * TILE_LENGTH))
    pygame.quit()
