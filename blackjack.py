import random
import streamlit as st

class CardDeck:
    """Represents a deck of cards."""
    def __init__(self):
        suits = ["hearts", "diamonds", "clubs", "spades"]
        values = [2, 3, 4, 5, 6, 7, 8, 9, 10, "jack", "queen", "king", "ace"]
        self.original_deck = [(value, suit) for value in values for suit in suits]  # Cards with values and suits
        self.cards = self.original_deck * 8  # 8 decks of cards
        random.shuffle(self.cards)  # Shuffle the cards at the start

    def deal_card(self):
        """Returns a random card from the deck and reshuffles if 50% depleted."""
        if len(self.cards) < len(self.original_deck) * 4:  # Reshuffle when 50% depleted
            self.reshuffle()
        return self.cards.pop()

    def reshuffle(self):
        """Reshuffles the deck."""
        st.write("Reshuffling the deck...")
        suits = ["hearts", "diamonds", "clubs", "spades"]
        values = [2, 3, 4, 5, 6, 7, 8, 9, 10, "jack", "queen", "king", "ace"]
        self.original_deck = [(value, suit) for value in values for suit in suits]
        self.cards = self.original_deck * 8
        random.shuffle(self.cards)

class Player:
    """Represents a player in the game."""
    def __init__(self, name):
        self.name = name
        self.cards = []  # List of tuples (value, suit)
        self.score = 0
        self.money = 100

    def gamble(self, bet):
        """Gambles a certain amount of money."""
        if bet > self.money:
            st.error("Not enough money to gamble.")
            return False
        self.money -= bet
        return True

    def add_card(self, card):
        """Adds a card to the player's hand."""
        self.cards.append(card)
        self.calculate_score()

    def calculate_score(self):
        """Calculates the player's score, handling Aces as 1 or 11."""
        self.score = 0
        aces = 0
        for value, suit in self.cards:
            if value in ["jack", "queen", "king"]:
                self.score += 10
            elif value == "ace":
                aces += 1
                self.score += 11  # Initially count Ace as 11
            else:
                self.score += value

        # Adjust for Aces if score exceeds 21
        while self.score > 21 and aces:
            self.score -= 10  # Convert an Ace from 11 to 1
            aces -= 1

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
            blackjack_payout = int(bet * 1.5)  # Ensure integer payout
            self.player.money += bet + blackjack_payout
            return f"Win with a Blackjack! Payout: {bet + blackjack_payout}"
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

# Streamlit App
st.title("Blackjack Game")

if "game" not in st.session_state:
    st.session_state.game = BlackjackGame()

game = st.session_state.game

if "bet" not in st.session_state:
    st.session_state.bet = 0

if "game_over" not in st.session_state:
    st.session_state.game_over = False

if "player_turn" not in st.session_state:
    st.session_state.player_turn = True

def display_cards(cards):
    """Displays cards as text with values and suits."""
    for value, suit in cards:
        # Convert the value to a string if it's an integer
        value_str = str(value).capitalize() if isinstance(value, int) else value.capitalize()
        st.write(f"{value_str} of {suit.capitalize()}")

if st.session_state.player_turn:
    st.subheader("Place Your Bet")
    bet = st.number_input("Enter your bet:", min_value=1, max_value=game.player.money, step=1)
    if st.button("Place Bet"):
        if game.player.gamble(bet):
            st.session_state.bet = bet
            for _ in range(2):
                game.player.add_card(game.deck.deal_card())
                game.dealer.add_card(game.deck.deal_card())
            st.session_state.player_turn = False

            # Check if dealer's first card is an Ace for insurance
            if game.dealer.cards[0][0] == "ace":
                st.subheader("Insurance Bet")
                insurance_bet = st.number_input(
                    "Enter your insurance bet (up to half of your original bet):",
                    min_value=0,
                    max_value=st.session_state.bet // 2,
                    step=1,
                )
                if st.button("Place Insurance Bet"):
                    if game.player.gamble(insurance_bet):
                        st.session_state.insurance_bet = insurance_bet
                        st.success(f"Insurance bet of {insurance_bet} placed!")
                    else:
                        st.error("Not enough money for the insurance bet.")

if not st.session_state.player_turn:
    st.subheader("Your Turn")
    st.write("Your cards:")
    display_cards(game.player.cards)
    st.write(f"Current score: {game.player.score}")
    st.write("Dealer's first card:")
    display_cards([game.dealer.cards[0]])

    if game.player.has_blackjack():
        st.success("Blackjack! You win!")
        st.session_state.game_over = True
    elif game.player.is_busted():
        st.error("You went over 21! You lose!")
        st.session_state.game_over = True
    elif game.player.score == 21:
        st.success("You have 21! Your turn is over.")
        st.session_state.game_over = True
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Hit"):
                game.player.add_card(game.deck.deal_card())
                st.experimental_rerun()

        with col2:
            if st.button("Stand"):
                st.session_state.game_over = True

        with col3:
            if len(game.player.cards) == 2 and game.player.cards[0][0] == game.player.cards[1][0]:
                if game.player.money >= st.session_state.bet:
                    if st.button("Split"):
                        st.session_state.split_hand = [game.player.cards.pop()]
                        game.player.add_card(game.deck.deal_card())
                        st.session_state.split_bet = st.session_state.bet
                        st.experimental_rerun()
                else:
                    st.warning("Insufficient funds to split this turn.")

        if len(game.player.cards) == 2:
            if game.player.money >= st.session_state.bet:
                if st.button("Double Down"):
                    st.session_state.bet *= 2
                    game.player.add_card(game.deck.deal_card())
                    st.session_state.game_over = True
                    st.experimental_rerun()
            else:
                st.write("Insufficient funds to double down this turn.")

# Add the split hand logic here
if "split_hand" in st.session_state and st.session_state.split_hand:
    st.subheader("Playing Split Hand")
    st.write("Your split hand:")
    display_cards(st.session_state.split_hand)
    st.write(f"Current score: {game.player.score}")

    if st.button("Hit (Split Hand)"):
        st.session_state.split_hand.append(game.deck.deal_card())
        st.experimental_rerun()

    if st.button("Stand (Split Hand)"):
        st.session_state.split_hand = None  # End the split hand turn
        st.experimental_rerun()


if st.session_state.game_over:
    st.subheader("Dealer's Turn")
    while game.dealer.score < 17 and not game.dealer.is_busted():
        game.dealer.add_card(game.deck.deal_card())

    st.write("Dealer's final hand:")
    display_cards(game.dealer.cards)
    st.write(f"Dealer's final score: {game.dealer.score}")

    # Display the result of the game
    result = game.compare_scores(st.session_state.bet)
    st.write(result)
    st.write(f"Your remaining money: {game.player.money}")

    if game.player.money <= 0:
        st.error("You are out of money! Game over.")
        st.stop()

    # Options to play again or finish the game
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Play Again", key="play_again_1"):
            st.session_state.game = BlackjackGame()
            st.session_state.bet = 0
            st.session_state.game_over = False
            st.session_state.player_turn = True
            st.experimental_rerun()

    with col2:
        if st.button("Finish Game", key="finish_game_1"):
            st.write(f"Final Total Money: {game.player.money}")
            st.success("Thank you for playing!")
            st.stop()