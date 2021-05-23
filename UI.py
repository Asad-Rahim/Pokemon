import pygame, math, copy
window=WIDTH=HEIGHT=screen_h=screen_w=front=back=fshiny=bshiny=save = 0
from Items import ITEMS, Healables, Ball
from Encounter import PVE_Encounter, PvP_Battle
continueBtns = [None, None, None, None, None]
def init(_window, w, h, sw,sh, _sprites, _save):
    global window
    global WIDTH
    global HEIGHT
    global screen_w 
    global screen_h
    global front
    global back
    global fshiny
    global bshiny
    global save
    window, WIDTH, HEIGHT, screen_w, screen_h , save= _window, w, h, sw, sh, _save
    front, back, fshiny, bshiny= _sprites
def btns(btns):
    global continueBtns
    if continueBtns[0] is None:
        continueBtns= btns
def UI_encounter(encounter):
    run  =False
    cont = None
    def pvp_guard():
        i, k = encounter.game_on()
        return i >-1 and k >-1
    def pve_guard():
        return (encounter.game_on()[0]!= -1 or encounter.game_on()[1]!=1) and not encounter.caught
    while (isinstance(encounter,PvP_Battle) and pvp_guard()) or (isinstance(encounter, PVE_Encounter) and pve_guard()):
        
        if isinstance(encounter,PvP_Battle) and  encounter.game_on() == (0,1):
            check = True
            swap = False
            while check:
                pygame.draw.rect(window, (25, 187, 212), (20, 380, 510, 300))
                font = pygame.font.Font('freesansbold.ttf', 18)
                new_enemy = encounter.new_enemy()
                msg = font.render("{} is going to send out {}. Will you...".format(encounter.enemy_player.name, new_enemy.name), True, (232, 65, 65), (245, 245, 245))
                window.blit(msg, (50, 400))
                swap_txt = font.render("Switch?", True,(25, 187, 212),(232, 65, 65))
                swaprect = swap_txt.get_rect()
                swaprect.center= (270,600)
                swapbtn = pygame.draw.rect(window,(232, 65, 65),  (210, 630, 120, 40))
                keep_txt = font.render("Keep Battling?", True ,(25, 187, 212),(232, 65, 65))
                keeprect = keep_txt.get_rect()
                keeprect.center= (270,470)
                keepbtn = pygame.draw.rect(window,(232, 65, 65), (210, 630, 120, 40))
                window.blit(keep_txt, keeprect)
                window.blit(swap_txt, swaprect)
                
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        check = False
                pygame.display.update()
                pos = pygame.mouse.get_pos()
                pressed1, pressed2, pressed3 = pygame.mouse.get_pressed()
                if keepbtn.collidepoint(pos) and pressed1:
                    check = False
                if swapbtn.collidepoint(pos) and pressed1:
                    swap = True
                    check = False
            if swap:
                swap_menu(encounter)

        if encounter.game_on()[0] ==1:
            pygame.draw.rect(window, (25, 187, 212), (20, 380, 510, 300))
            font = pygame.font.Font('freesansbold.ttf', 18)
            msg = font.render("{} has fainted, who will you send in?".format(encounter.player_pokemon.name), True, (232, 65, 65), (245, 245, 245))
            window.blit(msg, (50, 400))
            swap_menu(encounter)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = True
                break
        pygame.time.delay(100)
        window.fill((80, 240, 62))
        pygame.draw.circle(window, (0, 102, 9), (120, 280), 80)
        pygame.draw.circle(window, (0, 102, 9), (400, 100), 80)
        if encounter.player_pokemon.shiny:
            bshiny.draw(window, encounter.player_pokemon.num,120,280,4,90)
        else:
            back.draw(window, encounter.player_pokemon.num,120,280,4,90)
        if encounter.enemy.shiny:
            fshiny.draw(window, encounter.enemy.num,400,100,4,90)
        else:
            front.draw(window, encounter.enemy.num,400,100,4,90)
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
            pygame.time.delay(200)
            if keys[pygame.K_RETURN]:
                if cont =='{} was Caught!'.format(encounter.enemy.name):
                    encounter.player.add_pokemon(encounter.enemy)
                    encounter.caught = True
                cont = None
                break
        if run_btn.collidepoint(pos) and pressed1:
            run = True
            break
        if bag_btn.collidepoint(pos) and pressed1:
            if isinstance(encounter, PvP_Battle):
                i = ItemBagUI(encounter.player,1,None,None,150,150,screen_w-200,screen_h-200)
            else:
                i = ItemBagUI(encounter.player,1,None,encounter.enemy,150,150,screen_w-200,screen_h-200)
            i.info = True
            catch = i.draw()
            if catch is not None:
                if catch ==4:
                    cont = 'Yay {} was Caught!'.format(encounter.enemy.name)
                    break
                else:
                    cont = 'Darn {} broke out'.format(encounter.enemy.name)
            a = encounter.enemy_move()
            print(encounter.enemy.attack(encounter.player_pokemon, a))
            
        if party_btn.collidepoint(pos) and pressed1:
            swap_menu(encounter)

        for a in attacks:
            if a[0].collidepoint(pos) and pressed1:
                encounter.play(a[1])
    if encounter.game_on()==1 and not encounter.caught:
        encounter.xp_gain()
            


def swap_menu(encounter):
    player = encounter.player
    x = 660
    pygame.draw.rect(window, (89, 235, 240),(x,180,max(100*len(player.bag.pokemons),400),270))
    font = pygame.font.Font('freesansbold.ttf', 18)
    window.blit(
        font.render("Who would you like to send out?", True, (46, 46, 46), (89, 235, 240)),
        (x+20, 200))
    font2 = pygame.font.SysFont('georgia', 15)

    if encounter.player_pokemon.hp>0:
        close = window.blit(font.render("Cancel", True, (46, 46, 46), (89, 235, 240)), (660, 450))
    else:
        close = None
    pokemons = []
    sprites = front
    if encounter.player_pokemon.shiny:
        sprites = fshiny
    sprites.draw(window, encounter.player_pokemon.num, x, 220, 0, 90)
    window.blit(font2.render("HP:{}/{}".format(encounter.player_pokemon.hp, encounter.player_pokemon.maxhp),
                             True, (46, 46, 46), (89, 235, 240)), (x, 220 + 90 + 10))
    window.blit(font2.render("Status:" + str(encounter.player_pokemon.status.name),
        True, (46, 46, 46), (89, 235, 240)), (x, 220 + 90 + 30))
    x+=100
    for i in range(len(player.bag.pokemons)):
        if player.bag.pokemons[i] != encounter.player_pokemon:
            sprites = front
            if player.bag.pokemons[i].shiny:
                sprites = fshiny
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
        self.citem = None
        self.done = False
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
                save.save(self.player)
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
                if isinstance(self.citem, Ball):
                    return self.player.bag.consume_item(self.citem, self.pokemon)
                pygame.draw.rect(window, (89, 235, 240),(150,200,640,400))
                window.blit(font.render("Who would you like to use the {} on?".format(self.citem.name),True, (46, 46, 46), (89, 235, 240)),(160, 200))
                font2 = pygame.font.SysFont('georgia', 15)
                x = 160
                close =  window.blit(font.render("Cancel",True, (46, 46, 46), (89, 235, 240)),(640, 600))
                pokemons = []
                for i in range(len(self.player.bag.pokemons)):
                    sprites = front
                    if self.player.bag.pokemons[i].shiny:
                        sprites = fshiny
                    sprites.draw(window,self.player.bag.pokemons[i].num, x,220,0,90)
                    window.blit(font2.render("HP:{}/{}".format(self.player.bag.pokemons[i].hp, self.player.bag.pokemons[i].maxhp),
                                    True, (46, 46, 46), (89, 235, 240)),(x, 220+90+10))
                    window.blit(font2.render(
                        "Status:"+str(self.player.bag.pokemons[i].status.name),
                        True, (46, 46, 46), (89, 235, 240)), (x, 220 + 90 + 30))
                    if usuable_item(self.player.bag.pokemons[i], self.citem):
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
                        save.save(self.player)
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
                            self.player.bag.consume_item(self.citem, pokemon)
                            loop = run = False
                            self.draw()
            for item in items:
                if item[0].collidepoint(pos) and pressed1:
                    if self.info and self.pokemon is None:
                        self.use , self.citem = draw_item_info(self.player, item[1],1), item[1]
                        pygame.display.update()
                    elif self.info:
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
                        self.use , self.citem = draw_item_info(self.player, item[1]), item[1]
                        pygame.display.update()
                    else:
                        self.use , self.citem = draw_item_info(self.player, item[1],1), item[1]
                        pygame.display.update()
                        if isinstance(item[1], Healables) and usuable_item(self.pokemon,item[1]):
                            self.player.bag.consume_item(item[1], self.pokemon)
                            run = False
        self.done = True
def usuable_item(pokemon, item):
    temp = copy.copy(pokemon)
    item.use(temp)
    if pokemon.hp == temp.hp and pokemon.status.name == temp.status.name:
        return False
    return True
def draw_item_info(player, item, mode =0):
    pygame.draw.rect(window, (217, 179, 98), (0, screen_h, WIDTH, 200))
    item.sprite_num = 0
    front.draw(window, item.sprite_num, 0, screen_h, 0, 180)
    font = pygame.font.SysFont('georgia', 30)
    window.blit(font.render(item.name, True, (46, 46, 46), (217, 179, 98)), (15, HEIGHT - 35))
    window.blit(font.render('Use:', True, (46, 46, 46), (217, 179, 98)), (215, screen_h+10))

    if isinstance(item, Ball):
        window.blit(font.render(' Thrown at wild pokemon to catch them', True, (46, 46, 46), (217, 179, 98)), (285, screen_h+10))
        window.blit(font.render('Effectiveness:{}'.format(item.description), True, (46, 46, 46), (217, 179, 98)), (215, screen_h + 50))
        if mode:
            return None
        return window.blit(font.render("Throw {} at enemy".format(item.name), True, (46, 46, 46), (247, 10, 10)),
                    (300 + 740, screen_h + 25))
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
        return window.blit(font.render("Use {} on an ally".format(item.name), True, (46, 46, 46), (247, 10, 10)),
                    (300 + 740, screen_h + 25))

class InventoryUI():
    def __init__(self, player, page=1):
        self.player, self.page = player, page
        self.pokemon = self.move = self.item = self.prestege =self.swap =self.cancel= None
        self.store, self.attacks = None, []
        self.save = save
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
            sprites = front
            if self.player.bag.pokemons[i].shiny:
                sprites = fshiny
            pokemon = sprites.draw(window, self.player.bag.pokemons[i].num, screen_w-350 + x + 60,
                                   50 + i * ((screen_h-100 + 50) // 6), 0, 135)
            party.append((pokemon, self.player.bag.pokemons[i]))
            x = 0
        for i in range(6):
            for k in range(10):
                if i * 10 + k < len(self.player.inventory):
                    sprites = front
                    if self.player.inventory[i * 10 + k].shiny:
                        sprites = fshiny
                    pokemon = sprites.draw(window, self.player.inventory[i * 10 + k].num, 80 + k * (110),
                                           100 + (120) * i, 0, 105)
                    inventory.append((pokemon, self.player.inventory[i * 10 + k]))

        pygame.display.update()
        run, remake= True, False
        current = [None, None, None]
        selected = [None, None, None]
        if self.pokemon is not None:
            self.item, self.swap, self.prestege, self.move, self.attacks = draw_pokemon_info(self.player, self.pokemon[0])
            pygame.draw.circle(window, (247, 10, 10), self.pokemon[1].center, self.pokemon[1][2] // 2 + 3, 2)
            selected = self.pokemon
            self.pokemon = None
        itembag = None
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            keys = pygame.key.get_pressed()
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
            if itembag is not None and itembag.done:
                run= False
                self.draw()
            if back.collidepoint(pos) and pressed1:
                run = False
            elif remake and not pressed1:
                run = False
                self.draw()
            elif (continueBtns[2] is not None and continueBtns[2].collidepoint(pos) and pressed1) or keys[pygame.K_b]:
                run = False
                itembag = ItemBagUI(self.player,1,None,None,0,0,screen_w,screen_h)
                itembag.draw()
            elif (continueBtns[4] is not None and continueBtns[4].collidepoint(pos) and pressed1) or keys[pygame.K_q]:
                self.save.save(self.player)
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
                itembag = ItemBagUI(self.player, 1, None, selected[0], 200, 200, screen_w - 350 - 50, screen_h - 250)
                itembag.draw()
                
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
                        self.pokemon = selected
                else:
                    if current[0] is not None and current[0] is not selected[0]:
                        pygame.draw.circle(window, current[2], current[1].center, current[1][2] // 2 + 3, 2)
                        curent = None, None, None
                    if temp[0] is not None:
                        pygame.draw.circle(window, (61, 224, 69), temp[1].center, temp[1][2] // 2 + 3, 2)
                        current = temp[0], temp[1], temp[2]
                pygame.display.update()


def attacktxt( text, x= 200 + 530, y = HEIGHT - 200 + 45):
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

def draw_pokemon_info(player, pokemon):
    pygame.draw.rect(window, (217, 179, 98), (0, screen_h, WIDTH, 200))
    sprites = front
    if pokemon.shiny:
        sprites = fshiny
    sprites.draw(window,pokemon.num,0,screen_h,0,180)
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
