# ai_logic.py
import random
from config import *
from models import Card

class AIBrain:
    def __init__(self, player, all_card_names, all_player_names):
        self.player = player
        self.all_card_names = all_card_names # Dict of all possible names
        self.all_player_names = all_player_names
        self.initialize_knowledge()

    def initialize_knowledge(self):
        """Start by suspecting everyone, then remove own hand."""
        # 1. Fill possible solutions with everything
        for c_type, names_list in self.all_card_names.items():
            self.player.possible_solutions[c_type] = set(names_list)
        
        # 2. Initialize player tracking
        self.player.initialize_player_tracking(self.all_player_names)
        
        # 3. Hand is already processed via player.add_card() calling eliminate_card()
        pass

    def decide_move(self, board, roll):
        """
        AI Movement Logic:
        Perform a 'Random Walk' for 'roll' steps, but stop if we hit a room.
        Returns a list of coordinate tuples representing the path.
        """
        path = []
        current_pos = self.player.position
        
        # If already in a room, we can move out (but this shouldn't happen at start of turn)
        # The movement will naturally take us out of the room
        
        for step in range(roll):
            neighbors = board.get_valid_neighbors(current_pos)
            if not neighbors:
                break # Stuck, can't move further
            
            next_pos = random.choice(neighbors)
            path.append(next_pos)
            current_pos = next_pos
            
            # Stop if we entered a room (and weren't already there at start of step)
            if board.is_room(current_pos):
                break
                
        return path

    def pick_suggestion(self, current_room_name):
        """
        Strategy: Suggest the current room (Rule), plus 
        one Character and one Weapon that are still in 'possible_solutions'.
        """
        # Pick Character
        poss_chars = list(self.player.possible_solutions["Character"])
        if poss_chars:
            s_char = random.choice(poss_chars)
        else:
            s_char = "Miss Scarlett" # Fallback (shouldn't happen if logic is sound)

        # Pick Weapon
        poss_weaps = list(self.player.possible_solutions["Weapon"])
        if poss_weaps:
            s_weapon = random.choice(poss_weaps)
        else:
            s_weapon = "Dagger" # Fallback

        return s_char, s_weapon, current_room_name
    
    def choose_refutation_card(self, matching_cards):
        """
        When the AI has multiple cards that match a suggestion, choose which one to show.
        Strategy: Prefer showing a card that's less likely to be in the solution
        (i.e., one that's already known to be in someone else's hand, or one we've seen before).
        """
        if len(matching_cards) == 1:
            return matching_cards[0]
        
        # Strategy: Show the card that's least likely to be in the solution
        # (i.e., one that's already known to be in someone's hand)
        for card in matching_cards:
            # If we know someone else has this card, it's safe to show
            for player_name, known_cards in self.player.known_player_cards.items():
                if card.name in known_cards:
                    return card
        
        # Otherwise, just pick randomly (or first one)
        return matching_cards[0]

    def check_accusation_readiness(self):
        """
        Returns (True, SolutionDict) if the AI has narrowed it down to 1 option per category.
        """
        ps = self.player.possible_solutions
        if len(ps["Character"]) == 1 and len(ps["Weapon"]) == 1 and len(ps["Room"]) == 1:
            return True, {
                "Character": list(ps["Character"])[0],
                "Weapon": list(ps["Weapon"])[0],
                "Room": list(ps["Room"])[0]
            }
        return False, None
    
    def _ensure_player_tracking(self, player_name):
        """Ensure player tracking dictionaries exist for a given player."""
        if player_name not in self.player.known_player_cards:
            self.player.known_player_cards[player_name] = set()
        if player_name not in self.player.known_player_not_cards:
            self.player.known_player_not_cards[player_name] = set()
    
    def observe_suggestion(self, suggester_name, suggestion_dict, refuter_name, shown_card_name, all_players):
        """
        AI observes a suggestion made by another player and updates knowledge base.
        This implements the logical deduction requirements.
        
        Args:
            suggester_name: Name of player who made the suggestion
            suggestion_dict: {"Character": name, "Weapon": name, "Room": name}
            refuter_name: Name of player who refuted (None if no one refuted)
            shown_card_name: Name of card shown (None if no refutation)
            all_players: List of all Player objects
        """
        # Don't process our own suggestions (handled separately)
        if suggester_name == self.player.character_name:
            return
        
        char_name = suggestion_dict["Character"]
        weapon_name = suggestion_dict["Weapon"]
        room_name = suggestion_dict["Room"]
        suggested_cards = [char_name, weapon_name, room_name]
        
        # Get player indices for turn order
        suggester_idx = next(i for i, p in enumerate(all_players) if p.character_name == suggester_name)
        my_idx = next(i for i, p in enumerate(all_players) if p.character_name == self.player.character_name)
        
        if refuter_name is None:
            # No one could refute - all other players (except suggester) don't have any of these cards
            for player in all_players:
                if player.character_name != suggester_name and player.character_name != self.player.character_name:
                    self._ensure_player_tracking(player.character_name)
                    for card_name in suggested_cards:
                        self.player.known_player_not_cards[player.character_name].add(card_name)
        else:
            # Someone refuted - need to check turn order
            refuter_idx = next(i for i, p in enumerate(all_players) if p.character_name == refuter_name)
            
            # Ensure tracking exists for refuter
            self._ensure_player_tracking(refuter_name)
            
            # The refuter has at least one of the three cards
            self.player.known_player_cards[refuter_name].add(shown_card_name)
            
            # All players before the refuter (in turn order) don't have any of these cards
            num_players = len(all_players)
            for i in range(1, num_players):
                check_idx = (suggester_idx + i) % num_players
                checker = all_players[check_idx]
                
                if checker.character_name == refuter_name:
                    break  # Stop at refuter
                
                if checker.character_name != self.player.character_name:
                    # This player couldn't refute, so they don't have any of these cards
                    self._ensure_player_tracking(checker.character_name)
                    for card_name in suggested_cards:
                        self.player.known_player_not_cards[checker.character_name].add(card_name)
            
            # Complex inference: If only one player could refute and we know they don't have 2 cards,
            # they must have the third
            if shown_card_name:
                # Check if we can deduce which card the refuter has
                other_cards = [c for c in suggested_cards if c != shown_card_name]
                for other_card in other_cards:
                    # If we know the refuter doesn't have this card, and they showed a different one,
                    # we can't deduce anything new. But if we know they don't have 2 of the 3,
                    # we can deduce they have the third.
                    pass  # This is handled by the fact we know they showed one card
        
        # Perform inference: eliminate cards from solution if we know all players have them
        self.perform_inference()
    
    def perform_inference(self):
        """
        Perform logical deductions based on accumulated knowledge.
        Implements constraint satisfaction principles.
        """
        # Inference 1: If we know a player has a card, it can't be in the solution
        for player_name, cards in self.player.known_player_cards.items():
            for card_name in cards:
                # Find card type
                card_type = None
                for c_type, names_list in self.all_card_names.items():
                    if card_name in names_list:
                        card_type = c_type
                        break
                
                if card_type and card_name in self.player.possible_solutions[card_type]:
                    self.player.possible_solutions[card_type].remove(card_name)
                    self.player.known_innocent_cards.add(card_name)
        
        # Inference 2: If we know all players (except ourselves) don't have a card,
        # and we don't have it, it must be in the solution
        all_other_players = [name for name in self.all_player_names if name != self.player.character_name]
        
        for card_type, names_list in self.all_card_names.items():
            for card_name in names_list:
                # Skip if we already know it's not in solution
                if card_name in self.player.known_innocent_cards:
                    continue
                
                # Check if we have this card
                we_have_it = any(c.name == card_name for c in self.player.hand)
                if we_have_it:
                    continue
                
                # Check if all other players don't have it
                all_others_dont_have = all(
                    card_name in self.player.known_player_not_cards.get(player_name, set())
                    for player_name in all_other_players
                )
                
                if all_others_dont_have:
                    # This card must be in the solution!
                    # But we can't be 100% sure until we've seen all refutations
                    # So we'll keep it in possible_solutions but note it's likely
                    pass
        
        # Inference 3: Complex deduction - if only one player could refute a suggestion
        # and we know they don't have 2 of the 3 cards, they must have the third
        for suggester_name, suggestion_dict, refuter_name, shown_card_name in self.player.suggestion_history:
            if refuter_name and shown_card_name:
                char_name = suggestion_dict["Character"]
                weapon_name = suggestion_dict["Weapon"]
                room_name = suggestion_dict["Room"]
                suggested_cards = [char_name, weapon_name, room_name]
                
                # If we know the refuter doesn't have 2 of the 3 cards, they must have the third
                self._ensure_player_tracking(refuter_name)
                refuter_not_cards = self.player.known_player_not_cards.get(refuter_name, set())
                refuter_has_cards = self.player.known_player_cards.get(refuter_name, set())
                
                # Count how many of the suggested cards we know the refuter doesn't have
                known_not_count = sum(1 for card in suggested_cards if card in refuter_not_cards)
                
                if known_not_count == 2:
                    # They must have the third card
                    for card in suggested_cards:
                        if card not in refuter_not_cards and card not in refuter_has_cards:
                            self.player.known_player_cards[refuter_name].add(card)
                            # Also eliminate from solution
                            card_type = None
                            for c_type, names_list in self.all_card_names.items():
                                if card in names_list:
                                    card_type = c_type
                                    break
                            if card_type and card in self.player.possible_solutions[card_type]:
                                self.player.possible_solutions[card_type].remove(card)
                                self.player.known_innocent_cards.add(card)