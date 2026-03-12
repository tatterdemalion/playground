import time
from game.ai.environment import UrEnvironment
from game.ai.bots import RandomBot, GreedyBot


def run_simulation(num_games=1000):
    env = UrEnvironment()

    random_bot = RandomBot()
    greedy_bot = GreedyBot()

    results = {
        "RandomBot": {"wins": 0, "total_turns": 0},
        "GreedyBot": {"wins": 0, "total_turns": 0}
    }

    start_time = time.time()
    print(f"Starting simulation of {num_games} games...")

    for i in range(num_games):
        # Swap who goes first halfway through to be fair
        if i < num_games // 2:
            bots = {0: random_bot, 1: greedy_bot}
            p1_name, p2_name = "RandomBot", "GreedyBot"
        else:
            bots = {0: greedy_bot, 1: random_bot}
            p1_name, p2_name = "GreedyBot", "RandomBot"

        state, valid_moves, done, _ = env.reset()
        turns = 0

        while not done:
            turns += 1
            active_player_idx = env.game.current_idx
            active_bot = bots[active_player_idx]
            active_player = env.game.current_player

            chosen_piece = active_bot.choose_move(state, valid_moves, active_player)
            state, valid_moves, reward, done = env.step(chosen_piece)

        # Game over, record stats
        winner_idx = 0 if env.game.players[0].has_won() else 1
        winner_name = p1_name if winner_idx == 0 else p2_name

        results[winner_name]["wins"] += 1
        results[winner_name]["total_turns"] += turns

    # Print Report
    elapsed = time.time() - start_time
    print("\n=== SIMULATION RESULTS ===")
    print(f"Games Played: {num_games} (in {elapsed:.2f} seconds)")

    for bot_name, stats in results.items():
        win_rate = (stats["wins"] / num_games) * 100
        avg_turns = stats["total_turns"] / max(1, stats["wins"]) if stats["wins"] > 0 else 0
        print(f"{bot_name}: {stats['wins']} wins ({win_rate:.1f}%) | Avg turns when winning: {avg_turns:.0f}")


if __name__ == "__main__":
    run_simulation(1000)
