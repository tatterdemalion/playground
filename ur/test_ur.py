import unittest

from ur import Player, Engine, P1_PATH, P2_PATH


class TestUrEngine(unittest.TestCase):
    def setUp(self):
        # Create a fresh game before each test
        self.p1 = Player("P1", P1_PATH, "X")
        self.p2 = Player("P2", P2_PATH, "O")
        self.game = Engine(self.p1, self.p2)

    def test_zero_roll(self):
        """Rolling a 0 should result in no valid moves."""
        self.assertEqual(self.game.get_valid_moves(0), [])

    def test_basic_movement_and_turn_passing(self):
        """A piece should move correctly, and passing the turn should work."""
        piece = self.p1.pieces[0]
        self.game.execute_move(piece, 2)

        self.assertEqual(piece.progress, 2)
        self.assertEqual(self.game.current_idx, 1)  # Turn passed to P2

    def test_cannot_land_on_own_piece(self):
        """Rule 1: A player cannot move a piece onto a space occupied by their own piece."""
        self.p1.pieces[0].progress = 2

        # P1 rolls a 2. Piece 1 (at progress 0) trying to move to 2 should be invalid.
        valid_moves = self.game.get_valid_moves(2)
        self.assertNotIn(self.p1.pieces[1], valid_moves)

    def test_hit_opponent(self):
        """Landing on an opponent in the shared zone should reset their progress to 0."""
        # P1 is in the shared zone at progress 5 (coord 1,0)
        self.p1.pieces[0].progress = 5

        # P2 is at progress 4 (coord 2,0). P2 rolls 1, aiming for progress 5 (coord 1,0)
        self.p2.pieces[0].progress = 4
        self.game.current_idx = 1  # Manually set to P2's turn

        self.game.execute_move(self.p2.pieces[0], 1)

        self.assertEqual(self.p2.pieces[0].progress, 5)  # P2 successfully moved
        self.assertEqual(self.p1.pieces[0].progress, 0)  # P1 was hit and reset

    def test_rosetta_safe_zone(self):
        """Rule 2: Cannot hit an opponent if they are on a Rosetta."""
        # P1 is on the central shared Rosetta at progress 8 (coord 1,3)
        self.p1.pieces[0].progress = 8

        # P2 is right behind them at progress 7. P2 rolls a 1.
        self.p2.pieces[0].progress = 7
        self.game.current_idx = 1

        valid_moves = self.game.get_valid_moves(1)
        self.assertNotIn(self.p2.pieces[0], valid_moves)  # Move is blocked by safe zone

    def test_rosetta_extra_turn(self):
        """Landing on a Rosetta should grant the player another turn."""
        # P1 rolls 4, landing on their private start Rosetta
        self.game.execute_move(self.p1.pieces[0], 4)
        self.assertEqual(self.game.current_idx, 0)  # Turn did NOT pass; still P1's turn

    def test_exact_scoring_and_stacking(self):
        """Pieces must roll exact numbers to score, and multiple pieces can sit at 15."""
        self.p1.pieces[0].progress = 14

        # 1. Roll 2 (overshoot) should be invalid
        self.assertNotIn(self.p1.pieces[0], self.game.get_valid_moves(2))

        # 2. Roll 1 (exact) should be valid
        self.assertIn(self.p1.pieces[0], self.game.get_valid_moves(1))

        # 3. Execute the score
        self.game.execute_move(self.p1.pieces[0], 1)
        self.assertEqual(self.p1.pieces[0].progress, 15)

        # --- THE FIX: Give the turn back to P1! ---
        self.game.current_idx = 0

        # 4. Confirm the "Rule 1 Fix": A second piece can also score without being blocked
        self.p1.pieces[1].progress = 14
        self.assertIn(self.p1.pieces[1], self.game.get_valid_moves(1))


if __name__ == "__main__":
    unittest.main()
