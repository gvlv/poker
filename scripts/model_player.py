import logging
from pprint import pformat
from typing import Dict

import pandas as pd
import torch

from action import Action
from core.card import Card
from core.types import ActionType, Street
from features.board import Board
from features.combinations import Combination
from features.features import FeaturesPack
from player import Player
from scripts.const import Streets
from scripts.log_player import LogPlayer
logger = logging.getLogger()


def get_features_names():
    return FeaturesPack.features_names()[5:] + Board.features_names() + Combination.features_names()


class ModelPlayer(LogPlayer):
    def __init__(self, regressor_path: str, classifier_path: str, big_blind: float):
        super().__init__()
        self.__big_blind = big_blind
        self.__pack = None
        self.__board = None
        self.__combination = None
        self.__player_name = None
        self.__players: Dict[str, Player] = {}
        self.__regressor = torch.load(regressor_path)
        self.__classifier = torch.load(classifier_path)

    def __predict(self, d, model):  # d = dict([(n, f) for n, f in zip(get_features_names(), features)])
        df = pd.DataFrame(d, index=[0])
        df.current_pot_size = df.current_pot_size.astype(int)
        df.current_bet = df.current_bet.astype(int)
        df.pay_for_continue_play = df.pay_for_continue_play.astype(int)
        df.player_stack_size = df.player_stack_size.astype(int)
        df.current_bet = df.current_bet.astype(int)
        df.paid_on_all_streets = df.paid_on_all_streets.astype(int)
        df.ready_combination.replace(to_replace=['TWO_PAIR', 'ONE_PAIR', 'HIGH_CARD', 'AIR', 'STRAIGHT', 'THREE_OF_A_KIND',
                                                 'FLUSH', 'FULL_HOUSE', 'STRAIGHT_FLUSH', 'FOUR_OF_A_KIND'],
                                     value=list(range(10)), inplace=True)
        return model.predict(df)

    def declare_action(self, valid_actions, hole_card, round_state, hand):
        features = self.__pack.collect_features() + self.__board.extract_features() + \
                   [self.__combination.ready_combination().name]
        d = dict([(n, f) for n, f in zip(get_features_names(), features)])
        #logger.info(f"Features: {pformat(d)}")

        action_classifier: str = self.__predict(d, self.__classifier)[0][0]
        action_regressor = self.__predict(d, self.__regressor)[0]

        logger.info(f"Predict: {action_classifier} {action_regressor} {valid_actions}")

        if action_classifier.lower() == 'call':
            return valid_actions[1]['action'], valid_actions[1]['amount']
        if action_classifier.lower() == 'fold':
            return valid_actions[0]['action'], valid_actions[0]['amount']
        if action_classifier.lower() == 'check':
            if valid_actions[1]['amount'] == 0:
                return valid_actions[1]['action'], valid_actions[1]['amount']
            else:
                return valid_actions[0]['action'], valid_actions[0]['amount']
        if action_classifier.lower() == 'bet' or action_classifier.lower() == 'raise':
            if valid_actions[2]['amount']['min'] != -1 and valid_actions[2]['amount']['max'] != -1:
                return valid_actions[2]['action'], min(max(valid_actions[2]['amount']['min'],
                                                           action_regressor * self.__big_blind),
                                                       valid_actions[2]['amount']['max'])
            else:
                return valid_actions[1]['action'], valid_actions[1]['amount']

    def receive_game_start_message(self, game_info):
        self.__player_name: str = game_info['seats'][game_info['player_num'] - 1]['uuid']

    def receive_round_start_message(self, round_count, hole_card, seats):
        """
        9
        ['SA', 'DQ']
        [{'name': 'fish', 'uuid': 'dkxjvyjobhbyiiaooiycre', 'stack': 130, 'state': 'participating'},
        {'name': 'model', 'uuid': 'yzjwbrgvjkiktrdsvaetjg', 'stack': 55, 'state': 'participating'}]
        """
        self.__players: Dict[str, Player] = dict([(seat['uuid'], Player(position, seat['uuid'], seat['stack']))
                                                  for position, seat in enumerate(seats)])
        cards = [Card(c[0], c[1]) for c in hole_card]
        self.__players[self.__player_name].player_cards = cards
        self.__pack = FeaturesPack(self.__players, self.__player_name, self.__big_blind)
        super().receive_round_start_message(round_count, hole_card, seats)

    def receive_street_start_message(self, street, round_state):
        if street == 'preflop':
            ss = Street.PREFLOP
        elif street == 'flop':
            ss = Street.FLOP
        elif street == 'turn':
            ss = Street.TURN
        elif street == 'river':
            ss = Street.RIVER
        else:
            raise Exception(f"Unknown street name {street}")
        cards = [Card(c[0], c[1]) for c in round_state['community_card']]
        self.__board = Board(cards)
        self.__combination = Combination(cards, self.__players[self.__player_name].player_cards)
        self.__pack.street_start(ss)
        if ss == Street.PREFLOP:
            small_blind = round_state['action_histories'][Streets.PREFLOP.value][0]['amount']
            big_blind = round_state['action_histories'][Streets.PREFLOP.value][1]['amount']

            sb_player = round_state['action_histories'][Streets.PREFLOP.value][0]['uuid']
            bb_player = round_state['action_histories'][Streets.PREFLOP.value][1]['uuid']

            sb = Action(sb_player, ActionType.SMALLBLIND, small_blind)
            bb = Action(bb_player, ActionType.BIGBLIND, big_blind)
            self.__pack.collect_action(sb)
            self.__pack.collect_action(bb)

        super().receive_street_start_message(street, round_state)

    def receive_game_update_message(self, action, round_state):
        if action['action'] == 'call':
            if action['amount'] == 0:
                action_type = ActionType.CHECK
            else:
                action_type = ActionType.CALL
        elif action['action'] == 'bet':
            action_type = ActionType.BET
        elif action['action'] == 'raise':
            if self.last_bet_size > 0:
                action_type = ActionType.RAISE
            else:
                action_type = ActionType.BET
        elif action['action'] == 'fold':
            action_type = ActionType.FOLD
        else:
            raise Exception("Unknown action type")
        a = Action(action['player_uuid'], action_type, action['amount'])
        self.__pack.collect_action(a)
        super().receive_game_update_message(action, round_state)

    def receive_round_result_message(self, winners, hand_info, round_state):
        super().receive_round_result_message(winners, hand_info, round_state)
