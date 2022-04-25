from typing import List

from core.types import Street, ActionType
from features.board import Board
from features.combinations import Combination
from features.features import FeaturesPack
from hand import Hand, GameType


def extract_features_for_player(hand: Hand, player_name: str):
    features = []
    pack = FeaturesPack(hand.players, player_name, hand.big_blind)
    for street, board_cards, actions in [(Street.PREFLOP, [], hand.preflop_actions),
                                         (Street.FLOP, hand.flop_cards, hand.flop_actions),
                                         (Street.TURN, hand.turn_cards, hand.turn_actions),
                                         (Street.RIVER, hand.river_cards, hand.river_actions)]:
        pack.street_start(street)
        board = Board(board_cards)
        for action in actions:
            # Player makes some decision
            if action.player == player_name and action.action_type not in [ActionType.SMALLBLIND, ActionType.BIGBLIND]:
                comb = Combination(board_cards, hand.players[player_name].player_cards)
                features.append(
                    [hand.hand_id, player_name, street.name, action.action_type.name, action.bet_size / hand.big_blind] +
                    pack.collect_features() +
                    board.extract_features() +
                    [comb.ready_combination().name]
                )
            pack.collect_action(action)
    return features


def extract_features(hand: Hand, nicknames: List[str]):
    features = []
    for player_name, player in hand.players.items():
        if player_name in nicknames and player.player_cards:
            features.extend(extract_features_for_player(hand, player_name))
    return features


class FeatureExtractor(object):
    def __init__(self, nicknames: List[str]):
        self.__nicknames = nicknames

    @property
    def nicknames(self):
        return self.__nicknames

    def extract_features(self, hand: Hand):
        features = []
        if hand.game_type != GameType.HOLDEM_NO_LIMIT:
            return features
        features.extend(extract_features(hand, self.nicknames))
        return features
