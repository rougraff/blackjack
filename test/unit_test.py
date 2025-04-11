import pytest
from unittest.mock import MagicMock
from blackjack import CardDeck, Player, BlackjackGame
import streamlit as st

# Mock st.session_state
@pytest.fixture(autouse=True)
def mock_session_state():
    st.session_state = MagicMock()
    st.session_state.game = BlackjackGame()
    st.session_state.bet = 0
    st.session_state.game_over = False
    st.session_state.player_turn = True
    st.session_state.insurance_bet = 0

# CardDeck Tests
def test_card_deck_initialization():
    deck = CardDeck()
    assert len(deck.cards) == 416  # 8 decks of 52 cards
    assert len(deck.original_deck) == 52  # Single deck of cards

def test_card_deck_deal_card():
    deck = CardDeck()
    initial_count = len(deck.cards)
    card = deck.deal_card()
    assert card in deck.original_deck
    assert len(deck.cards) == initial_count - 1

def test_card_deck_reshuffle():
    deck = CardDeck()
    deck.cards = deck.cards[:200]  # Simulate depletion
    deck.deal_card()  # Trigger reshuffle
    assert len(deck.cards) == 415  # Back to full 8 decks minus one card

def test_card_deck_reshuffle_full():
    deck = CardDeck()
    deck.reshuffle()
    assert len(deck.cards) == 416  # Full 8 decks

# Player Tests
def test_player_initialization():
    player = Player("TestPlayer")
    assert player.name == "TestPlayer"
    assert player.cards == []
    assert player.score == 0
    assert player.money == 100

def test_player_gamble_success():
    player = Player("TestPlayer")
    assert player.gamble(50) is True
    assert player.money == 50

def test_player_gamble_failure():
    player = Player("TestPlayer")
    assert player.gamble(150) is False
    assert player.money == 100

def test_player_add_card():
    player = Player("TestPlayer")
    player.add_card((10, "hearts"))
    assert player.cards == [(10, "hearts")]
    assert player.score == 10

def test_player_calculate_score_with_ace():
    player = Player("TestPlayer")
    player.add_card(("ace", "hearts"))
    player.add_card((10, "spades"))
    player.add_card((5, "diamonds"))  # Should convert Ace to 1
    assert player.score == 16

def test_player_has_blackjack():
    player = Player("TestPlayer")
    player.add_card(("ace", "hearts"))
    player.add_card((10, "spades"))
    assert player.has_blackjack() is True

def test_player_is_busted():
    player = Player("TestPlayer")
    player.add_card((10, "hearts"))
    player.add_card((10, "spades"))
    player.add_card((5, "diamonds"))
    assert player.is_busted() is True

# BlackjackGame Tests
def test_blackjack_game_initialization():
    game = BlackjackGame()
    assert isinstance(game.deck, CardDeck)
    assert isinstance(game.player, Player)
    assert isinstance(game.dealer, Player)

def test_blackjack_game_compare_scores_draw():
    game = BlackjackGame()
    game.player.score = 20
    game.dealer.score = 20
    result = game.compare_scores(50)
    assert result == "Draw"
    assert game.player.money == 150  # Bet returned

def test_blackjack_game_compare_scores_player_blackjack():
    game = BlackjackGame()
    game.player.score = 21
    game.player.cards = [("ace", "hearts"), (10, "spades")]
    game.dealer.score = 18
    result = game.compare_scores(50)
    assert result == "Win with a Blackjack! Payout: 125"
    assert game.player.money == 175  # 1.5x bet

def test_blackjack_game_compare_scores_dealer_blackjack():
    game = BlackjackGame()
    game.player.score = 20
    game.dealer.score = 21
    game.dealer.cards = [("ace", "hearts"), (10, "spades")]
    result = game.compare_scores(50)
    assert result == "Lose, opponent has Blackjack"
    assert game.player.money == 100  # No change

def test_blackjack_game_compare_scores_player_busted():
    game = BlackjackGame()
    game.player.score = 22
    game.dealer.score = 18
    result = game.compare_scores(50)
    assert result == "You went over. You lose"
    assert game.player.money == 100  # No change

def test_blackjack_game_compare_scores_dealer_busted():
    game = BlackjackGame()
    game.player.score = 20
    game.dealer.score = 22
    result = game.compare_scores(50)
    assert result == "Opponent went over. You win"
    assert game.player.money == 200  # 2x bet

def test_blackjack_game_compare_scores_player_wins():
    game = BlackjackGame()
    game.player.score = 20
    game.dealer.score = 18
    result = game.compare_scores(50)
    assert result == "You win"
    assert game.player.money == 200  # 2x bet

def test_blackjack_game_compare_scores_player_loses():
    game = BlackjackGame()
    game.player.score = 18
    game.dealer.score = 20
    result = game.compare_scores(50)
    assert result == "You lose"
    assert game.player.money == 100  # No change