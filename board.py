# board.py
from config import *
from ui import Colors

class Board:
    def __init__(self):
        self.grid_size = GRID_SIZE
        self.rooms = ROOM_COORDINATES
        self.passages = SECRET_PASSAGES

    def is_room(self, pos):
        return pos in self.rooms

    def get_room_name(self, pos):
        return self.rooms.get(pos)

    def is_valid_move(self, current_pos, target_pos):
        r, c = target_pos
        return 0 <= r < self.grid_size and 0 <= c < self.grid_size

    def get_valid_neighbors(self, pos):
        r, c = pos
        candidates = [(r-1,c), (r+1,c), (r,c-1), (r,c+1)]
        return [cand for cand in candidates if self.is_valid_move(pos, cand)]

    def display_board(self, players):
        print(f"\n{Colors.BOLD}      --- MANSION MAP ---{Colors.RESET}")
        
        # Top Border
        print("    " + "+-----" * self.grid_size + "+")

        for r in range(self.grid_size):
            # Row Content
            row_str = "    "
            for c in range(self.grid_size):
                pos = (r, c)
                
                # Check for Players
                players_here = [p for p in players if p.position == pos and p.active]
                
                if players_here:
                    # Show all players at this position
                    # Get all player initials with their colors
                    if len(players_here) == 1:
                        # Single player - show with color
                        p = players_here[0]
                        p_char = p.character_name[0]
                        # Specific overrides for clarity
                        if "Scarlett" in p.character_name: p_char = "S"
                        elif "Mustard" in p.character_name: p_char = "M"
                        elif "White" in p.character_name: p_char = "W"
                        elif "Green" in p.character_name: p_char = "G"
                        elif "Peacock" in p.character_name: p_char = "C" # C for peaCock
                        elif "Plum" in p.character_name: p_char = "P"
                        color = self._get_p_color(p.character_name)
                        cell_content = f"  {color}{Colors.BOLD}{p_char}{Colors.RESET}  "
                    else:
                        # Multiple players - show all initials with their individual colors
                        # Build colored string for each character
                        colored_parts = []
                        plain_chars = []
                        
                        for p in players_here[:4]:  # Limit to 4 to fit in cell
                            p_char = p.character_name[0]
                            # Specific overrides for clarity
                            if "Scarlett" in p.character_name: p_char = "S"
                            elif "Mustard" in p.character_name: p_char = "M"
                            elif "White" in p.character_name: p_char = "W"
                            elif "Green" in p.character_name: p_char = "G"
                            elif "Peacock" in p.character_name: p_char = "C"
                            elif "Plum" in p.character_name: p_char = "P"
                            
                            color = self._get_p_color(p.character_name)
                            colored_parts.append(f"{color}{Colors.BOLD}{p_char}{Colors.RESET}")
                            plain_chars.append(p_char)
                        
                        # Combine colored characters
                        combined_colored = "".join(colored_parts)
                        
                        if len(players_here) > 4:
                            # More than 4 players - show first 2 with colors, then count
                            display_str = "".join(plain_chars[:2]) + str(len(players_here))
                            # But we want colors for the first 2
                            colored_display = "".join(colored_parts[:2]) + str(len(players_here))
                            # Pad based on visible length
                            visible_len = len(display_str)
                            padding = " " * (4 - visible_len) if visible_len < 4 else ""
                            cell_content = f" {colored_display}{padding}"
                        else:
                            # 2-4 players - show all with colors
                            # Pad based on number of visible characters
                            visible_len = len(plain_chars)
                            padding = " " * (4 - visible_len) if visible_len < 4 else ""
                            cell_content = f" {combined_colored}{padding}"
                
                elif pos in self.rooms:
                    # Room Label (First 3 chars)
                    room_name = self.rooms[pos]
                    short_name = room_name[:3].upper()
                    cell_content = f"{Colors.CYAN} {short_name} {Colors.RESET}"
                else:
                    cell_content = f"{Colors.GREY}  .  {Colors.RESET}"

                row_str += f"|{cell_content}"
            print(row_str + "|")
            
            # Row Border
            print("    " + "+-----" * self.grid_size + "+")
            
        # Player Key
        print(f"{Colors.GREY}Players: {Colors.RED}S{Colors.RESET}=Scarlett, {Colors.YELLOW}M{Colors.RESET}=Mustard, {Colors.WHITE}W{Colors.RESET}=White, {Colors.GREEN}G{Colors.RESET}=Green, {Colors.BLUE}C{Colors.RESET}=Peacock, {Colors.MAGENTA}P{Colors.RESET}=Plum")
        
        # Room Key (Dynamic Generation)
        # Get unique room names, sort them, and format nicely
        unique_rooms = sorted(list(set(self.rooms.values())))
        # Break into two lines if needed, or join all
        room_legend = ", ".join([f"{Colors.CYAN}{r[:3].upper()}{Colors.RESET}={r}" for r in unique_rooms])
        print(f"{Colors.GREY}Rooms:   {room_legend}{Colors.RESET}")

    def _get_p_color(self, name):
        if "Scarlett" in name: return Colors.RED
        if "Mustard" in name: return Colors.YELLOW
        if "White" in name: return Colors.WHITE
        if "Green" in name: return Colors.GREEN
        if "Peacock" in name: return Colors.BLUE
        if "Plum" in name: return Colors.MAGENTA
        return Colors.RESET