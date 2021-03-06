from pypokerengine.engine.dealer import Dealer
from pypokerengine.players import BasePokerPlayer


def setup_config(max_round, initial_stack, small_blind_amount, ante=0, reset_stack=False):
    return Config(max_round, initial_stack, small_blind_amount, ante, reset_stack)


def start_poker(config, verbose=2):
    config.validation()
    dealer = Dealer(config.sb_amount, config.initial_stack, config.ante, config.reset_stack)
    dealer.set_verbose(verbose)
    dealer.set_blind_structure(config.blind_structure)
    for info in config.players_info:
        dealer.register_player(info["name"], info["algorithm"], info["initial_stack"])
    result_message = dealer.start_game(config.max_round)
    return _format_result(result_message)


def _format_result(result_message):
    return {
        "rule": result_message["message"]["game_information"]["rule"],
        "players": result_message["message"]["game_information"]["seats"]
    }


class Config(object):

    def __init__(self, max_round, initial_stack, sb_amount, ante, reset_stack):
        self.players_info = []
        self.blind_structure = {}
        self.max_round = max_round
        self.initial_stack = initial_stack
        self.sb_amount = sb_amount
        self.ante = ante
        self.reset_stack = reset_stack

    def register_player(self, name, algorithm, initial_stack=None):
        if not isinstance(algorithm, BasePokerPlayer):
            base_msg = 'Poker player must be child class of "BasePokerPlayer". But its parent was "%s"'
            raise TypeError(base_msg % algorithm.__class__.__bases__)

        info = {"name": name, "algorithm": algorithm, "initial_stack": initial_stack}
        self.players_info.append(info)

    def set_blind_structure(self, blind_structure):
        self.blind_structure = blind_structure

    def validation(self):
        player_num = len(self.players_info)
        if player_num < 2:
            detail_msg = "no player is registered yet" if player_num == 0 else "you registered only 1 player"
            base_msg = "At least 2 players are needed to start the game"
            raise Exception("%s (but %s.)" % (base_msg, detail_msg))
