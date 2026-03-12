from game.ai.environment import UrEnvironment
from game.ai.bots import RandomBot, GreedyBot


env = UrEnvironment()

# Let's pit a Random bot against our new Greedy bot
bots = {
    0: RandomBot(),
    1: GreedyBot()
}

state, valid_moves, done, _ = env.reset()
turns = 0

while not done:
    turns += 1
    active_player_idx = env.game.current_idx
    active_bot = bots[active_player_idx]
    active_player = env.game.current_player

    # 1. The Environment asks the Bot for a decision
    chosen_piece = active_bot.choose_move(state, valid_moves, active_player)

    # 2. The Bot hands the decision back to the Environment
    state, valid_moves, reward, done = env.step(chosen_piece)

winner = "P1 (Random)" if env.game.players[0].has_won() else "P2 (Greedy)"
print(f"Game Over in {turns} turns! Winner: {winner}")
