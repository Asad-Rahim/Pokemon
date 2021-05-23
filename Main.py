import pygame, ctypes
from Items import ITEMS
import SpriteSheet

ATTACKS = {'iron tail': [30, 15, 0.0, 70, 100, 'Normal', ('', 100)],
           'thunder': [65, 5, 0.2, 80, 80, 'Electrike', ('', 100)],
           'flame thrower': [40, 15, 0.0, 70, 95, 'Fire', ('Burned', 50)],
           'rock crush': [55, 5, 0.1, 40, 70, 'Ground', ('', 100)]}
POKEMON = {'pikachu': [120, 'Electrike', ('Raichu', 20), 190, 0, 'iron tail', 'thunder', 'rock crush'],
           'charizard': [170, 'Fire', ('None', 0), 45, 4, 'flame thrower', 'rock crush']}


from Player import Player
from Encounter import PVE_Encounter, PvP_Battle
from Pokemon import Pokemon, Attack, Status


# WIDTH, HEIGHT= 550, 600
# window = pygame.display.set_mode((WIDTH,HEIGHT))

# screen_dimensions = WIDTH-180//TILE_LENGTH,HEIGHT-120//TILE_LENGTH


#LOCATION = {}
pygame.init()
ctypes.windll.user32.SetProcessDPIAware()
WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
screen_w, screen_h = WIDTH - 350, HEIGHT - 200
SCREEN_DETAILS = [window, WIDTH, HEIGHT, screen_w, screen_h]
pygame.display.set_caption('Pokemon')

sprites = SpriteSheet.SpriteSheet('spritesheet.png', 1, 4)
walk = SpriteSheet.SpriteSheet('PlayerSprite.png', 4, 4)
front = SpriteSheet.SpriteSheet('front.png', 21, 31)
back = SpriteSheet.SpriteSheet('back.png', 21, 31)
frontShiny = SpriteSheet.SpriteSheet('front-shiny.png', 21, 31)
backShiny = SpriteSheet.SpriteSheet('back-shiny.png', 21, 31)
from Location import LoadSave, LoadSave, TILE_LENGTH
from UI import init, btns
save = LoadSave('Save.txt')
init(window,WIDTH, HEIGHT,screen_w,screen_h, [front,back, frontShiny,backShiny], save)
from UI import ItemBagUI,InventoryUI, UI_encounter

def print_screen(player):
    """
    Print all the tiles in around the player using the corners of player
    """
    tile = player.corners[0]
    left_edge = player.corners[0]
    right_edge = player.corners[1]
    direction = True
    screen_dimensions = player.screen_dimensions
    x, y = (screen_w - screen_dimensions[0] * TILE_LENGTH) // 2, (
                screen_h - screen_dimensions[1] * TILE_LENGTH) // 2
    playerx, playery = 0, 0
    while (direction and tile != player.corners[3]) or (not direction and tile != player.corners[2]):
        tile.draw(x,y,window,walk)
        if tile == player.curr_tile:
            # pygame.draw.circle(window,  (30, 213, 230), (x+TILE_LENGTH//2,y+TILE_LENGTH//2), TILE_LENGTH//2)
            playerx, playery = x, y
        if (direction and (tile.right is None or tile == right_edge)) or \
                (not direction and (tile.left is None or tile == left_edge)):
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
    tile.draw(x,y,window)
    walk.draw(window, player.stance, playerx, playery, -1)
    pygame.draw.rect(window, (255, 255, 255), (screen_w, 0, 350, HEIGHT))
    pygame.draw.rect(window, (255, 255, 255), (0, screen_h, WIDTH, 200))
    i = 0
    rows = 0
    font = pygame.font.SysFont('georgia', 30)

    while i < len(player.dialogue):
        txt = font.render("{}".format(player.dialogue[i:i + 30]), True, (46, 46, 46), (255, 255, 255))
        window.blit(txt, (20, screen_h + 20 + rows * 20))
        i += 30
        rows += 1
    txt = font.render("Press enter to continue", True, (46, 46, 46), (255, 255, 255))
    continueBtns[2] = window.blit(font.render("BAG", True, (46, 46, 46), (255, 255, 255)), (screen_w + 50, 160))
    continueBtns[3] = window.blit(font.render("Inventory", True, (46, 46, 46), (255, 255, 255)), (screen_w + 50, 250))
    continueBtns[4] = window.blit(font.render("Save and Quit", True, (46, 46, 46), (255, 255, 255)),
                                  (WIDTH - 250, 15))
    if player.stopped:
        continueBtns[0] = window.blit(txt, (20, HEIGHT - 40))
        continueBtns[1] = window.blit(txt, (screen_w - 400, HEIGHT - 40))


fullscreen = False
continueBtns = [None, None, None, None, None]
main_run = True


def command(player, text):
    txt = text.split('.')
    if txt[0] == 'spawn':
        if len(txt) == 3 and txt[1] in POKEMON.keys():
            if txt[2].isnumeric() and 1 <= int(txt[2]) <= 100:
                info = POKEMON[txt[1]]
                p = Pokemon(txt[1], info[4], int(txt[2]))
                e = PVE_Encounter(player, player.curr_location)
                e.enemy = p
                return True, e
        elif len(txt) == 4 and txt[1] in POKEMON.keys():
            if txt[2].isnumeric() and 1 <= int(txt[2]) <= 100 and txt[3] == 'shiny':
                info = POKEMON[txt[1]]
                p = Pokemon(txt[1], info[4], int(txt[2]))
                p.shiny = True
                e = PVE_Encounter(player, player.curr_location)
                e.enemy = p
                return True, e
    elif txt[0] == 'give':
        if len(txt) == 2 and txt[1] in ITEMS:
            player.bag.add_item(ITEMS[txt[1]])
            return True, None
        elif len(txt) == 3 and txt[1] in ITEMS and txt[2].isnumeric():
            if int(txt[2]) > 0:
                for i in range(int(txt[2])):
                    player.bag.add_item(ITEMS[txt[1]])
                return True, None
    return False, None


if __name__ == '__main__':
    Asad = save.player
    print(Asad.curr_location)
    # l2 = Location([('charizard',3,100, 1, 100)], "test_A.txt")
    # l = Location([('charizard',3,100, 1, 0)], 'test_level.txt')

    # pygame.display.set_mode((WIDTH,HEIGHT),pygame.RESIZABLE)
    window.fill((46, 46, 46))
    
    # print_text('Welcome to the pokemon world! Please enter your name')

    # s = POKEMON['pikachu']
    # p = Pokemon('pikachu', 0,5)
    # p.set_hp(40)
    # Asad.add_pokemon(p)

    # for i in range(26):
    #   Asad.add_pokemon(Pokemon('charizard', 3, 5))
    # Asad.inventory[1].shiny = True
    # print(l2.height, l2.width)
    # print_tile(l.start, True, (WIDTH -l.width*40)//2,(HEIGHT-l.height*40)//2)
    # print_player(Asad)
    # screen_dimensions = min((screen_w) // TILE_LENGTH, Asad.curr_location.width), min(
    #     (screen_h) // TILE_LENGTH,
    #     Asad.curr_location.height)
    # Asad.screen_dimensions = screen_dimensions
    Asad.make_corners((screen_w) // TILE_LENGTH, (screen_h) // TILE_LENGTH)
    # Bob = Player(None,Asad.curr_location, None)
    # Asad.curr_tile.down.down.walk_to(Bob)
    # for i in range(10):
    #     ball = ITEMS['Full Restore']
    #     Asad.bag.add_item(ball)
    # print_screen(Asad)
    # i = InventoryUI(Asad)
    # i.draw()
    pygame.display.update()
    encounter = None

    font = pygame.font.SysFont('georgia', 20)
    # e = PVE_Encounter(Asad, Asad.curr_location)
    # print(e.catch())
    # UI_encounter(PVE_Encounter(Asad, Asad.curr_location))
    curr = Asad.curr_location
    left = right = up = down = False
    pressed = cheat = False
    count = 0
    text = ''
    # i = ItemBagUI(Asad)
    # i.draw()
    time = 200
    print(Asad.bag.items)
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
                pygame.draw.rect(window, (104, 107, 105), (10, screen_h - 70, screen_w - 10, 30))
                window.blit(font.render(text, True, (46, 46, 46), (104, 107, 105)), (10, screen_h - 70))
                if (continueBtns[4] is not None and continueBtns[4].collidepoint(pos) and pressed1):
                    save.save(Asad)
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
                        pygame.draw.rect(window, (104, 107, 105), (0, screen_h - 50, screen_w, 50))
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
                                         and pressed1):
                Asad.stopped = False
                Asad.dialogue = ''
        elif (continueBtns[2] is not None and continueBtns[2].collidepoint(pos) and pressed1) or keys[pygame.K_b]:
            btns(continueBtns)
            i = ItemBagUI(Asad,1,None,None,0,0,screen_w,screen_h)
            i.info = True
            i.draw()
        elif (continueBtns[3] is not None and continueBtns[3].collidepoint(pos) and pressed1) or keys[pygame.K_i]:
            btns(continueBtns)
            i = InventoryUI(Asad)
            i.draw()
        elif (continueBtns[4] is not None and continueBtns[4].collidepoint(pos) and pressed1) or keys[pygame.K_q]:
            save.save(Asad)
            main_run = False
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            left = True
            Asad.stance = 2 * (count % 2) + 5
            count += 1
            if Asad.corners[0].left is not None:
                # if Asad.corners[1].x- Asad.curr_tile.x== Asad.curr_tile.x -Asad.corners[0].x:
                for corner in range(len(Asad.corners)):
                    Asad.corners[corner] = Asad.corners[corner].left

            encounter = Asad.curr_tile.left.walk_to(Asad)
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            right = True
            Asad.stance = 2 * (count % 2) + 9
            count += 1
            if Asad.corners[1].right is not None:
                # if Asad.corners[1].x- Asad.curr_tile.x== Asad.curr_tile.x -Asad.corners[0].x:
                for corner in range(len(Asad.corners)):
                    Asad.corners[corner] = Asad.corners[corner].right

            encounter = Asad.curr_tile.right.walk_to(Asad)
        elif keys[pygame.K_w] or keys[pygame.K_UP]:
            up = True
            Asad.stance = 2 * (count % 2) + 13
            count += 1
            if Asad.corners[0].up is not None:
                # if Asad.corners[3].y- Asad.curr_tile.y== Asad.curr_tile.y -Asad.corners[0].y:
                for corner in range(len(Asad.corners)):
                    Asad.corners[corner] = Asad.corners[corner].up

            encounter = Asad.curr_tile.up.walk_to(Asad)
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            down = True
            Asad.stance = 2 * (count % 2) + 1
            count += 1
            if Asad.corners[2].down is not None:
                # if Asad.curr_tile.y - Asad.corners[0].y == Asad.corners[3].y - Asad.curr_tile.y:
                for corner in range(len(Asad.corners)):
                    Asad.corners[corner] = Asad.corners[corner].down

            encounter = Asad.curr_tile.down.walk_to(Asad)
        else:
            count = 0
            if left:
                Asad.stance = 4
            elif right:
                Asad.stance = 8
            elif up:
                Asad.stance = 12
            elif down:
                Asad.stance = 0
            up = down = right = left = False
        if curr != Asad.curr_location:
            curr = Asad.curr_location
            screen_dimensions = min((WIDTH - 350) // TILE_LENGTH, Asad.curr_location.width), min(
                (HEIGHT - 200) // TILE_LENGTH, Asad.curr_location.height)
            Asad.make_corners((screen_w) // TILE_LENGTH, (screen_h) // TILE_LENGTH)
            i = 1

        if event.type == pygame.KEYUP:
            pressed = False
        if not pressed and pygame.key.get_mods() & pygame.KMOD_CTRL:
            cheat = not cheat
            pressed = True
        # item_bag_UI(Asad)
        # aaaaaaprint_tile(Asad.curr_location.start, True, (WIDTH -Asad.curr_location.width*40)//2,(HEIGHT-Asad.curr_location.height*40)//2)
        # pygame.draw.circle(window, (30, 213, 230),
        #                   (Asad.curr_tile.x +20+ (WIDTH -Asad.curr_location.width*40)//2, Asad.curr_tile.y + 20+(HEIGHT-Asad.curr_location.height*40)//2), 20)
        pygame.display.update()
        #encounter= PvP_Battle(Asad,Asad,1)
        if encounter is not None and Asad.main.hp > 0:
            UI_encounter(encounter)
            print(type(encounter))
            if isinstance(encounter, PvP_Battle):
                print(encounter.game_on())
                if encounter.game_on()[1] ==-1:
                    tile = encounter.enemy.curr_tile
                    tile.up.down =tile.left.right=tile.right.left=tile.down.up= tile.floor
                else:
                    for pokemon in encounter.enemy_player.bag.pokemons:
                        pokemon.retore()
            if Asad.main.hp ==0:
                Asad.main = encounter.player_pokemon
            encounter = None
            # pygame.display.set_mode((curr.width * TILE_LENGTH, curr.height * TILE_LENGTH))
    pygame.quit()
