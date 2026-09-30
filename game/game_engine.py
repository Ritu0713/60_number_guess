"""
game_engine.py
--------------
Core logic and rendering for the Number Guessing Arena.

Task 1: Empty-input validation in submit_guess() (no crash, no attempt counted).
Task 2: Dynamic range hints (low_bound / high_bound tracked and shown on screen).
Task 3: Attempt history panel (last 5 guesses with coloured arrow + HIGH/LOW tag).
Task 4: Maximum attempts (7) and GAME OVER state that reveals the secret number.
"""

import random
import pygame
from game.text_box import TextBox

# ----------------------------------------------------------------------
# CONSTANTS
# ----------------------------------------------------------------------
MAX_ATTEMPTS = 7        # TASK 4: valid guesses allowed per round
HISTORY_LIMIT = 5       # TASK 3: how many recent guesses are displayed

# Colours reused for feedback text and history tags so the UI stays consistent
COLOR_LOW = (80, 160, 240)      # blue  -> guess was too low
COLOR_HIGH = (240, 100, 80)     # red   -> guess was too high
COLOR_WIN = (80, 220, 90)       # green -> correct


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

        # TASK 4: True once the player has used all MAX_ATTEMPTS without winning
        self.game_over = False

        # TASK 2: Dynamic range hint state.
        # The secret number always lies within [low_bound, high_bound].
        self.low_bound = 1
        self.high_bound = 100

        # TASK 3: Every valid guess is stored as (guess, result) where result
        # is "LOW", "HIGH" or "HIT". Only the last HISTORY_LIMIT are drawn.
        self.guess_history = []

        # UI elements
        self.input_box = TextBox(width // 2 - 110, 150, 120, 48)
        self.submit_btn = pygame.Rect(width // 2 + 25, 150, 100, 48)

        # TASK 3: History panel sits on the right, clear of the centred text
        self.history_rect = pygame.Rect(width - 140, 90, 130, 170)

        # Fonts
        self.font_title = pygame.font.SysFont(None, 42)
        self.font_medium = pygame.font.SysFont(None, 28)
        self.font_btn = pygame.font.SysFont(None, 26)
        self.font_small = pygame.font.SysFont(None, 22)  # TASK 3: history rows

    # ------------------------------------------------------------------
    # SECTION 2: GAME LOGIC
    # ------------------------------------------------------------------
    def submit_guess(self):
        """Validate the typed guess, compare it to the secret, update state."""
        # TASK 4: Ignore input once the round has ended (won or game over)
        if self.game_won or self.game_over:
            return

        # TASK 1 (also covers Task 4 req. 6): An empty box cannot be parsed
        # by int(). Return early so NO attempt is counted and the player
        # gets feedback instead of a crash.
        raw_text = self.input_box.text.strip()
        if not raw_text:
            self.feedback_msg = "Please enter a valid number first!"
            self.feedback_color = (240, 200, 60)
            return

        guess = int(raw_text)

        # From here on the guess is valid, so it counts as an attempt
        self.attempts += 1
        self.input_box.clear()

        if guess < self.secret_number:
            self.feedback_msg = f"TOO LOW! (Guess was {guess})"
            self.feedback_color = COLOR_LOW
            # TASK 2: max() keeps the range from ever widening
            self.low_bound = max(self.low_bound, guess)
            self.guess_history.append((guess, "LOW"))       # TASK 3
        elif guess > self.secret_number:
            self.feedback_msg = f"TOO HIGH! (Guess was {guess})"
            self.feedback_color = COLOR_HIGH
            # TASK 2: min() keeps the range from ever widening
            self.high_bound = min(self.high_bound, guess)
            self.guess_history.append((guess, "HIGH"))      # TASK 3
        else:
            self.feedback_msg = f"CORRECT! Found in {self.attempts} attempts."
            self.feedback_color = COLOR_WIN
            self.game_won = True
            self.guess_history.append((guess, "HIT"))       # TASK 3

        # TASK 4: Out of attempts without a win -> GAME OVER.
        # Checked AFTER the comparison so a correct 7th guess still wins.
        if not self.game_won and self.attempts >= MAX_ATTEMPTS:
            self.game_over = True
            self.feedback_msg = f"GAME OVER! The number was {self.secret_number}"
            self.feedback_color = COLOR_HIGH

    def reset(self):
        """Start a fresh round: new secret number and fully cleared state."""
        self.secret_number = random.randint(1, 100)
        self.attempts = 0
        self.feedback_msg = "Enter a number between 1 and 100"
        self.feedback_color = (220, 220, 220)
        self.game_won = False
        self.game_over = False              # TASK 4
        self.low_bound = 1                  # TASK 2
        self.high_bound = 100               # TASK 2
        self.guess_history = []             # TASK 3
        self.input_box.clear()

    # ------------------------------------------------------------------
    # SECTION 3: EVENT HANDLING AND UPDATE LOOP
    # ------------------------------------------------------------------
    def handle_event(self, event):
        self.input_box.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.submit_guess()
            # TASK 4: R restarts after either a win or a game over
            elif event.key == pygame.K_r and (self.game_won or self.game_over):
                self.reset()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.submit_btn.collidepoint(event.pos):
                self.submit_guess()

    def update(self):
        pass

    # ------------------------------------------------------------------
    # SECTION 4: RENDERING
    # ------------------------------------------------------------------
    def render_history(self, screen):
        """TASK 3: Draw the last HISTORY_LIMIT guesses in a small side panel."""
        panel = self.history_rect
        pygame.draw.rect(screen, (40, 45, 56), panel, border_radius=6)
        pygame.draw.rect(screen, (90, 95, 110), panel, width=1, border_radius=6)

        header = self.font_small.render("HISTORY", True, (180, 185, 195))
        screen.blit(header, (panel.x + 10, panel.y + 8))

        if not self.guess_history:
            empty = self.font_small.render("No guesses yet", True, (120, 125, 135))
            screen.blit(empty, (panel.x + 10, panel.y + 40))
            return

        # Slice the most recent guesses; keep their real attempt numbers
        recent = self.guess_history[-HISTORY_LIMIT:]
        first_number = len(self.guess_history) - len(recent) + 1

        for i, (guess, result) in enumerate(recent):
            row_y = panel.y + 34 + i * 26
            x0 = panel.x + 10

            # Attempt number and guessed value
            num_surf = self.font_small.render(f"#{first_number + i}", True, (140, 145, 155))
            guess_surf = self.font_small.render(str(guess), True, (235, 235, 240))
            screen.blit(num_surf, (x0, row_y + 3))
            screen.blit(guess_surf, (x0 + 26, row_y + 3))

            # Arrow shows which way the next guess should go:
            # LOW -> up (blue), HIGH -> down (red), HIT -> green dot
            cx, cy = x0 + 66, row_y + 10
            if result == "LOW":
                color, label = COLOR_LOW, "LOW"
                pygame.draw.polygon(screen, color, [(cx, cy - 6), (cx - 6, cy + 5), (cx + 6, cy + 5)])
            elif result == "HIGH":
                color, label = COLOR_HIGH, "HIGH"
                pygame.draw.polygon(screen, color, [(cx, cy + 6), (cx - 6, cy - 5), (cx + 6, cy - 5)])
            else:
                color, label = COLOR_WIN, "HIT"
                pygame.draw.circle(screen, color, (cx, cy), 5)

            tag_surf = self.font_small.render(label, True, color)
            screen.blit(tag_surf, (x0 + 78, row_y + 3))

    def render(self, screen):
        screen.fill((30, 34, 42))

        # Title
        title_surf = self.font_title.render("Number Guessing Arena", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 35))

        # Attempts counter (TASK 4: now shows the limit, e.g. "3 / 7")
        attempts_surf = self.font_medium.render(
            f"Attempts: {self.attempts} / {MAX_ATTEMPTS}", True, (180, 185, 195)
        )
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

        # Feedback message (too low / too high / correct / invalid / game over)
        feedback_surf = self.font_medium.render(self.feedback_msg, True, self.feedback_color)
        screen.blit(feedback_surf, (self.width // 2 - feedback_surf.get_width() // 2, 235))

        # TASK 2: Current possible range hint
        range_surf = self.font_medium.render(
            f"Current Possible Range: {self.low_bound} - {self.high_bound}", True, (200, 205, 215)
        )
        screen.blit(range_surf, (self.width // 2 - range_surf.get_width() // 2, 265))

        # TASK 3: Attempt history panel
        self.render_history(screen)

        # Restart prompt: shown after a win OR a game over (TASK 4)
        if self.game_won or self.game_over:
            restart_surf = self.font_medium.render("Press [R] to Start a New Game", True, (255, 220, 80))
            screen.blit(restart_surf, (self.width // 2 - restart_surf.get_width() // 2, 305))