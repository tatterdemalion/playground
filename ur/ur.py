import random
import time
import os

# --- 1. THE BOARD GEOMETRY ---
P1_PATH = {
    0: None, 1: (0, 3), 2: (0, 2), 3: (0, 1), 4: (0, 0),
    5: (1, 0), 6: (1, 1), 7: (1, 2), 8: (1, 3), 9: (1, 4), 10: (1, 5), 11: (1, 6), 12: (1, 7),
    13: (0, 7), 14: (0, 6), 15: None
}

P2_PATH = {
    0: None, 1: (2, 3), 2: (2, 2), 3: (2, 1), 4: (2, 0),
    5: (1, 0), 6: (1, 1), 7: (1, 2), 8: (1, 3), 9: (1, 4), 10: (1, 5), 11: (1, 6), 12: (1, 7),
    13: (2, 7), 14: (2, 6), 15: None
}

ROSETTAS = {(0, 0), (2, 0), (1, 3), (0, 6), (2, 6)}


# --- 2. ENTITIES ---
class Piece:
    def __init__(self, identifier: int, player: "Player"):
        self.identifier = f"{player.name}:{identifier}"
        self.player = player
        self.progress = 0

    @property
    def coord(self):
        return self.player.path[self.progress]

    @property
    def is_active(self):
        return 0 < self.progress < 15


class Player:
    def __init__(self, name: str, path: dict, symbol: str):
        self.name = name
        self.path = path
        self.symbol = symbol
        self.pieces = [Piece(i, self) for i in range(7)]

    def has_won(self) -> bool:
        return all(piece.progress == 15 for piece in self.pieces)


# --- 3. THE ENGINE ---
class Engine:
    def __init__(self, player_1: Player, player_2: Player):
        self.players = [player_1, player_2]
        self.current_idx = 0
        self.last_action = "Game started."

    @property
    def current_player(self) -> Player:
        return self.players[self.current_idx]

    @property
    def opponent(self) -> Player:
        return self.players[1 - self.current_idx]

    def roll_dice(self) -> int:
        return sum(random.getrandbits(1) for _ in range(4))

    def get_valid_moves(self, roll: int) -> list[Piece]:
        if roll == 0:
            return []

        valid_moves = []
        for piece in self.current_player.pieces:
            if piece.progress == 15:
                continue

            target_progress = piece.progress + roll
            if target_progress > 15:
                continue

            target_coord = self.current_player.path[target_progress]

            # Rule 1 FIX: Cannot land on your own piece, unless it is off-board at 15
            if target_progress < 15 and any(p.progress == target_progress for p in self.current_player.pieces):
                continue

            # Rule 2: Cannot hit an opponent if they are on a Rosetta
            if target_coord in ROSETTAS:
                if any(p.coord == target_coord for p in self.opponent.pieces if p.is_active):
                    continue

            valid_moves.append(piece)

        return valid_moves

    def execute_move(self, piece: Piece, roll: int):
        target_progress = piece.progress + roll
        target_coord = self.current_player.path[target_progress]
        state = "moved"
        roll_again = target_coord in ROSETTAS and target_progress < 15

        # Check for hit
        if target_coord is not None:
            for opp_piece in self.opponent.pieces:
                if opp_piece.coord == target_coord and opp_piece.is_active:
                    opp_piece.progress = 0
                    state = "hit opponent"
                    break

        piece.progress = target_progress
        if target_progress == 15:
            state = "scored"
            roll_again = False # Can't roll again if you move off the board

        self.last_action = f"{self.current_player.name} rolled {roll}: {piece.identifier} {state}."

        if not roll_again and not self.current_player.has_won():
            self.current_idx = 1 - self.current_idx
        elif roll_again:
            self.last_action += " Rolled again!"


# --- 4. CLI VISUALIZER ---
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


# --- 5. GAME LOOP ---
if __name__ == "__main__":
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
