from random import shuffle, randint


class Card:
    def __init__(self, action, data=None):
        self.action = action
        self.data = data

    def __str__(self):
        return f"{self.action}:{self.data}"


class Property:
    def __init__(self, name, price):
        self.name = name
        self.price = price
    
    def __str__(self):
        return self.name


class Plot(Property):
    pass


class Station(Plot):
    def __init__(self, name):
        super().__init__(name, 20000)


class Service(Property):
    def __init__(self, name):
        super().__init__(name, 15000)


class Deck:
    """Deck object, containing cards. Index of the top card is 0."""

    def __init__(self, *cards):
        self.cards = list(cards)
    
    def __getitem__(self, index):
        return self.cards[index]
    
    def __len__(self):
        return len(self.cards)
    
    def __str__(self):
        return str(self.cards)
    
    def shuffle(self):
        shuffle(self.cards)
    
    def draw(self):
        card = self.cards.pop(0)
        self.cards.append(card)
        return card


class Game:
    """Monopoly game object."""

    COMMUNITY_DECK = Deck(
        Card('OUTGO',   10000),
        Card('OUTGO',   5000),
        Card('OUTGO',   5000),
        Card('OUTCOME', 20000),
        Card('OUTCOME', 10000),
        Card('OUTCOME', 10000),
        Card('OUTCOME', 5000),
        Card('OUTCOME', 2500),
        Card('OUTCOME', 2000),
        Card('OUTCOME', 1000),
        Card('GO_TO', 0),  # start
        Card('GO_TO', 30), # jail
        Card('GO_BACK', 1), # belleville
        Card('BIRTHDAY'), # +1000 per other player
        Card('RELEASE'),
        Card('DRAW_CHANCE')
    )
    CHANCE_DECK = Deck(
        Card('OUTGO', 2000),
        Card('OUTGO', 1500),
        Card('OUTGO', 15000),
        Card('OUTCOME', 15000),
        Card('OUTCOME', 10000),
        Card('OUTCOME', 5000),
        Card('GO_TO', 0),  # start
        Card('GO_TO', 39), # rue de la paix
        Card('GO_TO', 30), # jail
        Card('GO_TO', 11), # la villette
        Card('GO_TO', 15), # gare de lyon
        Card('GO_TO', 24), # henri martin
        Card('GO_BACK_3_CASES'),
        Card('RELEASE'),

    )
    CASES = (
        'start',
        Plot('belleville', 6000),
        'community_chest',
        Plot('lecourbe', 6000),
        'income_taxes',
        Station('gare montparnasse'),
        Plot('vaugirard', 10000),
        'chance',
        Plot('courcelles', 10000),
        Plot('république', 12000),
        'jail_visit',
        Plot('la villette', 14000),
        Service('electricity'),
        Plot('neuilly', 14000),
        Plot('paradis', 16000),
        Station('gare de lyon'),
        Plot('mozart', 18000),
        'community_chest',
        Plot('saint michel', 18000),
        Plot('pigalle', 20000),
        'public_park',
        Plot('matignon', 22000),
        'chance',
        Plot('malesherbes', 22000),
        Plot('henri martin', 24000),
        Station('gare du nord'),
        Plot('saint honoré', 26000),
        Plot('la bourse', 26000),
        Service('water'),
        Plot('lafayette', 28000),
        'jail',
        Plot('breteuil', 30000),
        Plot('foch', 30000),
        'community_chest',
        Plot('capucines', 32000),
        Station('saint lazare'),
        'chance',
        Plot('champs élysées', 35000),
        'luxury_tax',
        Plot('rue de la paix', 40000)
    )

    def __init__(self):
        self.player_pos = 0
        self.player_doubles = 0
        self.player_jail_turns = 0
        self.counts = [0 for _ in range(len(self.CASES))]

        self.COMMUNITY_DECK.shuffle()
        self.CHANCE_DECK.shuffle()
    
    def move_player(self, destination):
        """Moves player absolutely."""
        dest = destination % len(self.CASES)
        self.player_pos = dest
        self.counts[dest] += 1
    
    def forward_player(self, distance):
        """Moves player relative to its position."""
        
        self.move_player(self.player_pos + distance)

    def get_current_case(self):
        return self.CASES[self.player_pos]
    
    def make_card_action(self, card):
        """Executes the action of a chance or community chest card. For now, only action that
        modify player position probabilities are executed."""

        if card.action in ('GO_TO', 'GO_BACK'):
            self.move_player(card.data)
        elif card.action == 'DRAW_CHANCE':
            card = self.CHANCE_DECK.draw()
            self.make_card_action(card)
        elif card.action == 'GO_BACK_3_CASES':
            self.forward_player(-3)
    
    def make_turn(self):
        """Executes a game turn. For now, only action that modify player position
        probabilities are executed."""
        # print("=== New turn ===")
        dices = randint(1, 6), randint(1, 6)
        # print(f"Dices: {dices}")
        
        if not self.player_jail_turns:
            if self.player_pos == 30: # player in jail but released this turn
                self.move_player(10) # jail visit

            self.forward_player(sum(dices))
            
            case = self.get_current_case()
            # print(f"Newpos: {self.player_pos} ({case})")
            if case in ('community_chest', 'chance'):
                deck = self.CHANCE_DECK if case == 'chance' else self.COMMUNITY_DECK
                card = deck.draw()
                self.make_card_action(card)
            elif case == 'jail':
                # print("Player jailed.")
                self.player_jail_turns = 3
                return
            
            if min(dices) == max(dices):
                self.player_doubles += 1
                if self.player_doubles > 3:
                    # print("Player jailed.")
                    self.move_player(30) # jail
                    self.player_doubles = 0
                else:
                    self.make_turn()
            else:
                self.player_doubles = 0
        
        else:
            if min(dices) == max(dices):
                self.move_player(10) # jail visit
                self.player_jail_turns = 0
                self.make_turn()
            else:
                self.player_jail_turns -= 1
                self.move_player(30) # move the player again to count jail turn
    
    def print_probas(self):
        for i, case in enumerate(self.CASES):
            proba = self.counts[i] / sum(self.counts)
            print(f"{case}: {proba}")
