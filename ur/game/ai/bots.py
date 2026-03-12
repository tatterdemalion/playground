import random
from game.ur import Player, Piece, ROSETTAS

class Bot:
    def choose_move(self, state: dict, valid_moves: list, player: Player) -> Piece:
        raise NotImplementedError("Bots must implement their own logic!")

class RandomBot(Bot):
    def choose_move(self, state: dict, valid_moves: list, player: Player):
        return random.choice(valid_moves)

class GreedyBot(Bot):
    def choose_move(self, state: dict, valid_moves: list, player: Player):
        best_move = valid_moves[0]
        best_score = -1

        for piece in valid_moves:
            target_progress = piece.progress + state["current_roll"]
            target_coord = player.path[target_progress]

            score = 0
            # Priority 1: Scoring a point
            if target_progress == 15:
                score = 1000
            # Priority 2: Hitting an opponent (Shared zone is progress 5-12)
            elif 5 <= target_progress <= 12 and target_progress in state["opp_pieces"]:
                score = 500
            # Priority 3: Landing on a Rosetta
            elif target_coord in ROSETTAS:
                score = 300
            # Priority 4: Getting a piece onto the board
            elif piece.progress == 0:
                score = 100

            if score > best_score:
                best_score = score
                best_move = piece

        return best_move
