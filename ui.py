# ui.py
import os

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    
    # Text Colors
    RED = "\033[91m"      # Miss Scarlett
    YELLOW = "\033[93m"   # Col. Mustard
    WHITE = "\033[97m"    # Mrs. White
    GREEN = "\033[92m"    # Rev. Green
    BLUE = "\033[94m"     # Mrs. Peacock
    MAGENTA = "\033[95m"  # Prof. Plum
    
    CYAN = "\033[96m"     # UI Elements / Rooms
    GREY = "\033[90m"     # Empty Spaces
    ORANGE = "\033[33m"   # Highlights

def clear_screen():
    """Clears the console for a fresh turn view."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(text):
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*40}")
    print(f" {text.center(38)} ")
    print(f"{'='*40}{Colors.RESET}")

def get_player_color(name):
    if "Scarlett" in name: return Colors.RED
    if "Mustard" in name: return Colors.YELLOW
    if "White" in name: return Colors.WHITE
    if "Green" in name: return Colors.GREEN
    if "Peacock" in name: return Colors.BLUE
    if "Plum" in name: return Colors.MAGENTA
    return Colors.RESET