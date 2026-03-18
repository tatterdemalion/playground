import os
import sys
import time
import random
from dataclasses import dataclass
from ur.game import Player, Piece, Engine, P1_PATH, P2_PATH, ROSETTAS
from ur.ai.bots import Bot, RandomBot, GreedyBot, StrategicBot

# --- ANSI COLOR CODES ---
C_RESET = "\033[0m"        # Resets terminal color back to default
C_BOARD = "\033[90m"       # Dark Gray for drawing the grid lines of the board
C_P1 = "\033[96m"          # Bright Cyan for Player 1 (You) and your pieces
C_P2 = "\033[91m"          # Bright Red for Player 2 (The Bot) and its pieces
C_ROSETTA = "\033[93m"     # Bright Yellow for Rosetta squares (✿) and point alerts
C_BOLD_TEXT = '\033[1;97m' # 1 for Bold, 97 for Bright White
C_TEXT = "\033[97m"        # Bright White for headers, menus, and general UI text

NUM_CIRCLES = {1: "①", 2: "②", 3: "③", 4: "④", 5: "⑤", 6: "⑥", 7: "⑦"}
BOARD_ROWS = 3
BOARD_COLUMNS = 8
MISSING_CELLS = ((0, 4), (0, 5), (2, 4), (2, 5))

TEMPLATE = """\
╔═══╦═══╦═══╦═══╗       ╔═══╦═══╗
║ {c00} ║ {c01} ║ {c02} ║ {c03} ║       ║ {c06} ║ {c07} ║
╠═══╬═══╬═══╬═══╬═══╦═══╬═══╬═══╣
║ {c10} ║ {c11} ║ {c12} ║ {c13} ║ {c14} ║ {c15} ║ {c16} ║ {c17} ║
╠═══╬═══╬═══╬═══╬═══╩═══╬═══╬═══╣
║ {c20} ║ {c21} ║ {c22} ║ {c23} ║       ║ {c26} ║ {c27} ║
╚═══╩═══╩═══╩═══╝       ╚═══╩═══╝\
"""


@dataclass
class Stats:
    p1_score: int
    p2_waiting: int
    p2_score: int


def clear():
    os.system("clear")


class BoardVisualizer:
    def __init__(self, engine: Engine):
        self.engine = engine
        self.p1, self.p2 = self.engine.players

    def draw(self):
        clear()

        stats = self._get_stats()
        cells = self._get_cells()

        # Create strings for waiting pieces
        p2_waiting_line = f"{C_P2}{' ●' * stats.p2_waiting}{C_RESET}"

        # Human waiting line (Always draws the specific piece's permanent number!)
        p1_waiting_line = " ".join([
            f"{C_P1}{self._numbered_piece(piece)}{C_RESET}"
            for piece in self.p1.pieces if piece.progress == 0
        ])

        p2_line = f"{C_P2} {self.p2.name} {stats.p2_score * '●'} {C_RESET}"
        p1_line = f"{C_P1} {self.p1.name} {stats.p1_score * '●'} {C_RESET}"

        board = TEMPLATE.format(**cells)

        game_screen = f"""
{C_BOLD_TEXT}=== THE ROYAL GAME OF UR ==={C_RESET}

        {p2_line}
        {p2_waiting_line}
{C_BOARD}{board}{C_RESET}
         {p1_waiting_line}
        {p1_line}
        """
        print(game_screen)

    def _get_stats(self) -> Stats:
        return Stats(
            p1_score=sum(1 for p in self.p1.pieces if p.progress >= 15),
            p2_waiting=sum(1 for p in self.p2.pieces if p.progress == 0),
            p2_score=sum(1 for p in self.p2.pieces if p.progress >= 15),
        )

    def _get_cells(self) -> dict[str, str]:
        cells = {}
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLUMNS):
                coord = (r, c)
                if coord in MISSING_CELLS: continue

                content = " "
                if coord in ROSETTAS:
                    content = f"{C_ROSETTA}✿{C_BOARD}"

                for piece in self.p2.pieces:
                    if piece.is_available and piece.coord == coord:
                        content = f"{C_P2}●{C_BOARD}"

                for piece in self.p1.pieces:
                    if piece.is_available and piece.coord == coord:
                        content = f"{C_P1}{self._numbered_piece(piece)}{C_BOARD}"

                cells[f"c{r}{c}"] = content

        return cells

    def _numbered_piece(self, piece: Piece) -> str:
        return NUM_CIRCLES[piece.identifier]


def _animate_dice(turn_text: str, player_color: str, roll: int):
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


def _build_move_hints(piece: Piece, roll: int, p1: Player, p2: Player, bot_name: str) -> str:
    target = piece.progress + roll
    target_coord = p1.path[target]
    hints = []

    if target == 15:
        hints.append(f"{C_ROSETTA}Scores a point!{C_RESET}")
    elif target_coord in ROSETTAS:
        hints.append(f"{C_ROSETTA}Lands on Rosetta (Roll again!){C_RESET}")

    for opp_piece in p2.pieces:
        if opp_piece.is_available and opp_piece.coord == target_coord:
            hints.append(f"{C_P2}Captures {bot_name}'s piece!{C_RESET}")

    return f" — {' '.join(hints)}" if hints else ""


def _get_human_move(valid_moves: list[Piece], roll: int, p1: Player, p2: Player, bot_name: str) -> Piece:
    print("Your options:")
    valid_moves.sort(key=lambda p: p.identifier)

    for piece in valid_moves:
        target = piece.progress + roll
        status = "Off-board" if piece.progress == 0 else f"Square {piece.progress}"
        hint_text = _build_move_hints(piece, roll, p1, p2, bot_name)
        print(f"  {C_P1}{NUM_CIRCLES[piece.identifier]}{C_RESET} : {status} -> Square {target}{hint_text}")

    while True:
        raw_input = input("\nSelect a piece to move (1-7): ")
        if raw_input == "exit":
            sys.exit()
        try:
            choice = int(raw_input)
            chosen = next((p for p in valid_moves if p.identifier == choice), None)
            if chosen:
                return chosen
            print("Invalid choice. That piece cannot move right now.")
        except ValueError:
            print("Please enter a valid piece number.")


def _get_bot_move(bot: Bot, engine: Engine, valid_moves: list[Piece], roll: int) -> Piece:
    state = {
        "my_pieces": sorted([p.progress for p in engine.current_player.pieces]),
        "opp_pieces": sorted([p.progress for p in engine.opponent.pieces]),
        "current_roll": roll,
    }
    return bot.choose_move(state, valid_moves, engine.current_player)


def play_game(bot: Bot):
    p1 = Player("You", P1_PATH, "●")
    p2 = Player(bot.name, P2_PATH, "●")

    engine = Engine(p1, p2)
    ui = BoardVisualizer(engine)

    while not engine.winner:
        roll = engine.roll_dice()
        valid_moves = engine.get_valid_moves(roll)

        ui.draw()
        print(f"Last action: {engine.last_action}")

        player_color = C_P1 if engine.current_player == p1 else C_P2
        turn_text = "Your" if engine.current_player == p1 else f"{engine.current_player.name}'s"
        _animate_dice(turn_text, player_color, roll)

        if not valid_moves:
            print("No valid moves. Turn skipped.")
            engine.last_action = f"{engine.current_player.name} rolled {roll} but had no moves."
            engine.current_idx = 1 - engine.current_idx
            time.sleep(2)
            continue

        if engine.current_player == p1:
            chosen_piece = _get_human_move(valid_moves, roll, p1, p2, bot.name)
        else:
            time.sleep(1.2)
            chosen_piece = _get_bot_move(bot, engine, valid_moves, roll)
            time.sleep(1.2)

        engine.execute_move(chosen_piece, roll)

    ui.draw()
    print(f"\nGame Over! {engine.winner} took the crown!")
    input("\nPress Enter to return to the main menu...")


def show_tutorial():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{C_BOLD_TEXT}=== HOW TO PLAY THE ROYAL GAME OF UR ==={C_RESET}\n")
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
        os.system('clear')
        print(f"{C_TEXT}=== THE ROYAL GAME OF UR ==={C_RESET}\n")
        print("  [1] Play Game")
        print("  [2] How to Play (Tutorial)")
        print("  [3] Exit\n")

        choice = input("Select an option: ")

        if choice == '1':
            bot = select_bot_menu()
            if bot:
                play_game(bot)
            else:
                main_menu()
        elif choice == '2':
            show_tutorial()
        elif choice == '3' or choice == "exit":
            os.system('cls' if os.name == 'nt' else 'clear')
            sys.exit()


def select_bot_menu():
    while True:
        os.system('clear')
        print(f"{C_BOLD_TEXT}=== SELECT OPPONENT ==={C_RESET}\n")
        print("  [1] RandomBot    (Easy - Moves completely randomly)")
        print("  [2] GreedyBot    (Medium - Always takes points or hits immediately)")
        print("  [3] StrategicBot (Hard - Calculates probabilities of danger)\n")
        print("  [4] Back to Main Menu\n")

        choice = input("Select an opponent: ")

        if choice == '1':
            return RandomBot()
        elif choice == '2':
            return GreedyBot()
        elif choice == '3':
            return StrategicBot()
        elif choice == '4':
            return None


if __name__ == "__main__":
    main_menu()
