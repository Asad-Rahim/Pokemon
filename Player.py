from Bag import Bag
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
        self.screen_dimensions = None, None
        self.diff = 0
        self.cash =0
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
        creatig the moving screen corners of the player using their current location.
        These cornors allow the screen to stop and start following at certain distances from the edge
        """
        self.screen_dimensions= x, y = min(max_width, self.curr_location.width), min(max_heigt,self.curr_location.height)
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
            i += '[' + str(pokemon) + '],'
        i= i[:-1]+'\n'
        return "{},{},{},{}".format(self.name, self.cash,self.stance, self.diff)+'\n'+s +i+ self.bag.print_items()