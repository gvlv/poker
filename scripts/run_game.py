import logging

from pypokerengine.api.game import setup_config, start_poker
from scripts.model_player import ModelPlayer

from scripts.strategy_player import StrategyPlayer


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
    )


def main():
    setup_logging()
    small_blind = 100
    big_blind = small_blind * 2

    config = setup_config(max_round=5000, initial_stack=20000, small_blind_amount=small_blind, reset_stack=True)
    config.register_player(name="dummy_player1", algorithm=StrategyPlayer(write_log=True, decrease_coefficient=100.))
    config.register_player(name="strategy2", algorithm=StrategyPlayer())
    config.register_player(name="strategy3", algorithm=StrategyPlayer())
    config.register_player(name="strategy4", algorithm=StrategyPlayer())
    config.register_player(name="strategy5", algorithm=StrategyPlayer())
    config.register_player(name="model6",
                           algorithm=ModelPlayer(classifier_path='/Users/shulgin/classifier.full.26.12.2020.pt',
                                                 regressor_path='/Users/shulgin/regressor.full.26.12.2020.1000_iterations.pt',
                                                 big_blind=big_blind))

    game_result = start_poker(config, verbose=1)


if __name__ == '__main__':
    main()
