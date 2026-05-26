import random
import sys
import pygame

pygame.init()

# Window Setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Text RPG Adventure")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
GREEN = (50, 205, 50)
RED = (220, 20, 60)

# Fonts
font_large = pygame.font.SysFont("Arial", 40)
font_medium = pygame.font.SysFont("Arial", 28)
font_small = pygame.font.SysFont("Arial", 20)

# --- Game State Variables ---
game_mode = "NORMAL"  # "NORMAL" or "ENDLESS"
stage = 1
health = 3
max_health = 3

# Inventory
weapons = 0
armor = 0
potions = 0

current_event = None
event_outcome_text = []  # Stores temporary message after an action

def calculate_success_chance():
    """Calculates success rate based on items: Base 50% + Weapons(10%) + Armor(5%) + Potions(5%)"""
    chance = 50 + (weapons * 10) + (armor * 5) + (potions * 5)
    return min(100, chance)  # Cap at 100%


def generate_event():
    """Generates a randomized stage event or a Boss fight every 5th stage."""
    global stage
    if stage % 5 == 0:
        return {
            "type": "boss",
            "text": [
                f"STAGE {stage}: BOSS BATTLE!",
                "An imposing boss blocks your passage.",
                "Defeating this foe completely restores your health!",
            ]
        }
    
    event_type = random.choice(["enemy", "trap", "loot", "miniboss"])
    
    if event_type == "enemy":
        return {
            "type": "enemy",
            "text": [
                f"STAGE {stage}: Enemy Encounter",
                "A dangerous creature lunges from the dark!",
                "Defeating it guarantees a new Weapon drop."
            ]
        }
    elif event_type == "trap":
        return {
            "type": "trap",
            "text": [
                f"STAGE {stage}: Deadly Trap",
                "Spikes and gears whirl ahead of you.",
                "Careful navigation is required to avoid taking damage."
            ]
        }
    elif event_type == "loot":
        return {
            "type": "loot",
            "text": [
                f"STAGE {stage}: Treasure Chest",
                "An ornate loot chest sits undisturbed.",
                "Opening it offers a very high chance of finding a Weapon."
            ]
        }
    elif event_type == "miniboss":
        return {
            "type": "miniboss",
            "text": [
                f"STAGE {stage}: Miniboss Room",
                "An elite vanguard challenges your presence.",
                "Victory guarantees a vital Health Potion."
            ]
        }


def reset_game(mode):
    """Resets all metrics when starting a new game."""
    global game_mode, stage, health, weapons, armor, potions, current_event, event_outcome_text
    game_mode = mode
    stage = 1
    health = 3
    weapons = 0
    armor = 0
    potions = 0
    event_outcome_text = ["You enter the dungeon... Ready your wits!"]
    current_event = generate_event()


def draw_bordered_box(surface, rect, lines, font, border_width=3, is_button=False, color_override=None):
    """Draws a white-bordered box with centered multiline text."""
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = is_button and rect.collidepoint(mouse_pos)
    
    color = color_override if color_override else (GRAY if is_hovered else WHITE)
    pygame.draw.rect(surface, color, rect, border_width)
    
    total_height = len(lines) * font.get_linesize()
    start_y = rect.y + (rect.height - total_height) // 2
    
    for i, line in enumerate(lines):
        text_surf = font.render(line, True, color)
        text_rect = text_surf.get_rect(centerx=rect.centerx, top=start_y + i * font.get_linesize())
        surface.blit(text_surf, text_rect)
        
    return is_hovered


def draw_hud():
    """Displays real-time stats and item tracking tracking on-screen."""
    # Top status bar text
    mode_str = f"Mode: {game_mode}"
    stage_str = f"Stage: {stage}/15" if game_mode == "NORMAL" else f"Stage: {stage} (Endless)"
    hp_str = f"HP: {'♥ ' * health}{'♡ ' * (max_health - health)}"
    
    hud_text = f"{mode_str}   |   {stage_str}   |   {hp_str}"
    hud_surf = font_medium.render(hud_text, True, WHITE)
    screen.blit(hud_surf, (50, 15))
    
    # Inventory Status
    inv_text = f"Weapons (+10%): {weapons}   |   Armor (+5%): {armor}   |   Potions (+5%): {potions}"
    inv_surf = font_small.render(inv_text, True, GRAY)
    screen.blit(inv_surf, (50, 50))
    
    # Success Rate Display
    chance = calculate_success_chance()
    chance_surf = font_medium.render(f"Success Chance: {chance}%", True, GREEN if chance >= 70 else WHITE)
    screen.blit(chance_surf, (50, 535))
    
    # Potion usage prompt
    if potions > 0 and health < max_health:
        prompt_surf = font_small.render("[Press 'P' to Use Potion (+1 HP)]", True, GREEN)
        screen.blit(prompt_surf, (520, 540))


def handle_event_action(action):
    """Handles the RNG outcome mechanics for choosing 'DO' or 'TRY ESCAPE'."""
    global stage, health, weapons, armor, potions, current_event, event_outcome_text
    
    if action == "ESCAPE":
        event_outcome_text = ["You successfully escaped, forfeiting all room rewards!"]
        stage += 1
        current_event = generate_event()
        return "EVENT_MENU"

    # Action is "DO" -> Roll RNG success check
    chance = calculate_success_chance()
    roll = random.randint(1, 100)
    
    if roll <= chance:
        # SUCCESS REWARDS
        if current_event["type"] == "boss":
            health = max_health
            event_outcome_text = ["BOSS DEFEATED! Your health has been completely restored!"]
        elif current_event["type"] == "enemy":
            weapons += 1
            event_outcome_text = ["Success! You defeated the enemy and claimed a new Weapon."]
        elif current_event["type"] == "trap":
            event_outcome_text = ["Success! You cleanly maneuvered past the trap without a scratch."]
        elif current_event["type"] == "loot":
            loot_roll = random.randint(1, 100)
            if loot_roll <= 70:
                weapons += 1
                event_outcome_text = ["Success! Opened the chest and pulled out a sharp Weapon!"]
            elif loot_roll <= 85:
                armor += 1
                event_outcome_text = ["Success! Opened the chest and equipped some defensive Armor."]
            else:
                potions += 1
                event_outcome_text = ["Success! Opened the chest and stowed away a Health Potion."]
        elif current_event["type"] == "miniboss":
            potions += 1
            event_outcome_text = ["Success! The Miniboss falls, dropping a vital Health Potion."]
            
        # Win-condition check for Normal Mode
        if game_mode == "NORMAL" and stage == 15:
            return "FINALE"
            
        stage += 1
        current_event = generate_event()
        return "EVENT_MENU"
    else:
        # FAILURE CONSEQUENCES
        health -= 1
        if current_event["type"] == "trap":
            event_outcome_text = ["Failed! The trap triggered and caught you. You took 1 damage!"]
        else:
            event_outcome_text = ["Failed! You lost the encounter and took 1 damage!"]
            
        if health <= 0:
            return "GAME_OVER"
            
        # Keep moving forward through the dungeon even on room failure
        if game_mode == "NORMAL" and stage == 15:
            return "FINALE"
            
        stage += 1
        current_event = generate_event()
        return "EVENT_MENU"


def main():
    # Application States: 'MAIN_MENU', 'EVENT_MENU', 'GAME_OVER', 'FINALE'
    state = 'MAIN_MENU'
    global event_outcome_text
    while True:
        screen.fill(BLACK)
        
        # --- 1. RENDER INTERFACES ---
        if state == 'MAIN_MENU':
            title_rect = pygame.Rect(200, 100, 400, 120)
            draw_bordered_box(screen, title_rect, ["DUNGEON RUNNER"], font_large)
            
            normal_rect = pygame.Rect(120, 380, 240, 100)
            hover_normal = draw_bordered_box(screen, normal_rect, ["NORMAL"], font_medium, is_button=True)
            
            endless_rect = pygame.Rect(440, 380, 240, 100)
            hover_endless = draw_bordered_box(screen, endless_rect, ["ENDLESS"], font_medium, is_button=True)
            
        elif state == 'EVENT_MENU':
            draw_hud()
            
            # Action Output Feedback Box (Displays what just occurred)
            feedback_rect = pygame.Rect(80, 90, 640, 60)
            draw_bordered_box(screen, feedback_rect, event_outcome_text, font_small, border_width=1, color_override=GRAY)
            
            # Event Description Box
            event_rect = pygame.Rect(80, 170, 640, 180)
            draw_bordered_box(screen, event_rect, current_event["text"], font_small, border_width=3)
            
            # DO Button
            do_rect = pygame.Rect(80, 390, 300, 110)
            hover_do = draw_bordered_box(screen, do_rect, ["ACT", "(IF FAIL TAKE DAMAGE)"], font_small, is_button=True)
            
            # TRY ESCAPE Button
            escape_rect = pygame.Rect(420, 390, 300, 110)
            hover_escape = draw_bordered_box(screen, escape_rect, ["TRY ESCAPE", "(FORFEIT REWARDS)"], font_small, is_button=True)
            
        elif state == 'GAME_OVER':
            rect_go = pygame.Rect(150, 150, 500, 150)
            draw_bordered_box(screen, rect_go, ["GAME OVER", f"You perished on Stage {stage}."], font_large, color_override=RED)
            
            btn_menu = pygame.Rect(280, 400, 240, 80)
            hover_menu = draw_bordered_box(screen, btn_menu, ["Return to Menu"], font_medium, is_button=True)
            
        elif state == 'FINALE':
            rect_win = pygame.Rect(150, 150, 500, 180)
            draw_bordered_box(screen, rect_win, ["VICTORY!", "You cleared Stage 15", "and escaped the deep dungeon!"], font_large, color_override=GREEN)
            
            btn_menu = pygame.Rect(280, 420, 240, 80)
            hover_menu = draw_bordered_box(screen, btn_menu, ["Return to Menu"], font_medium, is_button=True)

        # --- 2. EVENT & INPUT HANDLING ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.KEYDOWN:
                # Use Potion input mechanism
                if state == 'EVENT_MENU' and event.key == pygame.K_p:
                    global health, potions
                    if potions > 0 and health < max_health:
                        potions -= 1
                        health += 1
                        event_outcome_text = ["Sip! You consumed a Health Potion and healed 1 HP."]
                        
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state == 'MAIN_MENU':
                    if hover_normal:
                        reset_game("NORMAL")
                        state = 'EVENT_MENU'
                    elif hover_endless:
                        reset_game("ENDLESS")
                        state = 'EVENT_MENU'
                        
                elif state == 'EVENT_MENU':
                    if hover_do:
                        state = handle_event_action("DO")
                    elif hover_escape:
                        state = handle_event_action("ESCAPE")
                        
                elif state in ['GAME_OVER', 'FINALE']:
                    if hover_menu:
                        state = 'MAIN_MENU'
                        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
