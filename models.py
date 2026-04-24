# models.py

class Card:
    def __init__(self, card_type, name):
        self.card_type = card_type  # "Weapon", "Room", "Character"
        self.name = name

    def __repr__(self):
        return f"{self.name} ({self.card_type})"
    
    def __eq__(self, other):
        if isinstance(other, Card):
            return self.name == other.name and self.card_type == other.card_type
        return False

class Player:
    def __init__(self, character_name, start_pos, is_computer=False):
        self.character_name = character_name
        self.position = start_pos
        self.hand = []
        self.active = True  # Becomes False if they make a wrong accusation
        self.is_computer = is_computer
        self.last_room = None
        
        # --- Knowledge Base (The Notebook) ---
        # "possible_solutions" starts full and gets whittled down.
        # Structure: {'Character': {'Mustard', ...}, 'Weapon': {...}, 'Room': {...}}
        self.possible_solutions = {
            "Character": set(), 
            "Weapon": set(), 
            "Room": set()
        }
        # Tracks cards we definitively know are NOT in the envelope
        self.known_innocent_cards = set()
        
        # Enhanced knowledge tracking for AI players
        # Cards we know specific players HAVE (from refutations)
        # Structure: {player_name: {card_name1, card_name2, ...}}
        self.known_player_cards = {}
        
        # Cards we know specific players DON'T HAVE
        # Structure: {player_name: {card_name1, card_name2, ...}}
        self.known_player_not_cards = {}
        
        # Track suggestions made by each player for inference
        # Structure: [(suggester_name, suggestion_dict, refuter_name, shown_card_name), ...]
        self.suggestion_history = []

    def move(self, new_pos):
        self.position = new_pos

    def add_card(self, card):
        self.hand.append(card)
        # If I hold the card, it cannot be the murderer
        self.eliminate_card(card)

    def show_hand(self):
        return ", ".join([c.name for c in self.hand])

    def eliminate_card(self, card):
        """Removes a card from the list of suspects (Knowledge Update)."""
        self.known_innocent_cards.add(card.name)
        if card.name in self.possible_solutions[card.card_type]:
            self.possible_solutions[card.card_type].remove(card.name)
    
    def initialize_player_tracking(self, all_player_names):
        """Initialize tracking structures for all players."""
        for player_name in all_player_names:
            if player_name != self.character_name:
                self.known_player_cards[player_name] = set()
                self.known_player_not_cards[player_name] = set()