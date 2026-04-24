# main.py
from game_logic import ClueGame

def main():
    game = ClueGame()

    while game.running:
        try:
            game.play_turn()
            
            # Check for total elimination (Optional end condition)
            active_count = sum(1 for p in game.players if p.active)
            if active_count == 0:
                print("All players eliminated. Game Over.")
                game.running = False
                
        except KeyboardInterrupt:
            print("\nGame Exited.")
            break

if __name__ == "__main__":
    main()