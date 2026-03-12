import os
import time
from game.ur import Player, Engine, P1_PATH, P2_PATH
from game.ai.bots import StrategicBot

class BoardVisualizer:
    def __init__(self, engine: Engine):
        self.engine = engine

    def draw(self):
        os.system('cls' if os.name == 'nt' else 'clear')

        grid = [
            ["[*]", "[ ]", "[ ]", "[ ]", "   ", "   ", "[*]", "[ ]"],
            ["[ ]", "[ ]", "[ ]", "[*]", "[ ]", "[ ]", "[ ]", "[ ]"],
            ["[*]", "[ ]", "[ ]", "[ ]", "   ", "   ", "[*]", "[ ]"]
        ]

        for player in self.engine.players:
            for piece in player.pieces:
                if piece.is_active:
                    r, c = piece.coord
                    grid[r][c] = f"[{player.symbol}]"

        p1, p2 = self.engine.players[0], self.engine.players[1]

        p1_start = sum(1 for p in p1.pieces if p.progress == 0)
        p1_score = sum(1 for p in p1.pieces if p.progress == 15)
        p2_start = sum(1 for p in p2.pieces if p.progress == 0)
        p2_score = sum(1 for p in p2.pieces if p.progress == 15)

        print(f"=== THE ROYAL GAME OF UR ===")
        print(f"Last action: {self.engine.last_action}\n")

        # Swapped print order: Bot (p2) on top, You (p1) on the bottom
        print(f"{p2.name} ({p2.symbol}) | Waiting: {p2_start} | Scored: {p2_score}")
        for row in grid:
            print("".join(row))
        print(f"{p1.name} ({p1.symbol}) | Waiting: {p1_start} | Scored: {p1_score}")
        print("============================\n")


def play_game():
    # Swapped paths: Human gets P2_PATH (Row 2), Bot gets P1_PATH (Row 0)
    p1 = Player("You", P2_PATH, "X")
    p2 = Player("StrategicBot", P1_PATH, "O")

    game = Engine(p1, p2)
    ui = BoardVisualizer(game)

    bot = StrategicBot()

    while not p1.has_won() and not p2.has_won():
        ui.draw()

        current_player = game.current_player
        roll = game.roll_dice()
        valid_moves = game.get_valid_moves(roll)

        turn_text = "Your" if current_player.name == "You" else f"{current_player.name}'s"
        print(f"{turn_text} turn. Rolled a {roll}!")

        if not valid_moves:
            print("No valid moves. Turn skipped.")
            game.last_action = f"{current_player.name} rolled {roll} but had no moves."
            game.current_idx = 1 - game.current_idx
            time.sleep(2)
            continue

        # --- HUMAN TURN ---
        if current_player == p1:
            print("\nValid moves:")

            # valid_moves.sort(key=lambda piece: piece.progress)

            for i, piece in enumerate(valid_moves):
                target = piece.progress + roll
                status = "Off-board" if piece.progress == 0 else f"Progress {piece.progress}"
                print(f"  [{i + 1}] Move piece from {status} -> Progress {target}")

            chosen_piece = None
            while chosen_piece is None:
                try:
                    choice = int(input("\nSelect a move (number): ")) - 1
                    if 0 <= choice < len(valid_moves):
                        chosen_piece = valid_moves[choice]
                    else:
                        print("Invalid choice. Try again.")
                except ValueError:
                    print("Please enter a valid number.")

            game.execute_move(chosen_piece, roll)

        # --- BOT TURN ---
        else:
            time.sleep(1.5)
            state = {
                "my_pieces": sorted([p.progress for p in current_player.pieces]),
                "opp_pieces": sorted([p.progress for p in game.opponent.pieces]),
                "current_roll": roll
            }
            chosen_piece = bot.choose_move(state, valid_moves, current_player)
            game.execute_move(chosen_piece, roll)
            time.sleep(1.5)

    ui.draw()
    winner = "You" if p1.has_won() else "StrategicBot"
    print(f"\nGame Over! {winner} took the crown!")


if __name__ == "__main__":
    play_game()
