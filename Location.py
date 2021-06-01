TILE_LENGTH= 40
from Items import ITEMS
import random, pygame
from Encounter import PVE_Encounter, PvP_Battle
from Pokemon import Pokemon, Status, Attack, ATTACKS, makeAttack
from Player import Player
from UI import UI_encounter
class Location:
    '''
    pokmeon:all possible pokemon that can be spawned and what their level can be
    location_id: uniue identifier number which will help correspond to
    where the end of each level ends
    '''

    def __init__(self, openfile, player, trainers):
        self.pokemon = []
        self.trainers = trainers
        self.player = player
        self.spawn_point = None
        self.create_level(openfile)
    def pokemon_list(self, f):
        text = f.readline()
        while text != "EOPL\n":
            t = text.split(",")
            t[-1] = t[-1][:-1]
            for i in range(len(t)):
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
            elif info[1] =='T':
                self.tileDict[info[0]]=(info[1],info[2], info[3])
            else:
                self.tileDict[info[0]]= (info[1], info[2])
            txt = f.readline()

    def create_level(self, f):
        self.pokemon_list(f)
        self.create_tile_dict(f)
        text = f.readline()
        self.id = text.split(',')[2][:-1]
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
            self.player.curr_location = self
            self.player.curr_tile = t
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
        elif self.tileDict[text[i]][0] == 'R':
            return Restore_Tile(self.tileDict[text[i]][1]), i+1
        elif self.tileDict[text[i]][0] == 'I':
            t = Item_Tile(None, None, self.get_tile(self.tileDict[text[i]][2], 0, [])[0])
            if self.tileDict[text[i]][1] in item_tiles:
                item_tiles[self.tileDict[text[i]][1]].append(t)
            else:
                item_tiles[self.tileDict[text[i]][1]] = [t]
            return t, i + 1
        elif self.tileDict[text[i]][0] == 'T':
            self.trainers[self.tileDict[text[i]][1]].curr_location= self
            floor = self.get_tile(self.tileDict[text[i]][2],0,item_tiles)[0]
            print(floor.print())
            t = Other_Player_Tile(self.tileDict[text[i]][1],self.trainers[self.tileDict[text[i]][1]], floor)
            self.trainers[self.tileDict[text[i]][1]].curr_tile = t
            return t, i+1
        else:
            t = Item_Tile(0,0, None,None)
            if text[i] in item_tiles:
                item_tiles[text[i]].append(t)
            else:
                item_tiles[text[i]]=[t]
            return t, i+1
    def print_location(self, player):
        d = {}
        tiles = ''
        available = '0123456789-=!@#$%^&*()_+[]{;:}<.>/?`~|'
        curr = 0
        left = self.start
        tile = self.start
        while tile is not None:
            if (isinstance(tile, Item_Tile) and not tile.got) or (isinstance(tile,Other_Player_Tile) and not tile.beat):
                info = tile.print()
                if info.split('/')[1] in d:
                    char = d[info.split('/')[1]]
                else:
                    d[info.split('/')[1]] = available[curr]
                    char = available[curr]
                    curr += 1
                info = info.split('/')[0]+','+char
            elif isinstance(tile,Other_Player_Tile):
                info = tile.floor.print()
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
        for pokemon in self.pokemon:
            s += '{},{},{},{},{}\n'.format(pokemon[0],pokemon[1],pokemon[2],pokemon[3],pokemon[4])
        s += "EOPL\n"
        for key, item in d.items():
            s += "{},{}".format(item, key)+'\n'
        i = 'EOD\n{},{},{}\n'.format(self.height, self.width, self.id)
        return "SOL\n"+s+i+tiles


class Tile:
    """
    Basic tile class. Tiles are what the player walks around on in the screen
    """
    def __init__(self, spriteNum = None, height = TILE_LENGTH, width= TILE_LENGTH):
        self.height, self.width, self.num = height, width, spriteNum
        self.left = self.right= self.up=self.down=self.colour= None
    def walk_to(self, player):
        raise NotImplementedError
    def move_player(self, player):
        player.curr_tile = self
    def draw(self,x,y,window,walk=None):
        pygame.draw.rect(window, self.colour, (x, y, TILE_LENGTH, TILE_LENGTH))
class Restore_Tile(Tile):
    def __init__(self, num, colour=None):
        Tile.__init__(self,num)
        if colour is None:
            self.colour = 247, 94, 232
        else:
            self.colour = colour
    def walk_to(self, player):
        Tile.move_player(self, player)
        player.heal()
        player.dialogue = "Your party has been healed"
        player.stance -=1
        player.stopped = True
    def print(self):
        return 'R,{}'.format(self.num)
class Other_Player_Tile(Tile):
    def __init__(self,num, player,tile,colour = None):
        Tile.__init__(self,num)
        self.beat = False
        self.floor = tile
        if colour is None:
            self.colour = 46,46,46
        else:
            self.colour = colour
        self.other_player = player
    def walk_to(self, player):
        return PvP_Battle(player, self.other_player, self.other_player.diff)
    def print(self):
        return "T,{}/{}".format(self.other_player.name, self.floor.print())
    def draw(self, x, y, window,walk):
        self.floor.draw(x,y,window, walk)
        walk.draw(window, self.other_player.stance, x,y, -1)
class Boundary_Tile(Tile):
    """
    Tiles that cannot be steped on
    """
    def __init__(self,num,colour = None):
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
            Tile.move_player(self, player)
            player.bag.add_item(self.item)
            player.dialogue = "You found a {}".format(self.item.name)
            player.stopped = True
            player.stance-=1
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
        self.trainers= {}
        i =0
        txt = f.readline().split(',')
        while txt[0] != 'EOPLAYERS\n': 
            playerName, playerCash,playerStance, pdiff = txt[0], int(txt[1]),int(txt[2]), int(txt[3][:-1])
            txt = f.readline()
            party= []
            if "]" in txt:
                partyPokemon = txt.split("]")
                party.append(self.readPokemon(partyPokemon[0]))
                for pokemon in partyPokemon[1:-1]:
                    party.append(self.readPokemon(pokemon[1:]))
            txt = f.readline()
            inventory = []
            if "]" in txt:
                inventoryPokemon = txt.split("]")
                inventory.append(self.readPokemon(inventoryPokemon[0]))
                for pokemon in inventoryPokemon[1:-1]:
                    inventory.append(self.readPokemon(pokemon[1:]))
            txt = f.readline()
            player_items = {}
            if txt != "\n":
                items = txt.replace("\n", '').split(',')
                for item in items:
                    info = item.split("/")
                    player_items[ITEMS[info[0]]] = int(info[1])
            txt = f.readline().split(',')
            p = Player(playerName,None,None)
            p.name, p.stance, p.diff, p.cash = playerName, playerStance, pdiff, playerCash
            p.bag.pokemons = party
            if len(party) > 0:
                p.change_main(party[0])
            p.inventory = inventory
            p.bag.items = player_items
            if i==0:
                self.player= p
            else:
                self.trainers[p.name]= p
            i+=1
        self.locations = {}
        txt= f.readline()
        while txt[:3] == 'SOL':
            l = Location(f, self.player, self.trainers)
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
        pokemon = Pokemon(int(info[6]), int(info[1]))
        pokemon.hp= float(info[2])
        pokemon.xp = int(info[3])
        pokemon.status = Status(info[4])
        if info[5] == "True":
            pokemon.shiny = True
        else:
            pokemon.shiny = False
        
        pokemon.attacks = []
        for potentialAttacks in info[7:]:
            if potentialAttacks[0] == '(':
                pokemon.attacks.append(self.readAttack(potentialAttacks))
        return pokemon

    def readAttack(self, text):
        info = text[1:-1].split("/")
        attack = makeAttack(int(info[0]), int(info[1]))
        return attack

    def save(self, player):
        s = player.print() + '\n'
        for trainer in self.trainers.values():
            s+= trainer.print() +"\n"
        s+= "EOPLAYERS\n"
        for location in self.locations.values():
            s += location.print_location(player)
        f = open("Save.txt", "w+")
        f.write(s + 'EOF')
        f.close()
        return s + 'EOF'