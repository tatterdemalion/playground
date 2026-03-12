import random
from typing import Optional

POSITIONS = tuple(range(14))
POSITIONS_WITH_BEGINNING = tuple(range(-1, 14))
PERSONAL_POSITIONS = tuple(range(4)) + tuple(range(12, 14))
COMMON_POSITIONS = tuple(range(4, 12))
SAFE_POSITIONS = tuple(range(4)) + (7,) + tuple(range(12, 14))
ROSETTA_POSITIONS = (3, 7, 13)


class Piece:
    last_position = -1
    current_position = -1
    next_position = -1

    def __init__(self, identifier: int, player: "Player") -> None:
        self.player = player
        self.identifier = f"{player.name}:{identifier}"

    def __str__(self):
        return ":".join((self.identifier, self.last_position, self.current_position, self.next_position))

    def refresh(self) -> "Piece":
        self.next_position = self.current_position + self.player.points
        return self

    def restart(self):
        self.last_position = self.current_position
        self.current_position = 0
        self.next_position = 0

    def is_safe(self):
        return self.current_position in SAFE_POSITIONS

    def is_on_rosetta(self):
        return self.current_position in PERSONAL_POSITIONS


class Player:
    dices: list[int, int, int, int] = [0, 0, 0, 0]
    points: int = 0
    next: Optional["Player"] = None
    playing: bool = False

    def __init__(self, name: str, *args, **kwargs):
        self.name = name
        self.pieces = [Piece(index, self) for index in range(7)]

    def set_next(self, other_player: "Player") -> None:
        if self.next:
            other_player.next = self.next
        self.next = other_player

    def end_turn(self):
        self.playing = False
        self.next.playing = True

    def won(self):
        return not any([piece.current_position < 14 for piece in self.pieces])

    @property
    def current_pieces(self) -> dict[int: Piece]:
        return {
            piece.current_position: piece.refresh()
            for piece in self.pieces
            if piece.current_position >= 0 and piece.current_position < 14
        }

    def __str__(self):
        return self.name


class Log:
    ledger = []

    def write(self, player: Player, piece: Piece, state: str) -> None:
        self.ledger.append({
            "player": player.name,
            "dices": player.dices,
            "points": player.points,
            "piece": piece.identifier,
            "last_position": piece.last_position,
            "current_position": piece.current_position,
            "state": state,
        })

    def pprint(self):
        from pprint import pprint
        pprint(self.ledger)


class Engine:
    log: Log = Log()
    game_over: bool = False
    current_player: Optional[Player] = None
    players: list = []
    pieces: list = []

    def __init__(self, current_player: Player) -> None:
        self.current_player = current_player
        self.players.append(current_player)
        self.pieces += self.current_player.pieces

        player = self.current_player.next
        while player != self.current_player:
            self.players.append(player)
            self.pieces += player.pieces
            player = player.next

    @property
    def current_pieces(self):
        return {piece.current_position: piece for player in self.players for piece in player.current_pieces.values()}

    def draw(self, number_of_dices: int = 4) -> None:
        self.current_player.dices = [random.getrandbits(1) for i in range(number_of_dices)]
        self.current_player.points = sum(self.current_player.dices)

    def move(self, piece: Piece) -> tuple[bool, str]:
        piece.refresh()
        state = "move"
        if other_piece := self.current_pieces.get(piece.next_position):
            if other_piece.is_safe or other_piece.player == self.current_player:
                state = "collision"
                return False, state
            else:
                state = "hit"
                other_piece.restart()

        piece.last_position = piece.current_position
        piece.current_position = piece.next_position

        if self.current_player.won():
            self.game_over = True
            state = "won"

        self.current_player.end_turn()
        self.current_player = self.current_player.next
        self.current_player.points = 0

        self.log.write(self.current_player, piece, state)

        return True, state


if __name__ == "__main__":
    player_1 = Player("p1")
    player_2 = Player("p2")
    player_1.set_next(player_2)
    player_2.set_next(player_1)
    engine = Engine(current_player=player_1)

    def rand_piece():
        pieces = [piece for piece in engine.current_player.pieces if piece.current_position in POSITIONS_WITH_BEGINNING]
        return random.choice(pieces)

    while not engine.game_over:
        engine.draw()
        success = False
        while not success:
            piece = rand_piece()
            success, state = engine.move(piece)

        engine.log.pprint()
