class Bag:
    """
    A bag which the player holds containg everything they have on them. Limited to 6 pokemon
    """
    def __init__(self):
        self.items ={}
        self.pokemons = []
        self.main = None
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