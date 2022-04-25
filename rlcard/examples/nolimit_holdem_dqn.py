""" An example of learning a Deep-Q Agent on Texas No-Limit Holdem
"""

import os

import torch
from tqdm import tqdm

import rlcard
from rlcard.agents import DQNAgentPytorch, RandomAgent
from rlcard.utils import Logger
from rlcard.utils import set_global_seed, tournament


def create_dqn_agent(agent_id, env, memory_init_size, train_every):
    return DQNAgentPytorch(scope=f'dqn_{agent_id}',
                           action_num=env.action_num,
                           replay_memory_init_size=memory_init_size,
                           train_every=train_every,
                           state_shape=env.state_shape,
                           mlp_layers=[512, 512])


def main():
    game_player_num = 6
    # Make environment
    env = rlcard.make('no-limit-holdem', config={'seed': 0, 'game_player_num': game_player_num})
    eval_env = rlcard.make('no-limit-holdem', config={'seed': 0, 'game_player_num': game_player_num})

    # Set the iterations numbers and how frequently we evaluate the performance
    evaluate_every = 100
    evaluate_num = 100
    episode_num = 1000

    # The intial memory size
    memory_init_size = 1000

    # Train the agent every X steps
    train_every = 1

    # The paths for saving the logs and learning curves
    log_dir = './experiments/nolimit_holdem_dqn_result/'

    # Set a global seed
    set_global_seed(0)

    # Set up the agents
    dqn_agents = [create_dqn_agent(agent_id, env, memory_init_size, train_every) for agent_id in range(game_player_num)]
    random_agents = [RandomAgent(action_num=eval_env.action_num) for _ in range(game_player_num - 1)]
    env.set_agents(dqn_agents)
    eval_env.set_agents(dqn_agents[:1] + random_agents)

    # Init a Logger to plot the learning curve
    logger = Logger(log_dir)

    for episode in (range(episode_num)):
        # Generate data from the environment
        trajectories, _ = env.run(is_training=True)
        # Feed transitions into agent memory, and train the agent
        for tss, agent in zip(trajectories, dqn_agents):
            for ts in tss:
                agent.feed(ts)

        # Evaluate the performance. Play with random agents.
        if episode % evaluate_every == 0:
            logger.log_performance(env.timestep, tournament(eval_env, evaluate_num)[0])

    # Close files in the logger
    logger.close_files()

    # Plot the learning curve
    logger.plot('DQN')

    # Save model
    save_dir = 'models/nolimit_holdem_dqn'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    for agent_id, agent in enumerate(dqn_agents):
        state_dict = {}
        state_dict.update(agent.get_state_dict())
        torch.save(state_dict, os.path.join(save_dir, f'model_{agent_id}'))


if __name__ == '__main__':
    main()
