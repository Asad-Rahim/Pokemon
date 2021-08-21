from Bag import Bag
class Player:
    """
    Actual player
    """
    def __init__(self, name, location, tile):
        self.name = name
        self.bag = Bag(self)
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
        self.screen_dimensions = None, None
        self.xDrift =0
        self.yDrift = 0
        self.diff = 0
        self.cash =0
        self.repel= 0
    def add_pokemon(self, pokemon):
        if len(self.bag.pokemons) == 6:
            self.inventory.append(pokemon)
        else:
            self.bag.add_pokemon(pokemon)
            if self.main is None:
                self.change_main(pokemon)
    def heal(self):
        for pokemon in self.bag.pokemons:
            pokemon.restore()
    def change_main(self, pokemon):
        #pokemon must be in bag
        self.bag.pokemons[0], self.bag.pokemons[self.bag.pokemons.index(pokemon)]=\
            self.bag.pokemons[self.bag.pokemons.index(pokemon)], self.bag.pokemons[0]
        self.main = self.bag.main = pokemon
    def make_corners(self, max_width, max_heigt):
        """
        creating the moving screen corners of the player using their current location.
        These cornors allow the screen to stop and start following at certain distances from the edge
        """
        self.screen_dimensions= x, y = min(max_width, self.curr_location.width), min(max_heigt,self.curr_location.height)
        midpoint = x//2, y//2
        self.xDrift=self.yDrift=0
        x, y = x-1,y-1
        left,right = self.curr_tile, self.curr_tile
        while x >0:
            if left.left is not None:
                left = left.left
                x -= 1
                self.xDrift+=1
            if right.right is not None:
                right = right.right
                x -= 1
                self.xDrift-=1
            if left.left is None and right.right is None:
                x = 0
        up_left, down_left, up_right, down_right = left, left, right,right
        while y>0:
            if up_left.up is not None:
                up_left = up_left.up
                y -=1
                up_right = up_right.up
                self.yDrift-=1
            if down_left.down is not None:
                down_left = down_left.down
                down_right = down_right.down
                y -= 1
                self.yDrift+=1
            if up_left.up is  None and down_left.down is  None:
                y = 0
        self.corners = [up_left, up_right, down_left, down_right]
        self.xDrift, self.yDrift= self.xDrift//2, self.yDrift//2
        print(self.xDrift, self.yDrift)
    def print(self):
        s = self.bag.print_pokemons()+'\n'
        i = ''
        for pokemon in self.inventory:
            i += '[' + str(pokemon) + '],'
        i= i[:-1]+'\n'
        return "{},{},{},{}".format(self.name, self.cash,self.stance, self.diff)+'\n'+s +i+ self.bag.print_items()