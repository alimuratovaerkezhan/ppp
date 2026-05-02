import pygame
import sys
from ui import (
    show_main_menu, show_username_input, show_leaderboard_screen,
    show_settings_screen, show_game_over_screen
)
from racer import run_game
from persistence import load_settings, add_score_to_leaderboard

pygame.init()

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 700

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("RACER GAME - Advanced")

def main():
    settings = load_settings()
    player_name = None
    
    while True:
        menu_choice = show_main_menu(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        if menu_choice == "quit":
            pygame.quit()
            sys.exit()
        
        elif menu_choice == "play":
            if player_name is None:
                player_name = show_username_input(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
                if player_name is None:
                    continue
            
            result, (score, distance, coins) = run_game(settings)
            
            if result == "game_over":
                game_over_choice = show_game_over_screen(
                    screen, SCREEN_WIDTH, SCREEN_HEIGHT, score, distance, coins
                )
                add_score_to_leaderboard(player_name, score, distance, coins)
                
                if game_over_choice == "quit":
                    pygame.quit()
                    sys.exit()
                elif game_over_choice == "menu":
                    continue
                elif game_over_choice == "retry":
                    continue
            
            elif result == "quit":
                pygame.quit()
                sys.exit()
        
        elif menu_choice == "leaderboard":
            show_leaderboard_screen(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        elif menu_choice == "settings":
            show_settings_screen(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
            settings = load_settings()

if __name__ == "__main__":
    print("\n" + "="*50)
    print("RACER GAME - ADVANCED")
    print("="*50)
    print("Features:")
    print("  - Lane hazards (oil spills, potholes, barriers, cones)")
    print("  - Dynamic road events (speed boosts, slow zones)")
    print("  - Power-ups: Nitro, Shield, Repair")
    print("  - Difficulty scaling as you progress")
    print("  - Persistent leaderboard (top 10 scores)")
    print("  - Settings: Sound toggle, Car color, Difficulty")
    print("  - SOUND EFFECTS: Coin pickup, Power-up, Crash")
    print("="*50)
    print("Controls: Left/Right arrows to move")
    print("="*50 + "\n")
    
    main()