import random

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
