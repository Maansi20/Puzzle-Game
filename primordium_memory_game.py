import pygame
import random
import sys
import time
import math
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Game Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CARD_WIDTH = 100
CARD_HEIGHT = 100
GRID_SIZE = 4  # 4x4 grid
MARGIN = 10
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
CARD_BACK = (70, 30, 100)  # Dark purple for card backs
CARD_FRONT = (30, 70, 100)  # Dark blue for card fronts
MATCHED_COLOR = (30, 100, 30)  # Dark green for matched cards
PRIMORDIUM_PURPLE = (128, 0, 128)
PRIMORDIUM_BLUE = (0, 0, 128)
PRIMORDIUM_GREEN = (0, 128, 0)

# Set up the window
DISPLAY_SURFACE = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Primordium Memory Game')
CLOCK = pygame.time.Clock()

# Font setup
FONT = pygame.font.SysFont('Arial', 32)
SMALL_FONT = pygame.font.SysFont('Arial', 24)

# Primordium-themed symbols (using simple shapes and colors as placeholders for images)
PRIMORDIUM_SYMBOLS = [
    {"shape": "circle", "color": (255, 0, 0)},
    {"shape": "square", "color": (0, 255, 0)},
    {"shape": "triangle", "color": (0, 0, 255)},
    {"shape": "diamond", "color": (255, 255, 0)},
    {"shape": "star", "color": (255, 0, 255)},
    {"shape": "cross", "color": (0, 255, 255)},
    {"shape": "hexagon", "color": (128, 128, 0)},
    {"shape": "octagon", "color": (0, 128, 128)},
]

class Card:
    def __init__(self, x, y, symbol):
        self.x = x
        self.y = y
        self.symbol = symbol
        self.width = CARD_WIDTH
        self.height = CARD_HEIGHT
        self.is_flipped = False
        self.is_matched = False
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
    
    def draw(self):
        if self.is_matched:
            pygame.draw.rect(DISPLAY_SURFACE, MATCHED_COLOR, self.rect)
            self.draw_symbol()
        elif self.is_flipped:
            pygame.draw.rect(DISPLAY_SURFACE, CARD_FRONT, self.rect)
            self.draw_symbol()
        else:
            pygame.draw.rect(DISPLAY_SURFACE, CARD_BACK, self.rect)
        
        # Draw border
        pygame.draw.rect(DISPLAY_SURFACE, BLACK, self.rect, 2)
    
    def draw_symbol(self):
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        if self.symbol["shape"] == "circle":
            pygame.draw.circle(DISPLAY_SURFACE, self.symbol["color"], (center_x, center_y), 30)
        elif self.symbol["shape"] == "square":
            rect = pygame.Rect(center_x - 25, center_y - 25, 50, 50)
            pygame.draw.rect(DISPLAY_SURFACE, self.symbol["color"], rect)
        elif self.symbol["shape"] == "triangle":
            points = [(center_x, center_y - 30), (center_x - 30, center_y + 20), (center_x + 30, center_y + 20)]
            pygame.draw.polygon(DISPLAY_SURFACE, self.symbol["color"], points)
        elif self.symbol["shape"] == "diamond":
            points = [(center_x, center_y - 30), (center_x + 30, center_y), (center_x, center_y + 30), (center_x - 30, center_y)]
            pygame.draw.polygon(DISPLAY_SURFACE, self.symbol["color"], points)
        elif self.symbol["shape"] == "star":
            # Simple star representation
            pygame.draw.circle(DISPLAY_SURFACE, self.symbol["color"], (center_x, center_y), 25)
            pygame.draw.rect(DISPLAY_SURFACE, self.symbol["color"], (center_x - 5, center_y - 30, 10, 60))
            pygame.draw.rect(DISPLAY_SURFACE, self.symbol["color"], (center_x - 30, center_y - 5, 60, 10))
        elif self.symbol["shape"] == "cross":
            pygame.draw.rect(DISPLAY_SURFACE, self.symbol["color"], (center_x - 25, center_y - 5, 50, 10))
            pygame.draw.rect(DISPLAY_SURFACE, self.symbol["color"], (center_x - 5, center_y - 25, 10, 50))
        elif self.symbol["shape"] == "hexagon":
            radius = 30
            points = []
            for i in range(6):
                angle = i * (2 * 3.14159 / 6)
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                points.append((x, y))
            pygame.draw.polygon(DISPLAY_SURFACE, self.symbol["color"], points)
        elif self.symbol["shape"] == "octagon":
            radius = 30
            points = []
            for i in range(8):
                angle = i * (2 * 3.14159 / 8)
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                points.append((x, y))
            pygame.draw.polygon(DISPLAY_SURFACE, self.symbol["color"], points)
    
    def flip(self):
        if not self.is_matched and not self.is_flipped:
            self.is_flipped = True
            return True
        return False

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(DISPLAY_SURFACE, color, self.rect)
        pygame.draw.rect(DISPLAY_SURFACE, BLACK, self.rect, 2)
        
        text_surface = SMALL_FONT.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        DISPLAY_SURFACE.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Game:
    def __init__(self):
        self.reset_game()
        
    def reset_game(self):
        self.cards = []
        self.first_selection = None
        self.second_selection = None
        self.current_player = 1
        self.player1_score = 0
        self.player2_score = 0
        self.waiting_time = 0
        self.game_over = False
        self.create_board()
        
        # Create buttons
        self.play_again_button = Button(
            WINDOW_WIDTH // 2 - 100, 
            WINDOW_HEIGHT - 80, 
            200, 50, 
            "Play Again", 
            PRIMORDIUM_GREEN, 
            (100, 200, 100)
        )
        
        self.exit_button = Button(
            WINDOW_WIDTH // 2 - 100, 
            WINDOW_HEIGHT - 150, 
            200, 50, 
            "Exit Game", 
            PRIMORDIUM_PURPLE, 
            (200, 100, 200)
        )
        
    def create_board(self):
        # Create pairs of cards with matching symbols
        symbols = PRIMORDIUM_SYMBOLS[:8]  # Use 8 symbols for 16 cards (8 pairs)
        card_symbols = symbols * 2  # Duplicate each symbol to create pairs
        random.shuffle(card_symbols)
        
        # Calculate grid layout
        total_width = GRID_SIZE * (CARD_WIDTH + MARGIN) - MARGIN
        total_height = GRID_SIZE * (CARD_HEIGHT + MARGIN) - MARGIN
        start_x = (WINDOW_WIDTH - total_width) // 2
        start_y = (WINDOW_HEIGHT - total_height) // 2
        
        # Create cards in a grid
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = start_x + col * (CARD_WIDTH + MARGIN)
                y = start_y + row * (CARD_HEIGHT + MARGIN)
                index = row * GRID_SIZE + col
                self.cards.append(Card(x, y, card_symbols[index]))
    
    def handle_click(self, pos):
        if self.waiting_time > 0 or self.game_over:
            return
            
        # Check if any card was clicked
        for card in self.cards:
            if card.rect.collidepoint(pos):
                if self.first_selection is None and card.flip():
                    self.first_selection = card
                elif self.second_selection is None and card != self.first_selection and card.flip():
                    self.second_selection = card
                    self.waiting_time = FPS  # Wait for 1 second
                break
    
    def update(self):
        if self.waiting_time > 0:
            self.waiting_time -= 1
            
            if self.waiting_time == 0:
                # Check if the cards match
                if (self.first_selection.symbol["shape"] == self.second_selection.symbol["shape"] and
                    self.first_selection.symbol["color"] == self.second_selection.symbol["color"]):
                    self.first_selection.is_matched = True
                    self.second_selection.is_matched = True
                    
                    # Update score
                    if self.current_player == 1:
                        self.player1_score += 1
                    else:
                        self.player2_score += 1
                else:
                    self.first_selection.is_flipped = False
                    self.second_selection.is_flipped = False
                    # Switch player turn
                    self.current_player = 3 - self.current_player  # Toggle between 1 and 2
                
                self.first_selection = None
                self.second_selection = None
                
        # Check if all cards are matched
        all_matched = all(card.is_matched for card in self.cards)
        if all_matched and not self.game_over:
            self.game_over = True
    
    def draw(self):
        DISPLAY_SURFACE.fill(DARK_GRAY)
        
        # Draw cards
        for card in self.cards:
            card.draw()
        
        # Draw scores and current player
        player1_text = f"Player 1: {self.player1_score}"
        player2_text = f"Player 2: {self.player2_score}"
        
        player1_surface = SMALL_FONT.render(player1_text, True, WHITE)
        player2_surface = SMALL_FONT.render(player2_text, True, WHITE)
        
        DISPLAY_SURFACE.blit(player1_surface, (20, 20))
        DISPLAY_SURFACE.blit(player2_surface, (WINDOW_WIDTH - player2_surface.get_width() - 20, 20))
        
        # Highlight current player
        if self.current_player == 1:
            pygame.draw.rect(DISPLAY_SURFACE, PRIMORDIUM_PURPLE, (15, 15, player1_surface.get_width() + 10, player1_surface.get_height() + 10), 2)
        else:
            pygame.draw.rect(DISPLAY_SURFACE, PRIMORDIUM_PURPLE, (WINDOW_WIDTH - player2_surface.get_width() - 25, 15, player2_surface.get_width() + 10, player2_surface.get_height() + 10), 2)
        
        # Draw game over message
        if self.game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Semi-transparent black
            DISPLAY_SURFACE.blit(overlay, (0, 0))
            
            if self.player1_score > self.player2_score:
                winner_text = "Player 1 Wins!"
            elif self.player2_score > self.player1_score:
                winner_text = "Player 2 Wins!"
            else:
                winner_text = "It's a Tie!"
                
            game_over_text = "Game Over!"
            
            game_over_surface = FONT.render(game_over_text, True, WHITE)
            winner_surface = FONT.render(winner_text, True, WHITE)
            
            DISPLAY_SURFACE.blit(game_over_surface, (WINDOW_WIDTH // 2 - game_over_surface.get_width() // 2, WINDOW_HEIGHT // 2 - 80))
            DISPLAY_SURFACE.blit(winner_surface, (WINDOW_WIDTH // 2 - winner_surface.get_width() // 2, WINDOW_HEIGHT // 2 - 30))
            
            # Draw buttons
            self.play_again_button.draw()
            self.exit_button.draw()

def main():
    game = Game()
    
    # Main game loop
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if game.game_over:
                    if game.play_again_button.is_clicked(mouse_pos):
                        game.reset_game()
                    elif game.exit_button.is_clicked(mouse_pos):
                        pygame.quit()
                        sys.exit()
                else:
                    game.handle_click(mouse_pos)
        
        # Update button hover states
        if game.game_over:
            game.play_again_button.check_hover(mouse_pos)
            game.exit_button.check_hover(mouse_pos)
        
        # Update game state
        game.update()
        
        # Draw everything
        game.draw()
        
        pygame.display.update()
        CLOCK.tick(FPS)

if __name__ == "__main__":
    main()
