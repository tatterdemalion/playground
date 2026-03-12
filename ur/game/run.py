import os
import random
import time

from game.ur import Player, Engine, P1_PATH, P2_PATH


class BoardVisualizer:
    def __init__(self, engine: Engine):
        self.engine = engine

    def draw(self):
        # Clear screen for animation (works on Windows/Mac/Linux)
        os.system('cls' if os.name == 'nt' else 'clear')

        # Base 3x8 grid with empty brackets and Rosettas marked with *
        grid = [
            ["[*]", "[ ]", "[ ]", "[ ]", "   ", "   ", "[*]", "[ ]"],
            ["[ ]", "[ ]", "[ ]", "[*]", "[ ]", "[ ]", "[ ]", "[ ]"],
            ["[*]", "[ ]", "[ ]", "[ ]", "   ", "   ", "[*]", "[ ]"]
        ]

        # Overlay active pieces
        for player in self.engine.players:
            for piece in player.pieces:
                if piece.is_active:
                    r, c = piece.coord
                    grid[r][c] = f"[{player.symbol}]"

        # Tally off-board pieces
        p1 = self.engine.players[0]
        p2 = self.engine.players[1]

        p1_start = sum(1 for p in p1.pieces if p.progress == 0)
        p1_score = sum(1 for p in p1.pieces if p.progress == 15)
        p2_start = sum(1 for p in p2.pieces if p.progress == 0)
        p2_score = sum(1 for p in p2.pieces if p.progress == 15)

        # Print UI
        print(f"=== THE ROYAL GAME OF UR ===")
        print(f"Last action: {self.engine.last_action}\n")
        print(f"{p1.name} ({p1.symbol}) | Waiting: {p1_start} | Scored: {p1_score}")

        for row in grid:
            print("".join(row))

        print(f"{p2.name} ({p2.symbol}) | Waiting: {p2_start} | Scored: {p2_score}")
        print("============================")

p1 = Player("Player 1", P1_PATH, "X")
p2 = Player("Player 2", P2_PATH, "O")
game = Engine(p1, p2)
ui = BoardVisualizer(game)

while not p1.has_won() and not p2.has_won():
    ui.draw()
    time.sleep(0.5)  # Adjust for animation speed

    roll = game.roll_dice()
    valid_moves = game.get_valid_moves(roll)

    if not valid_moves:
        game.last_action = f"{game.current_player.name} rolled {roll} but has no moves. Turn skipped."
        game.current_idx = 1 - game.current_idx
        continue

    chosen_piece = random.choice(valid_moves)
    game.execute_move(chosen_piece, roll)

# Final Draw
ui.draw()
winner = p1.name if p1.has_won() else p2.name
print(f"\nGame Over! {winner} takes the crown!")
