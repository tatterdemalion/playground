import os
import time
import argparse
from game.ai.environment import UrEnvironment
from game.ai import bots

class SimVisualizer:
    def __init__(self, env):
        self.env = env

    def draw(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        engine = self.env.game

        grid = [
            ["[*]", "[ ]", "[ ]", "[ ]", "   ", "   ", "[*]", "[ ]"],
            ["[ ]", "[ ]", "[ ]", "[*]", "[ ]", "[ ]", "[ ]", "[ ]"],
            ["[*]", "[ ]", "[ ]", "[ ]", "   ", "   ", "[*]", "[ ]"]
        ]

        for player in engine.players:
            for piece in player.pieces:
                if piece.is_active:
                    r, c = piece.coord
                    grid[r][c] = f"[{player.symbol}]"

        p1, p2 = engine.players[0], engine.players[1]

        p1_start = sum(1 for p in p1.pieces if p.progress == 0)
        p1_score = sum(1 for p in p1.pieces if p.progress == 15)
        p2_start = sum(1 for p in p2.pieces if p.progress == 0)
        p2_score = sum(1 for p in p2.pieces if p.progress == 15)

        print(f"=== UR BOT SIMULATION ===")
        print(f"Last Action: {engine.last_action}\n")
        print(f"{p2.name} ({p2.symbol}) | Waiting: {p2_start} | Scored: {p2_score}")
        for row in grid:
            print("".join(row))
        print(f"{p1.name} ({p1.symbol}) | Waiting: {p1_start} | Scored: {p1_score}")
        print("=========================\n")


def run_simulation(bot_class_1, bot_class_2, num_games=1000, show=False):
    env = UrEnvironment()
    ui = SimVisualizer(env) if show else None

    bot_a = bot_class_1()
    bot_b = bot_class_2()

    # Handle naming, especially if pitting the same bot classes against each other
    name_a = bot_class_1.__name__
    name_b = bot_class_2.__name__
    if name_a == name_b:
        name_a, name_b = f"{name_a}_1", f"{name_b}_2"

    results = {
        name_a: {"wins": 0, "total_turns": 0},
        name_b: {"wins": 0, "total_turns": 0}
    }

    start_time = time.time()

    if not show:
        print(f"Starting simulation of {num_games} games between {name_a} and {name_b}...")

    for i in range(num_games):
        # Swap who goes first halfway through to be fair
        if i < num_games // 2:
            players = {0: bot_a, 1: bot_b}
            names = {0: name_a, 1: name_b}
        else:
            players = {0: bot_b, 1: bot_a}
            names = {0: name_b, 1: name_a}

        state, valid_moves, done, _ = env.reset()

        # Sync the names to the engine so the visualizer prints them correctly
        env.game.players[0].name = names[0]
        env.game.players[1].name = names[1]

        turns = 0

        if show:
            ui.draw()
            time.sleep(0.5)

        while not done:
            turns += 1
            active_player_idx = env.game.current_idx
            active_bot = players[active_player_idx]
            active_player = env.game.current_player

            chosen_piece = active_bot.choose_move(state, valid_moves, active_player)
            state, valid_moves, reward, done = env.step(chosen_piece)

            if show:
                ui.draw()
                time.sleep(0.1)  # Brief pause for animation

        winner_idx = 0 if env.game.players[0].has_won() else 1
        winner_name = names[winner_idx]

        results[winner_name]["wins"] += 1
        results[winner_name]["total_turns"] += turns

    # Print Report only if we aren't using the visualizer
    if not show:
        elapsed = time.time() - start_time
        print("\n=== SIMULATION RESULTS ===")
        print(f"Games Played: {num_games} (in {elapsed:.2f} seconds)")

        for bot_name, stats in results.items():
            win_rate = (stats["wins"] / num_games) * 100
            avg_turns = stats["total_turns"] / max(1, stats["wins"]) if stats["wins"] > 0 else 0
            print(f"{bot_name}: {stats['wins']} wins ({win_rate:.1f}%) | Avg turns when winning: {avg_turns:.0f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Ur AI Simulations")
    parser.add_argument("bot1", type=str, help="Name of the first bot class (e.g., RandomBot)")
    parser.add_argument("bot2", type=str, help="Name of the second bot class (e.g., GreedyBot)")
    parser.add_argument("--games", type=int, default=1000, help="Number of games to simulate")
    parser.add_argument("--show", action="store_true", help="Watch the bots play in the terminal")

    args = parser.parse_args()

    # Dynamically grab the bot classes from the bots.py file
    bot1_cls = getattr(bots, args.bot1, None)
    bot2_cls = getattr(bots, args.bot2, None)

    if not bot1_cls or not bot2_cls:
        print("Error: Could not find one or both bots. Available bots in game/ai/bots.py:")
        for attr_name in dir(bots):
            if attr_name.endswith("Bot") and attr_name != "Bot":
                print(f" - {attr_name}")
        exit(1)

    # If --show is passed, default to 1 game unless explicitly told otherwise
    games_to_play = 1 if args.show and args.games == 1000 else args.games

    run_simulation(bot1_cls, bot2_cls, games_to_play, show=args.show)
