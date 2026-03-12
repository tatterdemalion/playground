import os
import sys
import time
import random
from ur.game import Player, Engine, P1_PATH, P2_PATH, ROSETTAS
from ur.ai.bots import RandomBot, GreedyBot, StrategicBot

# --- ANSI COLOR CODES ---
C_RESET = '\033[0m'
C_BOARD = '\033[90m'
C_P1 = '\033[96m'         # Cyan for You
C_P2 = '\033[91m'         # Red for the Bot
C_ROSETTA = '\033[93m'
C_TEXT = '\033[97m'

# Unicode Circle Numbers for easier move selection
NUM_CIRCLES = {1: "①", 2: "②", 3: "③", 4: "④", 5: "⑤", 6: "⑥", 7: "⑦"}

class BoardVisualizer:
    def __init__(self, engine: Engine):
        self.engine = engine

    def draw(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        p1, p2 = self.engine.players[0], self.engine.players[1]

        # Tally pieces
        p1_score = sum(1 for p in p1.pieces if p.progress == 15)
        p2_waiting = sum(1 for p in p2.pieces if p.progress == 0)
        p2_score = sum(1 for p in p2.pieces if p.progress == 15)

        # Create strings for waiting pieces
        p2_waiting_line = f"{C_P2}{' ●' * p2_waiting}{C_RESET}"

        # Human waiting line (Always draws the specific piece's permanent number!)
        p1_waiting_chars = []
        for piece in p1.pieces:
            if piece.progress == 0:
                p_id = int(piece.identifier.split(':')[1]) + 1
                p1_waiting_chars.append(f"{C_P1}{NUM_CIRCLES[p_id]}{C_RESET}")
        p1_waiting_line = "      " + " ".join(p1_waiting_chars)

        cells = {}
        for r in range(3):
            for c in range(8):
                if r in (0, 2) and c in (4, 5): continue

                content = " "
                if (r, c) in ROSETTAS:
                    content = f"{C_ROSETTA}✿{C_RESET}"

                for piece in p2.pieces:
                    if piece.is_active and piece.coord == (r, c):
                        content = f"{C_P2}●{C_RESET}"

                for piece in p1.pieces:
                    if piece.is_active and piece.coord == (r, c):
                        # Extract the 1-7 ID dynamically from the engine's piece identifier
                        p_id = int(piece.identifier.split(':')[1]) + 1
                        content = f"{C_P1}{NUM_CIRCLES[p_id]}{C_RESET}"

                cells[f"c{r}{c}"] = content

        p2_header = f"      [{C_P2} {p2.name} {p2_score * '●'} {C_RESET}] "
        p1_footer = f"      [{C_P1} {p1.name} {p1_score * '●'} {C_RESET}] "

        board_ui = f"""
{C_TEXT}=== THE ROYAL GAME OF UR ==={C_RESET}
Last action: {self.engine.last_action}

{p2_header}
{p2_waiting_line}
{C_BOARD}╔═══╦═══╦═══╦═══╗       ╔═══╦═══╗{C_RESET}
{C_BOARD}║{C_RESET} {cells['c00']} {C_BOARD}║{C_RESET} {cells['c01']} {C_BOARD}║{C_RESET} {cells['c02']} {C_BOARD}║{C_RESET} {cells['c03']} {C_BOARD}║       ║{C_RESET} {cells['c06']} {C_BOARD}║{C_RESET} {cells['c07']} {C_BOARD}║{C_RESET}
{C_BOARD}╠═══╬═══╬═══╬═══╬═══╦═══╬═══╬═══╣{C_RESET}
{C_BOARD}║{C_RESET} {cells['c10']} {C_BOARD}║{C_RESET} {cells['c11']} {C_BOARD}║{C_RESET} {cells['c12']} {C_BOARD}║{C_RESET} {cells['c13']} {C_BOARD}║{C_RESET} {cells['c14']} {C_BOARD}║{C_RESET} {cells['c15']} {C_BOARD}║{C_RESET} {cells['c16']} {C_BOARD}║{C_RESET} {cells['c17']} {C_BOARD}║{C_RESET}
{C_BOARD}╠═══╬═══╬═══╬═══╬═══╩═══╬═══╬═══╣{C_RESET}
{C_BOARD}║{C_RESET} {cells['c20']} {C_BOARD}║{C_RESET} {cells['c21']} {C_BOARD}║{C_RESET} {cells['c22']} {C_BOARD}║{C_RESET} {cells['c23']} {C_BOARD}║       ║{C_RESET} {cells['c26']} {C_BOARD}║{C_RESET} {cells['c27']} {C_BOARD}║{C_RESET}
{C_BOARD}╚═══╩═══╩═══╩═══╝       ╚═══╩═══╝{C_RESET}
{p1_waiting_line}
{p1_footer}
"""
        print(board_ui)


def play_game(bot_class):
    bot_name = bot_class.__name__

    # Ahh, much better. P1 gets P1_PATH, P2 gets P2_PATH.
    p1 = Player("You", P1_PATH, "●")
    p2 = Player(bot_name, P2_PATH, "●")

    game = Engine(p1, p2)
    ui = BoardVisualizer(game)
    bot = bot_class()

    while not p1.has_won() and not p2.has_won():
        current_player = game.current_player
        roll = game.roll_dice()
        valid_moves = game.get_valid_moves(roll)

        ui.draw()

        # --- DICE ANIMATION ---
        player_color = C_P1 if current_player == p1 else C_P2
        turn_text = "Your" if current_player.name == "You" else f"{current_player.name}'s"

        for _ in range(12):
            random_dots = " ".join(random.choice(["●", "○"]) for _ in range(4))
            sys.stdout.write(f"\r{turn_text} turn. Rolling...  [{player_color}{random_dots}{C_RESET}]")
            sys.stdout.flush()
            time.sleep(0.06)

        final_faces = ["●"] * roll + ["○"] * (4 - roll)
        random.shuffle(final_faces)
        final_str = " ".join(final_faces)

        sys.stdout.write(f"\r{turn_text} turn. Rolled {roll}! [{player_color}{final_str}{C_RESET}]" + " " * 10 + "\n\n")
        sys.stdout.flush()
        # ----------------------

        if not valid_moves:
            print("No valid moves. Turn skipped.")
            game.last_action = f"{current_player.name} rolled {roll} but had no moves."
            game.current_idx = 1 - game.current_idx
            time.sleep(2)
            continue

        if current_player == p1:
            print("Your options:")

            # Sort by the piece's permanent ID (1 to 7)
            valid_moves.sort(key=lambda p: int(p.identifier.split(':')[1]))

            for piece in valid_moves:
                p_id = int(piece.identifier.split(':')[1]) + 1
                target = piece.progress + roll
                target_coord = p1.path[target]
                status = "Off-board" if piece.progress == 0 else f"Square {piece.progress}"

                hints = []
                if target == 15:
                    hints.append(f"{C_ROSETTA}Scores a point!{C_RESET}")
                elif target_coord in ROSETTAS:
                    hints.append(f"{C_ROSETTA}Lands on Rosetta (Roll again!){C_RESET}")

                for opp_piece in p2.pieces:
                    if opp_piece.is_active and opp_piece.coord == target_coord:
                        hints.append(f"{C_P2}Captures {bot_name}'s piece!{C_RESET}")

                hint_text = f" — {' '.join(hints)}" if hints else ""

                # Menu option is now exactly the Piece ID!
                print(f"  {C_P1}{NUM_CIRCLES[p_id]}{C_RESET} : {status} -> Square {target}{hint_text}")

            chosen_piece = None
            while chosen_piece is None:
                raw_input = input("\nSelect a piece to move (1-7): ")
                if raw_input == "exit":
                    sys.exit()

                try:
                    choice = int(raw_input)
                    # Match the user's input directly to the piece's permanent ID
                    chosen_piece = next((p for p in valid_moves if int(p.identifier.split(':')[1]) + 1 == choice), None)
                    if not chosen_piece:
                        print("Invalid choice. That piece cannot move right now.")
                except ValueError:
                    print("Please enter a valid piece number.")

            game.execute_move(chosen_piece, roll)

        else:
            time.sleep(1.2)
            state = {
                "my_pieces": sorted([p.progress for p in current_player.pieces]),
                "opp_pieces": sorted([p.progress for p in game.opponent.pieces]),
                "current_roll": roll
            }
            chosen_piece = bot.choose_move(state, valid_moves, current_player)
            game.execute_move(chosen_piece, roll)
            time.sleep(1.2)

    ui.draw()
    winner = "You" if p1.has_won() else bot_name
    print(f"\nGame Over! {winner} took the crown!")
    input("\nPress Enter to return to the main menu...")


def show_tutorial():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{C_TEXT}=== HOW TO PLAY THE ROYAL GAME OF UR ==={C_RESET}\n")
    print("1. Objective: Move all 7 of your pieces across the board to the end before your opponent.")
    print("2. Movement: You roll 4 binary dice each turn, yielding a move of 0 to 4 spaces.")
    print("3. Stacking: You cannot land on a square occupied by your own piece.")
    print("4. Combat: Landing on an opponent's piece in the shared middle row 'captures' it,")
    print("   sending it back off-board to start over.")
    print(f"5. Rosettas: Landing on a Rosetta ({C_ROSETTA}✿{C_RESET}) grants an extra turn immediately.")
    print("   Additionally, the central Rosetta is a safe haven where your piece cannot be captured.\n")
    input("Press Enter to return to the main menu...")


def main_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{C_TEXT}=== THE ROYAL GAME OF UR ==={C_RESET}\n")
        print("  [1] Play Game")
        print("  [2] How to Play (Tutorial)")
        print("  [3] Exit\n")

        choice = input("Select an option: ")

        if choice == '1':
            bot_class = select_bot_menu()
            if bot_class:
                play_game(bot_class)
        elif choice == '2':
            show_tutorial()
        elif choice == '3':
            os.system('cls' if os.name == 'nt' else 'clear')
            sys.exit()


def select_bot_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{C_TEXT}=== SELECT OPPONENT ==={C_RESET}\n")
        print("  [1] RandomBot    (Easy - Moves completely randomly)")
        print("  [2] GreedyBot    (Medium - Always takes points or hits immediately)")
        print("  [3] StrategicBot (Hard - Calculates probabilities of danger)\n")
        print("  [4] Back to Main Menu\n")

        choice = input("Select an opponent: ")

        if choice == '1':
            return RandomBot
        elif choice == '2':
            return GreedyBot
        elif choice == '3':
            return StrategicBot
        elif choice == '4':
            return None


if __name__ == "__main__":
    main_menu()
