import random

class CardDeck:
    """Represents a deck of cards."""
    def __init__(self):
        self.original_deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4  # One deck of cards
        self.cards = self.original_deck * 8  # 8 decks of cards
        random.shuffle(self.cards)  # Shuffle the cards at the start

    def deal_card(self):
        """Returns a random card from the deck and reshuffles if 50% depleted."""
        if len(self.cards) < len(self.original_deck) * 4:  # Reshuffle when 50% depleted
            self.reshuffle()
        return self.cards.pop()

    def reshuffle(self):
        """Reshuffles the deck."""
        print("Reshuffling the deck...")
        self.cards = self.original_deck * 8
        random.shuffle(self.cards)

class Player:
    """Represents a player in the game."""
    def __init__(self, name):
        self.name = name
        self.cards = []
        self.score = 0
        self.money = 100

    def gamble(self, bet):
        """Gambles a certain amount of money."""
        if bet > self.money:
            print("Not enough money to gamble.")
            return False
        self.money -= bet
        return True

    def add_card(self, card):
        """Adds a card to the player's hand and updates the score."""
        self.cards.append(card)
        self.calculate_score()

    def calculate_score(self):
        """Calculates the player's score."""
        self.score = sum(self.cards)
        if 11 in self.cards and self.score > 21:
            self.cards.remove(11)
            self.cards.append(1)
            self.score = sum(self.cards)

    def has_blackjack(self):
        """Checks if the player has a blackjack."""
        return self.score == 21 and len(self.cards) == 2

    def is_busted(self):
        """Checks if the player is busted."""
        return self.score > 21

class BlackjackGame:
    """Represents the Blackjack game."""
    def __init__(self):
        self.deck = CardDeck()
        self.player = Player("Player")
        self.dealer = Player("Dealer")

    def compare_scores(self, bet):
        """Compares the scores of the player and the dealer."""
        if self.player.score == self.dealer.score:
            self.player.money += bet  
            return "Draw"
        elif self.dealer.has_blackjack():
            return "Lose, opponent has Blackjack"
        elif self.player.has_blackjack():
            self.player.money += bet * 1.5 
            return "Win with a Blackjack"
        elif self.player.is_busted():
            return "You went over. You lose"
        elif self.dealer.is_busted():
            self.player.money += bet * 2  
            return "Opponent went over. You win"
        elif self.player.score > self.dealer.score:
            self.player.money += bet * 2  
            return "You win"
        else:
            return "You lose"

    def play(self):
        """Main game loop."""
        # Initiate the wager
        while True:
            try:
                bet = int(input("Enter your bet: "))
                if self.player.gamble(bet):
                    break
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        # Initial deal
        for _ in range(2):
            self.player.add_card(self.deck.deal_card())
            self.dealer.add_card(self.deck.deal_card())

        # Player's turn
        game_over = False
        while not game_over:
            print(f"   Your cards: {self.player.cards}, current score: {self.player.score}")
            print(f"   Dealer's first card: {self.dealer.cards[0]}")

            if self.player.has_blackjack() or self.player.is_busted():
                game_over = True
            else:
                should_continue = input("Type 'y' to get another card, type 'n' to pass: ")
                if should_continue == 'y':
                    self.player.add_card(self.deck.deal_card())
                else:
                    game_over = True

        # Dealer's turn
        while self.dealer.score < 17 and not self.dealer.is_busted():
            self.dealer.add_card(self.deck.deal_card())

        # Final results
        print(f"   Your final hand: {self.player.cards}, final score: {self.player.score}")
        print(f"   Dealer's final hand: {self.dealer.cards}, final score: {self.dealer.score}")
        print(self.compare_scores(bet))
        print(f"Your remaining money: {self.player.money}")
        if self.player.money <= 0:
            print("You are out of money! Game over.")
            exit

if __name__ == "__main__":
    while input("Do you want to play a game of Blackjack? Type 'y' or 'n': ") == 'y':
        game = BlackjackGame()
        game.play()