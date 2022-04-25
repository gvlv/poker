import math

from scripts.log_player import LogPlayer, Streets
from scripts.const import Actions
from scripts.strategy.Preflop import Preflop
from scripts.strategy.Postflop import Postflop
from scripts.strategy.postflop_util import Pot, Strategy
from scripts.util import format_hole, get_seat_name


class StrategyPlayer(LogPlayer):

    def __init__(self, write_log=False, decrease_coefficient=100.):
        super().__init__(write_log, decrease_coefficient)
        self.raiser = None
        self.limper = None
        self.last_action = None
        self.bet_count = 0
        self.bb = 0
        self.pot_type = None

    def declare_action(self, valid_actions, hole_card, round_state, hand):
        player_seat = get_seat_name(len(round_state['seats']), round_state['next_player'], round_state['dealer_btn'])

        raiser_seat = None
        if self.raiser is not None:
            raiser_seat = get_seat_name(len(round_state['seats']), self.raiser, round_state['dealer_btn'])

        if round_state['street'] == Streets.PREFLOP.value:
            limper_seat = None
            if self.limper is not None:
                limper_seat = get_seat_name(len(round_state['seats']), self.limper, round_state['dealer_btn'])

            self.bb = round_state['action_histories'][Streets.PREFLOP.value][1]['amount']
            hc = format_hole(hole_card)
            player_uuid = round_state['seats'][round_state['next_player']]['uuid']

            preflop_strategy = Preflop(player_seat, raiser_seat, limper_seat, self.bb, self.bet_count,
                                       self.last_bet_size, hc,
                                       valid_actions, player_uuid, round_state['action_histories'])
            action, amount = preflop_strategy.declare_action()
            self.last_action = action
        else:
            seats = list(filter(lambda s: s['state'] is not 'folded', round_state['seats']))
            preflop_raises = list(filter(lambda a: a['action'] == 'RAISE', round_state['action_histories']['preflop']))

            if self.pot_type is None:
                if len(seats) > 2:
                    self.pot_type = Pot.MULTIPOT
                else:
                    if len(preflop_raises) >= 2:
                        self.pot_type = Pot.THREE_BET
                    else:
                        self.pot_type = Pot.RAISE

            strategy = Strategy.RAISER if self.last_action == Actions.RAISE else Strategy.CALLER

            player = {'position': player_seat}

            raiser = None
            if raiser_seat is not None:
                raiser = {'position': raiser_seat}

            pot = round_state['pot']['main']['amount']
            last_bet = self.last_bet_size
            max_available_bet = valid_actions[2]['amount']['max']
            players = list(filter(lambda s: s is not 'folded', round_state['seats']))

            postflop_strategy = Postflop(self.pot_type, strategy, hand, hole_card, round_state['community_card'],
                                         round_state['street'], player, raiser, pot, last_bet, max_available_bet,
                                         players, round_state['action_histories'])

            # Если на флопе размер банка превышает размер стэка, то стратегия играет через пуш любую руку
            # (если в стратегию бот ставит ставку, то стратегия играет рейз пуш)
            if round_state['street'] == Streets.FLOP.value and pot >= self.bb * 100:
                action = Actions.RAISE
                amount = valid_actions[2]['amount']['max']
            else:
                action, amount = postflop_strategy.declare_action()

        amount = math.floor(amount)

        if action == Actions.RAISE:
            raise_min = valid_actions[2]['amount']['min']
            raise_max = valid_actions[2]['amount']['max']

            if valid_actions[2]['amount']['min'] == valid_actions[2]['amount']['max'] == -1 or raise_max <= 0:
                action = Actions.CALL
                amount = valid_actions[1]['amount']
            else:
                amount = max(amount, raise_min)
                amount = min(amount, raise_max)

        if action == Actions.CALL:
            street_history = round_state['action_histories'][round_state['street']]
            raises = list(filter(lambda a: a['action'] in ['RAISE', 'SMALLBLIND', 'BIGBLIND'], street_history))
            if amount == 0:
                if len(raises) > 0:
                    amount = valid_actions[1]['amount']
            else:
                if len(raises) == 0:
                    amount = 0
                else:
                    amount = max(amount, valid_actions[1]['amount'])

        return action, amount

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        self.last_action = None
        self.pot_type = None
        super().receive_round_start_message(round_count, hole_card, seats)

    def receive_street_start_message(self, street, round_state):
        self.raiser = None
        self.limper = None
        self.bet_count = 1
        super().receive_street_start_message(street, round_state)

    def receive_game_update_message(self, action, round_state):
        if action['action'].lower() == Actions.CALL and self.limper is None and action['amount'] == self.bb:
            self.limper = round_state['next_player']

        if action['action'].lower() == Actions.RAISE:
            self.raiser = round_state['next_player']
            self.bet_count += 1

        super().receive_game_update_message(action, round_state)

    def receive_round_result_message(self, winners, hand_info, round_state):
        super().receive_round_result_message(winners, hand_info, round_state)
