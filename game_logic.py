# game_logic.py
import random
import time
from config import *
from models import Player, Card
from board import Board
from ai_logic import AIBrain
from ui import Colors, clear_screen, print_header, get_player_color

class ClueGame:
    def __init__(self):
        self.board = Board()
        self.players = []
        self.solution = {}
        self.turn_index = 0
        self.ai_brains = {} 
        self.winner = None
        self.running = True
        self.setup_game()

    def setup_game(self):
        clear_screen()
        # Header text inside setup_game guarantees it is seen after the clear
        print_header("Initializing Cluedo") 
        
        # 1. Create Players
        for i, char_name in enumerate(CHARACTERS):
            is_computer = (i > 0) # Player 1 is Human, rest AI
            start_pos = START_POSITIONS[char_name]
            p = Player(char_name, start_pos, is_computer)
            self.players.append(p)
        
        # 1b. Initialize AI Brains (after all players are created)
        all_names = {"Character": CHARACTERS, "Weapon": WEAPONS, "Room": ROOMS}
        all_player_names = [p.character_name for p in self.players]
        for i, p in enumerate(self.players):
            if p.is_computer:
                self.ai_brains[i] = AIBrain(p, all_names, all_player_names)

        # 2. Setup Solution
        all_cards = []
        all_cards.extend([Card("Character", c) for c in CHARACTERS])
        all_cards.extend([Card("Weapon", w) for w in WEAPONS])
        all_cards.extend([Card("Room", r) for r in ROOMS])
        
        random.shuffle(all_cards)
        
        sol_c = next(c for c in all_cards if c.card_type == "Character")
        all_cards.remove(sol_c)
        sol_w = next(c for c in all_cards if c.card_type == "Weapon")
        all_cards.remove(sol_w)
        sol_r = next(c for c in all_cards if c.card_type == "Room")
        all_cards.remove(sol_r)
        
        self.solution = {"Character": sol_c, "Weapon": sol_w, "Room": sol_r}
        
        # DEBUG: Uncomment to see the answer for testing
        # print(f"{Colors.GREY}DEBUG SOLUTION: {self.solution}{Colors.RESET}")

        # 3. Deal Cards
        random.shuffle(all_cards)
        p_idx = 0
        while all_cards:
            card = all_cards.pop()
            self.players[p_idx].add_card(card)
            p_idx = (p_idx + 1) % len(self.players)
                    
        input(f"\n{Colors.ORANGE}Press Enter to Start...{Colors.RESET}")

    def roll_dice(self):
        return random.randint(1, 6)

    def handle_accusation(self, player, accusation_dict=None):
        p_color = get_player_color(player.character_name)
        print(f"\n{Colors.RED}!!! {player.character_name} IS MAKING AN ACCUSATION !!!{Colors.RESET}")
        
        if accusation_dict is None:
            # Human Input
            print("Enter your accusation details:")
            c = input("Character: ")
            w = input("Weapon: ")
            r = input("Room: ")
            accusation_dict = {"Character": c, "Weapon": w, "Room": r}
        
        print(f"Accusation: {accusation_dict['Character']} with {accusation_dict['Weapon']} in {accusation_dict['Room']}")
        
        is_correct = (
            accusation_dict['Character'].lower() == self.solution['Character'].name.lower() and
            accusation_dict['Weapon'].lower() == self.solution['Weapon'].name.lower() and
            accusation_dict['Room'].lower() == self.solution['Room'].name.lower()
        )

        if is_correct:
            print(f"\n{Colors.BOLD}{Colors.GREEN}*** CONGRATULATIONS! {player.character_name} SOLVED THE MURDER! ***{Colors.RESET}")
            print(f"Solution: {self.solution}")
            self.winner = player
            self.running = False
            return True
        else:
            print(f"\n{Colors.RED}>>> INCORRECT! {player.character_name} has been ELIMINATED. <<<{Colors.RESET}")
            player.active = False
            return False

    def handle_refutation(self, suggester_idx, suggestion_dict):
        print(f"\n{Colors.ORANGE}--- Refutation Phase ---{Colors.RESET}")
        suggester = self.players[suggester_idx]
        refutation_made = False
        refuter_name = None
        shown_card_name = None

        num_players = len(self.players)
        for i in range(1, num_players):
            check_idx = (suggester_idx + i) % num_players
            checker = self.players[check_idx]
            
            # Gather matching cards
            matches = [c for c in checker.hand if c.name in suggestion_dict.values()]
            
            if matches:
                refutation_made = True
                refuter_name = checker.character_name
                checker_color = get_player_color(checker.character_name)
                print(f"> {checker_color}{checker.character_name}{Colors.RESET} can refute.")
                
                # Choose which card to show
                if checker.is_computer and check_idx in self.ai_brains:
                    # AI chooses strategically
                    shown_card = self.ai_brains[check_idx].choose_refutation_card(matches)
                else:
                    # Human player - for now just first match (could be enhanced to ask)
                    shown_card = matches[0]
                shown_card_name = shown_card.name
                
                if suggester.is_computer:
                    print(f"  (Card shown privately to AI {suggester.character_name})")
                    suggester.eliminate_card(shown_card)
                    # Update AI's knowledge: the refuter has this card
                    if suggester_idx in self.ai_brains:
                        # Ensure tracking exists
                        if refuter_name not in suggester.known_player_cards:
                            suggester.known_player_cards[refuter_name] = set()
                        suggester.known_player_cards[refuter_name].add(shown_card_name)
                else:
                    # Human View
                    print(f"  --> {checker_color}{checker.character_name}{Colors.RESET} shows you: {Colors.CYAN}{shown_card.name}{Colors.RESET}")
                    suggester.eliminate_card(shown_card)
                
                break 
            else:
                pass # Silent pass

        if not refutation_made:
            print(f"{Colors.BOLD}No one could refute the suggestion!{Colors.RESET}")
            # If no one refuted and suggester is AI, update knowledge
            if suggester.is_computer and suggester_idx in self.ai_brains:
                # All other players don't have any of these cards
                for player in self.players:
                    if player.character_name != suggester.character_name:
                        # Ensure tracking exists
                        if player.character_name not in suggester.known_player_not_cards:
                            suggester.known_player_not_cards[player.character_name] = set()
                        for card_name in suggestion_dict.values():
                            suggester.known_player_not_cards[player.character_name].add(card_name)
        
        # Notify all AI players (except the suggester) about this suggestion and refutation
        for idx, ai_brain in self.ai_brains.items():
            if idx != suggester_idx:
                ai_brain.observe_suggestion(
                    suggester.character_name,
                    suggestion_dict,
                    refuter_name,
                    shown_card_name,
                    self.players
                )
        
        # Record in suggester's history if they're AI and update their knowledge
        if suggester.is_computer and suggester_idx in self.ai_brains:
            suggester.suggestion_history.append((
                suggester.character_name,
                suggestion_dict,
                refuter_name,
                shown_card_name
            ))
            # Perform inference after recording
            self.ai_brains[suggester_idx].perform_inference()

    def handle_movement(self, player, roll):
        current_idx = self.players.index(player)
        curr_room = self.board.get_room_name(player.position)
        
        # Secret Passage
        if curr_room in SECRET_PASSAGES:
            target = SECRET_PASSAGES[curr_room]
            target_name = self.board.get_room_name(target)
            
            take_passage = False
            if player.is_computer:
                if random.choice([True, False]): take_passage = True
            else:
                choice = input(f"Secret Passage to {target_name}? (y/n): ")
                if choice.lower() == 'y': take_passage = True
            
            if take_passage:
                player.move(target)
                print(f"{player.character_name} took secret passage to {Colors.CYAN}{target_name}{Colors.RESET}!")
                return

        # Movement
        if player.is_computer:
            ai = self.ai_brains[current_idx]
            path = ai.decide_move(self.board, roll)
            if path:
                # Validate path length doesn't exceed roll (shouldn't happen, but safety check)
                if len(path) > roll:
                    path = path[:roll]  # Truncate to roll length
                
                end_pos = path[-1]
                player.move(end_pos)
                room_name = self.board.get_room_name(end_pos)
                loc_str = room_name if room_name else "Hallway"
                print(f"AI moved to {Colors.CYAN}{loc_str}{Colors.RESET}")
            else:
                print("AI stays put.")
        else:
            print(f"Moves allowed: {roll}")
            moves = input("Enter moves (e.g. U U L): ").upper().split()
            
            # --- FIX: Check length FIRST and stop immediately ---
            if len(moves) > roll:
                print(f"{Colors.RED}Too many steps! You only rolled {roll}.{Colors.RESET}")
                return # Stops function here. Does not proceed to wall check.
            
            # Simplified Validation
            curr = player.position
            valid = True
            
            for m in moves:
                r, c = curr
                if m == 'U': r-=1
                elif m == 'D': r+=1
                elif m == 'L': c-=1
                elif m == 'R': c+=1
                
                if not self.board.is_valid_move(curr, (r,c)):
                    print(f"{Colors.RED}Hit wall.{Colors.RESET}")
                    valid = False
                    break
                
                curr = (r,c)
                if self.board.is_room(curr) and curr != player.position: break
            
            if valid: player.move(curr)

    def play_turn(self):
        player = self.players[self.turn_index]
        
        if not player.active:
            self.turn_index = (self.turn_index + 1) % len(self.players)
            return

        p_color = get_player_color(player.character_name)
        
        # UI: Clear screen for human, separator for AI
        if not player.is_computer:
            print(f"\n{Colors.GREY}{'-'*50}{Colors.RESET}") 
            print_header(f"TURN: {p_color}{player.character_name}{Colors.RESET}")
            self.board.display_board(self.players)
            
            print(f"\n{Colors.BOLD}YOUR HAND:{Colors.RESET}")
            for c in player.hand:
                print(f" - {Colors.CYAN}{c.name}{Colors.RESET} ({c.card_type})")
        else:
            print(f"\n{Colors.GREY}{'-'*50}{Colors.RESET}")
            print(f"TURN: {p_color}{player.character_name}{Colors.RESET} (AI)")

        # 1. Accusation
        accuse_now, acc_details = False, None
        if player.is_computer:
            accuse_now, acc_details = self.ai_brains[self.turn_index].check_accusation_readiness()
        else:
            if input(f"{Colors.ORANGE}[Enter] to Roll, or 'A' to Accuse: {Colors.RESET}").lower() == 'a':
                accuse_now = True
        
        if accuse_now:
            if self.handle_accusation(player, acc_details): return
            self.turn_index = (self.turn_index + 1) % len(self.players)
            return

        # 2. Move
        roll = self.roll_dice()
        print(f"Rolled: {Colors.BOLD}{roll}{Colors.RESET}")
        self.handle_movement(player, roll)

        # 3. Suggestion
        if self.board.is_room(player.position):
            room_name = self.board.get_room_name(player.position)
            make_sugg = False
            s_c, s_w = None, None

            if player.is_computer:
                make_sugg = True
                s_c, s_w, _ = self.ai_brains[self.turn_index].pick_suggestion(room_name)
            else:
                if input(f"Make suggestion in {Colors.CYAN}{room_name}{Colors.RESET}? (y/n): ") == 'y':
                    make_sugg = True
                    s_c = input("Suspect: ")
                    s_w = input("Weapon: ")
            
            if make_sugg:
                print(f"Suggesting: {s_c}, {s_w}, {room_name}")
                # Drag logic
                for p in self.players:
                    if p.character_name.lower() == s_c.lower():
                        p.move(player.position)
                        print(f"** {p.character_name} dragged to {room_name} **")
                
                self.handle_refutation(self.turn_index, {"Character": s_c, "Weapon": s_w, "Room": room_name})

        self.turn_index = (self.turn_index + 1) % len(self.players)