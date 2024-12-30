from dataclasses import dataclass
from typing import List, Dict, Optional
import random

@dataclass
class Card:
    rank: str  # 'K', 'Q', 'A', or 'J' for Joker
    count: int

    def __init__(self, rank: str, count: int = 1):
        self.rank = rank
        self.count = count

    def __repr__(self):
        return f"{self.rank} (x{self.count})"

@dataclass
class Player:
    id: str
    name: str
    cards: List[Card]
    lives: int
    position: int  # Position in the game circle

class Game:
    def __init__(self, code: str):
        self.code = code
        self.players: List[Player] = []
        self.current_player_index = 0
        self.started = False
        self.deck = self.create_deck()
        self.current_required_card: Optional[str] = None  # 'K', 'Q', or 'A'
        self.current_play: List[Card] = []
        self.current_claim: str = ''  # What the player claims they're playing
        # Initialize roulette attributes
        self.chamber_positions = {}  # Player ID to bullet position
        self.current_chamber = {}    # Player ID to current chamber position
        
    def create_deck(self) -> List[Card]:
        deck = []
        # Add regular cards
        for rank in ['K', 'Q', 'A']:
            for _ in range(6):  # 6 of each rank
                deck.append(Card(rank=rank, count=1))
        # Add jokers
        for _ in range(2):  # 2 jokers
            deck.append(Card(rank='J', count=1))
        return deck

    def add_player(self, player_id: str, name: str) -> Player:
        # Check if player already exists
        existing_player = next((p for p in self.players if p.id == player_id), None)
        if existing_player:
            existing_player.name = name  # Update name if needed
            return existing_player
        
        position = len(self.players)
        player = Player(
            id=player_id,
            name=name,
            cards=[],
            lives=1,
            position=position
        )
        self.players.append(player)
        self.initialize_roulette(player_id)
        return player

    def start_game(self) -> bool:
        print(f"Starting game with {len(self.players)} players")
        if len(self.players) < 2 or self.started:
            print("Cannot start game: not enough players or already started")
            return False

        # Create the deck with specific cards
        self.deck = []
        # Add 6 Kings
        for _ in range(6):
            self.deck.append(Card(rank='K', count=1))
        # Add 6 Queens
        for _ in range(6):
            self.deck.append(Card(rank='Q', count=1))
        # Add 6 Aces
        for _ in range(6):
            self.deck.append(Card(rank='A', count=1))
        # Add 2 Jokers
        for _ in range(2):
            self.deck.append(Card(rank='J', count=1))

        print(f"Created deck with {len(self.deck)} cards")
        random.shuffle(self.deck)

        # Deal 5 cards to each player
        for player in self.players:
            player.cards = self.deck[:5]
            self.deck = self.deck[5:]
            print(f"Dealt cards to {player.name}: {[card.rank for card in player.cards]}")

        self.started = True
        self.current_required_card = random.choice(['K', 'Q', 'A'])
        print(f"Game started. Required card: {self.current_required_card}")
        return True

    def play_cards(self, player_id: str, cards: List[str], claim_rank: str) -> bool:
        player = next((p for p in self.players if p.id == player_id), None)
        if not player or player.id != self.players[self.current_player_index].id:
            return False  # Not this player's turn

        # Validate the cards played
        if len(cards) > 3 or any(card not in [c.rank for c in player.cards] for card in cards):
            return False  # Invalid play

        # Remove played cards from player's hand
        player.cards = [c for c in player.cards if c.rank not in cards]
        
        # Update turn to the next player
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        
        return True

    def challenge(self, challenger_id: str) -> Dict:
        challenger = self.get_player(challenger_id)
        current_player = self.players[self.current_player_index]
        
        # Check if the played cards match the claim
        all_match = all(card.rank in [self.current_claim, 'J'] for card in self.current_play)
        
        # Determine who needs to play roulette
        player_to_shoot = current_player if not all_match else challenger
        was_shot = self.fire_roulette(player_to_shoot.id)
        
        if was_shot:
            player_to_shoot.lives = 0  # Eliminate player
        
        # Reset current play
        self.current_play = []
        self.current_claim = ''
        self.current_required_card = random.choice(['K', 'Q', 'A'])
        
        return {
            "player_shot": player_to_shoot.id,
            "was_eliminated": was_shot,
            "was_lie": not all_match
        }

    def continue_play(self, player_id: str) -> bool:
        # Move to next player
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        return True

    def get_player(self, player_id: str) -> Optional[Player]:
        return next((p for p in self.players if p.id == player_id), None)

    def get_game_state(self, player_id: str) -> dict:
        """Get the game state for a specific player"""
        return {
            "started": self.started,
            "players": [
                {
                    "id": p.id,
                    "name": p.name,
                    "lives": p.lives,
                    "cards": [{"rank": c.rank} for c in p.cards] if p.id == player_id else None,
                    "cards_count": len(p.cards)
                }
                for p in self.players
            ],
            "current_player": self.players[self.current_player_index].name,  # Current player's name
            "required_card": self.current_required_card,
            "current_play": self.current_play
        }

    def initialize_roulette(self, player_id: str):
        """Initialize a player's revolver with one bullet in random position"""
        self.chamber_positions[player_id] = random.randint(1, 6)
        self.current_chamber[player_id] = 1

    def fire_roulette(self, player_id: str) -> bool:
        """Returns True if player is shot (eliminated)"""
        current = self.current_chamber[player_id]
        is_shot = current == self.chamber_positions[player_id]
        self.current_chamber[player_id] = (current % 6) + 1
        return is_shot

    def remove_player(self, player_id: str):
        """Remove a player from the game"""
        self.players = [p for p in self.players if p.id != player_id]
        
        # Clean up player's roulette state
        if player_id in self.chamber_positions:
            del self.chamber_positions[player_id]
        if player_id in self.current_chamber:
            del self.current_chamber[player_id]
        
        # If game was started and now has less than 2 players, reset it
        if self.started and len(self.players) < 2:
            self.started = False
            self.current_required_card = None
            self.current_play = []
            self.current_claim = ''