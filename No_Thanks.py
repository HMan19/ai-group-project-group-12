import random

# 1. Deck
# ----------------------------------------------------------------------------

class Deck(object):
    """
    Deck consists of list of numbers (cards). Is initialised with standard list
    of cards in No Thanks!. Decks can be shuffled, drawn from and number of 
    cards counted.
    """
    
    def __init__(self):
        self.deck = []
        
    def build(self):
        cards_all = range(3,36)
        deck = random.sample(cards_all, 24)
        
        for card in deck:
            self.deck.append(card)
        
        print("The deck has been shuffled.")
            
    def draw(self):
        return self.deck.pop()

    def check_end(self):
        if self.deck == []:
            return True
        
# 2. Player
# ----------------------------------------------------------------------------
        
class Player(object):
    """
    Player consists of a list of cards and number of chips in posession.
    Players can take or pass cards and/or chips. Total points to player at any
    time can be calculated.
    """
    
    def __init__(self, name):
        self.name = name
        self.card_hand = list()
        self.chip_hand = 11
        
    def draw_card(self, deck, player):
        global card_pool
        
        card_pool = deck.draw()
        print(f'{self.name} draws the number ' + str(card_pool) + ".")
        
        player.weighted_play(player, deck)
    
    def take_card(self, player, deck):
        global card_pool
        global chip_pool
        global game_end
        
        game_end = False
        
        self.card_hand.append(card_pool)
        self.chip_hand += chip_pool
        
        print(f'{self.name} takes the ' + str(card_pool) + " and " + str(chip_pool) + " chips.")
        print(f'{self.name} has ' + str(self.chip_hand) + ' chips remaining.')
        
        chip_pool = 0
        
        if not deck.check_end():
            player.draw_card(deck, player)
        else:
            game_end = True
        
    def pass_card(self):
        
        global card_pool
        global chip_pool
        
        self.chip_hand -= 1
        chip_pool += 1
        
        print(f'{self.name} passes the ' + str(card_pool) + " and loses a chip.")
        print(f'{self.name} has ' + str(self.chip_hand) + ' chips remaining.')
        
    def rand_play(self, player, deck):
        """
        Action is randomly determined. Note that players must take a card if
        they are out of chips.
        """
        global chip_pool
        decision = random.randint(0,1)
        
        
        if self.chip_hand == 0:
            decision == 0
        
        if decision == 0:
            player.take_card(player, deck)
            
        if decision == 1:
            player.pass_card()
            
    def remove_runs(player_hand):
        player_hand.sort()
        player_hand.reverse()
        remove_list = []
        
        for i in player_hand:
            if i-1 in player_hand:
                remove_list.append(i)

        for i in remove_list:
            player_hand.remove(i)
            
        return player_hand
    
    def point_tally(self):
        self.card_hand = Player.remove_runs(self.card_hand)
        card_points = sum(self.card_hand)
        chip_points = self.chip_hand
        return card_points - chip_points
    
    def chip_weight(chip_count):
        # Linear function mx + c such that chip_weight = 1 when chip_count = 1
        # and chip_weight = 3 when chip_count = 11
        return 0.2*chip_count + 0.8
        
    
    def weighted_play(self, player, deck):
        global card_pool
        global chip_pool
    
        take_card_hand = Player.remove_runs(self.card_hand + [card_pool])
        take_chip_hand = self.chip_hand + chip_pool
        pass_card_hand = Player.remove_runs(self.card_hand)
        pass_chip_hand = self.chip_hand - 1
        
        # Unevenly weights passing over taking to make the players pick up more
        take_value = sum(take_card_hand) - (Player.chip_weight(take_chip_hand)/2) * take_chip_hand
        pass_value = sum(pass_card_hand) - Player.chip_weight(pass_chip_hand) * pass_chip_hand
        
        # print('take_value is '+str(take_value)+' and pass_value is '+str(pass_value))
        
        if take_value <= pass_value or self.chip_hand <= 0:
            player.take_card(player, deck)
            
        else:
            player.pass_card()
        
        
        
        
    
# 3. Game
# ----------------------------------------------------------------------------

def Run_Game(player_1, player_2, player_3):
    """
    A game reflects an iteration of turns, until the deck emtpies and total
    points are tallied. Winner is then determined. Initialised with three
    players.
    """

    Player_1 = Player(player_1)
    Player_2 = Player(player_2)
    Player_3 = Player(player_3)

    deck = Deck()
    deck.build()
    turn_no = 1
    global card_pool
    global chip_pool 
    global game_end
    """
    Global used as card_pool and chip_pool need to be updated each turn so
    cannot be reset between function calls.
    """
    card_pool = 0
    chip_pool = 0
    game_end = False
    random_start = True
    if random_start:
        turn_no = random.randint(1, 3)
        if turn_no == 1:
            Player_1.draw_card(deck, Player_1)
        elif turn_no == 2:
            Player_2.draw_card(deck, Player_2)
        elif turn_no == 3:
            Player_3.draw_card(deck, Player_3)
    
    else:
        turn_no = 1
        Player_1.draw_card(deck, Player_1)
    
    while not game_end:
        turn_no += 1
        
        if turn_no % 3 == 1:
            Player_1.weighted_play(Player_1, deck)
            
        if turn_no % 3 == 2:
            Player_2.weighted_play(Player_2, deck)
            
        if turn_no % 3 == 0:
            Player_3.weighted_play(Player_3, deck)
            
    else:
        P1_total = Player_1.point_tally()
        P2_total = Player_2.point_tally()
        P3_total = Player_3.point_tally()
        
        print(f'{Player_1.name} has a final score of ' + str(P1_total))
        print(f'{Player_2.name} has a final score of ' + str(P2_total))
        print(f'{Player_3.name} has a final score of ' + str(P3_total))
        
        if min(P1_total, P2_total, P3_total) == P1_total:
            print(f'{Player_1.name} has won!!!')
            
        elif min(P1_total, P2_total, P3_total) == P2_total:
             print(f'{Player_2.name} has won!!!')
         
        elif min(P1_total, P2_total, P3_total) == P3_total:
             print(f'{Player_3.name} has won!!!')
            
Run_Game('Alice', 'Bob', 'Claire')  
