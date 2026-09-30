"""
game_engine.py
--------------
Core logic and rendering for the Number Guessing Arena.

Task 1: Empty-input validation in submit_guess() (no crash, no attempt counted).
Task 2: Dynamic range hints (low_bound / high_bound tracked and shown on screen).
"""

import random
import pygame
from game.text_box import TextBox


class GameEngine:
    # ------------------------------------------------------------------
    # SECTION 1: INITIALIZATION
    # ------------------------------------------------------------------
    def __init__(self, width, height):
        # Window dimensions (used for centering UI elements)
        self.width = width
        self.height = height

        # Core game state
        self.secret_number = random.randint(1, 100)
        self.attempts = 0
        self.feedback_msg = "Enter a number between 1 and 100"
        self.feedback_color = (220, 220, 220)
        self.game_won = False

        # TASK 2: Dynamic range hint state.
        # The secret number always lies within [low_bound, high_bound].
        # These tighten after every valid guess.
        self.low_bound = 1
        self.high_bound = 100

        # UI elements
        self.input_box = TextBox(width // 2 - 110, 150, 120, 48)
        self.submit_btn = pygame.Rect(width // 2 + 25, 150, 100, 48)

        # Fonts
        self.font_title = pygame.font.SysFont(None, 42)
        self.font_medium = pygame.font.SysFont(None, 28)
        self.font_btn = pygame.font.SysFont(None, 26)

    # ------------------------------------------------------------------
    # SECTION 2: GAME LOGIC
    # ------------------------------------------------------------------
    def submit_guess(self):
        """Validate the typed guess, compare it to the secret, update state."""
        if self.game_won:
            return

        # TASK 1: Validate before converting. An empty box cannot be parsed
        # by int(). Return early so no attempt is counted and the player
        # gets feedback instead of a crash.
        raw_text = self.input_box.text.strip()
        if not raw_text:
            self.feedback_msg = "Please enter a valid number first!"
            self.feedback_color = (240, 200, 60)
            return

        guess = int(raw_text)

        self.attempts += 1
        self.input_box.clear()

        if guess < self.secret_number:
            self.feedback_msg = f"TOO LOW! (Guess was {guess})"
            self.feedback_color = (80, 160, 240)
            # TASK 2: A too-low guess becomes the new lower bound.
            # max() ensures the range never widens if the player guesses
            # a number that is already outside the known range.
            self.low_bound = max(self.low_bound, guess)
        elif guess > self.secret_number:
            self.feedback_msg = f"TOO HIGH! (Guess was {guess})"
            self.feedback_color = (240, 100, 80)
            # TASK 2: A too-high guess becomes the new upper bound.
            # min() ensures the range never widens either.
            self.high_bound = min(self.high_bound, guess)
        else:
            self.feedback_msg = f"CORRECT! Found in {self.attempts} attempts."
            self.feedback_color = (80, 220, 90)
            self.game_won = True

    def reset(self):
        """Start a fresh round: new secret number and cleared state."""
        self.secret_number = random.randint(1, 100)
        self.attempts = 0
        self.feedback_msg = "Enter a number between 1 and 100"
        self.feedback_color = (220, 220, 220)
        self.game_won = False
        # TASK 2: Restore the full range for the new round.
        self.low_bound = 1
        self.high_bound = 100
        self.input_box.clear()

    # ------------------------------------------------------------------
    # SECTION 3: EVENT HANDLING AND UPDATE LOOP
    # ------------------------------------------------------------------
    def handle_event(self, event):
        self.input_box.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.submit_guess()
            elif event.key == pygame.K_r and self.game_won:
                self.reset()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.submit_btn.collidepoint(event.pos):
                self.submit_guess()

    def update(self):
        pass

    # ------------------------------------------------------------------
    # SECTION 4: RENDERING
    # ------------------------------------------------------------------
    def render(self, screen):
        screen.fill((30, 34, 42))

        # Title
        title_surf = self.font_title.render("Number Guessing Arena", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 35))

        # Attempts counter
        attempts_surf = self.font_medium.render(f"Attempts: {self.attempts}", True, (180, 185, 195))
        screen.blit(attempts_surf, (self.width // 2 - attempts_surf.get_width() // 2, 95))

        # Input box
        self.input_box.render(screen)

        # Submit button
        pygame.draw.rect(screen, (50, 150, 80), self.submit_btn, border_radius=6)
        pygame.draw.rect(screen, (220, 220, 220), self.submit_btn, width=2, border_radius=6)
        btn_text = self.font_btn.render("SUBMIT", True, (255, 255, 255))
        screen.blit(
            btn_text,
            (self.submit_btn.centerx - btn_text.get_width() // 2, self.submit_btn.centery - btn_text.get_height() // 2),
        )

        # Feedback message (too low / too high / correct / invalid input)
        feedback_surf = self.font_medium.render(self.feedback_msg, True, self.feedback_color)
        screen.blit(feedback_surf, (self.width // 2 - feedback_surf.get_width() // 2, 235))

        # TASK 2: Current possible range hint, shown below the feedback message
        range_surf = self.font_medium.render(
            f"Current Possible Range: {self.low_bound} - {self.high_bound}", True, (200, 205, 215)
        )
        screen.blit(range_surf, (self.width // 2 - range_surf.get_width() // 2, 265))

        # Restart prompt (only after winning)
        if self.game_won:
            restart_surf = self.font_medium.render("Press [R] to Start a New Game", True, (255, 220, 80))
            screen.blit(restart_surf, (self.width // 2 - restart_surf.get_width() // 2, 305))