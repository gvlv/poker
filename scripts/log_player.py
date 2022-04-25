import random
import logging
from enum import Enum
from time import gmtime, strftime, time

from math import floor
from pypokerengine.players import BasePokerPlayer
from scripts.const import Actions, CardValues, States, Streets

logging.POKERSTARS = 60
logging.addLevelName(logging.POKERSTARS, "ps")

LOG_FILE_SIZE = 10000


def format_cards(cards):
    formatted_cards = list()
    for card in cards:
        number = card[1:]
        suit = card[0:1].lower()
        formatted_cards.append(number + suit)
    return formatted_cards


def format_hand(strength, cards):
    strength = strength.upper()
    hand = Strengths[strength].fullname + ' '

    card0 = None
    card1 = None

    if len(cards) > 0:
        card0 = CardValues['C' + cards[0]]

    if len(cards) > 1:
        card1 = CardValues['C' + cards[1]]

    if strength == Strengths.HIGHCARD.name:
        if card0 is not None:
            hand += card0.single

    if strength == Strengths.ONEPAIR.name:
        if card0 is not None:
            hand += card0.multiple

    if strength == Strengths.TWOPAIR.name:
        if card0 is not None and card1 is not None:
            hand += card0.multiple + ' and ' + card1.multiple

    if strength == Strengths.THREECARD.name:
        if card0 is not None:
            hand += card0.multiple

    if strength == Strengths.STRAIGHT.name:
        if card0 is not None and card1 is not None:
            hand += card0.multiple + ' to ' + card1.multiple

    if strength == Strengths.FLASH.name:
        if card0 is not None:
            hand += card0.single + ' high'

    if strength == Strengths.FULLHOUSE.name:
        if card0 is not None and card1 is not None:
            hand += card0.multiple + ' full of ' + card1.multiple

    if strength == Strengths.FOURCARD.name:
        if card0 is not None:
            hand += card0.multiple

    if strength == Strengths.STRAIGHTFLASH.name:
        if card0 is not None:
            hand += card0.single + ' high'

    return hand


def format_float(f):
    f = round(f, 2)
    if f - round(f) == 0:
        return int(f)
    return f


class LogPlayer(BasePokerPlayer):
    def format_amount(self, a):
        a = floor(a)
        amount = a / self.coef
        return format_float(amount)

    def ps(self, message, *args, **kws):
        if self.isEnabledFor(logging.POKERSTARS):
            self._log(logging.POKERSTARS, message, args, **kws)

    logging.Logger.ps = ps

    def rotate_logs(self, round_state):
        if not self.write_log:
            return

        date = strftime("%Y-%m-%d", gmtime())
        max_chip = int(max(self.format_amount(s['stack']) for s in round_state['seats']))
        log_file_number = str(self.log_file).zfill(4)
        # TODO: fix number of seats
        filename = f"{date} PS NLH{max_chip} 6-max USD {log_file_number}"
        file_handler = logging.FileHandler(f'log/{filename}.txt', 'w')
        formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.POKERSTARS)

        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        self.logger.addHandler(file_handler)

    def __init__(self, write_log=False, decrease_coefficient=1.):
        super().__init__()

        self.write_log = write_log
        if write_log:
            self.logger = logging.getLogger('DQN')
        else:
            self.logger = EmptyLogger()
        self.coef = decrease_coefficient

        self.hand_number = 1
        self.log_file = 1
        self.board = list()
        self.players = {}
        self.uncalled_bet = None
        self.bet = 0
        self.last_bet_size = 0

    def declare_action(self, valid_actions, hole_card, round_state, hand):
        action = random.choice(valid_actions)["action"]
        if action == "raise":
            action_info = valid_actions[2]
            amount = random.randint(action_info["amount"]["min"], action_info["amount"]["max"])
            if amount == -1:
                action = "call"
        if action == "call":
            action_info = valid_actions[1]
            amount = action_info["amount"]
        if action == "fold":
            action_info = valid_actions[0]
            amount = action_info["amount"]
        return action, amount

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        self.players = {}
        for seat in seats:
            self.players[seat['uuid']] = {'name': seat['name'], 'bet': 0}
        pass

    def receive_street_start_message(self, street, round_state):
        self.uncalled_bet = None
        self.last_bet_size = 0

        if street is not Streets.PREFLOP.value:
            self.bet = 0

        if self.players is not None:
            for player in self.players.values():
                player['bet'] = 0

        if street == Streets.PREFLOP.value:
            # TODO: Create new log file if date has been changed
            if self.hand_number % LOG_FILE_SIZE == 1:
                self.rotate_logs(round_state)
                self.log_file += 1

            current_time = strftime("%Y/%m/%d %H:%M:%S", gmtime())
            small_blind = round_state['action_histories'][Streets.PREFLOP.value][0]['amount']
            big_blind = round_state['action_histories'][Streets.PREFLOP.value][1]['amount']

            self.logger.ps(
                f"PokerStars Hand #{round(time() * 1000)}: Hold'em No Limit (${self.format_amount(small_blind)}/"
                f"${self.format_amount(big_blind)} USD) - {current_time}")
            self.hand_number += 1

            self.logger.ps(
                f"Table 'Edisona III' {6 if len(round_state['seats']) > 6 else len(round_state['seats'])}-max Seat #{round_state['dealer_btn'] + 1} "
                f"is the button")

            initial_stack = int(max(s['stack'] for s in round_state['seats']))
            for num in range(len(round_state['seats'])):
                player = round_state['seats'][num]

                if player['stack'] > 0:
                    self.logger.ps(f"Seat {num + 1}: {player['name']} (${self.format_amount(initial_stack)} in chips)")

                self.players[player['uuid']] = {'name': player['name'], 'bet': 0, 'stack': initial_stack}

            sb_player = self.players[round_state['action_histories'][Streets.PREFLOP.value][0]['uuid']]
            sb_player['bet'] = small_blind
            self.logger.ps(f"{sb_player['name']}: posts small blind ${self.format_amount(small_blind)}")

            bb_player = self.players[round_state['action_histories'][Streets.PREFLOP.value][1]['uuid']]
            bb_player['bet'] = big_blind
            self.logger.ps(f"{bb_player['name']}: posts big blind ${self.format_amount(big_blind)}")

            self.bet = big_blind

            self.uncalled_bet = {'uuid': round_state['action_histories'][Streets.PREFLOP.value][1]['uuid'],
                                 'bet': self.format_amount(big_blind - small_blind)}

            self.last_bet_size = round_state['action_histories'][Streets.PREFLOP.value][1]['amount']

            self.logger.ps(f"*** HOLE CARDS ***")

        if street == Streets.FLOP.value:
            flop = format_cards(round_state['community_card'])
            self.logger.ps(f"*** FLOP *** [{' '.join(flop)}]")
            self.board = flop
        elif street == Streets.TURN.value:
            turn = format_cards(round_state['community_card'])
            self.logger.ps(f"*** TURN *** [{' '.join(self.board)}] [{turn[3]}]")
            self.board = turn
        elif street == Streets.RIVER.value:
            river = format_cards(round_state['community_card'])
            self.logger.ps(f"*** RIVER *** [{' '.join(self.board)}] [{river[4]}]")
            self.board = river

    def receive_game_update_message(self, action, round_state):
        player = self.players[action['player_uuid']]
        seat = list(filter(lambda s: s['uuid'] == action['player_uuid'], round_state['seats']))[0]
        allin = seat['state'] == States.ALLIN

        if action['action'].lower() == Actions.FOLD:
            log = f"{player['name']}: folds"
            player['summary'] = FoldText[round_state['street'].upper()].value
        elif action['action'].lower() == Actions.CALL:
            if action['amount'] > 0:
                call = action['amount'] - player['bet']
                log = f"{player['name']}: calls ${self.format_amount(call)}"
                self.uncalled_bet = None
            else:
                log = f"{player['name']}: checks"
            if allin:
                log += " and is all-in"
        elif action['action'].lower() == Actions.RAISE:
            player['bet'] = action['amount']
            formatted_amount = self.format_amount(action['amount'])

            if self.last_bet_size > 0:
                raise_size = self.format_amount(action['amount'] - self.last_bet_size)
                self.uncalled_bet = {'uuid': action['player_uuid'], 'bet': raise_size}
                log = f"{player['name']}: raises ${raise_size} to ${formatted_amount}"

                if allin:
                    log += " and is all-in"
            else:
                log = f"{player['name']}: bets ${formatted_amount}"
                self.uncalled_bet = {'uuid': action['player_uuid'], 'bet': formatted_amount}
                if allin:
                    log += " and is all-in"

            self.last_bet_size = action['amount']

        self.logger.ps(log)

    def receive_round_result_message(self, winners, hand_info, round_state):
        participating = list(filter(lambda s: s['state'] is not States.FOLDED, round_state['seats']))
        print_show_down = len(participating) > 1
        if print_show_down:
            self.logger.ps(f"*** SHOW DOWN ***")

            seat_len = len(round_state['seats'])
            shift = round_state['small_blind_pos'] | 1
            strongest_combination = 0
            highest_card = 0
            for num in range(seat_len):
                seat = round_state['seats'][(num + shift - 1) % seat_len]
                player = self.players[seat['uuid']]
                if player['stack'] <= 0 or seat['state'] == States.FOLDED:
                    continue

                show_down = f"{seat['name']}: "

                player_hand_info = list(filter(lambda hi: hi['uuid'] == seat['uuid'], hand_info))
                info = player_hand_info[0]["hand"]
                seat_strength = int(Strengths[info['hand']['strength']])
                seat_highest_card = sorted([int(CardValues['C' + card]) for card in info['hand']['strongest_cards']],
                                           reverse=True)[0]

                if seat_strength > strongest_combination or \
                        (seat_strength == strongest_combination and seat_highest_card >= highest_card):

                    strongest_combination = seat_strength
                    highest_card = seat_highest_card
                    card_list = ' '.join(format_cards(info["list"]))
                    formatted_hand = format_hand(info['hand']['strength'], info['hand']['strongest_cards'])
                    show_down += f'shows [{card_list}] ({formatted_hand})'
                else:
                    show_down += 'mucks hand'
                    player['summary'] = 'mucked'

                self.logger.ps(show_down)

        pot = round_state['pot']['main']['amount']

        if self.uncalled_bet is not None:
            player_name = self.players[self.uncalled_bet['uuid']]['name']
            self.logger.ps(f"Uncalled bet (${self.uncalled_bet['bet']}) returned to {player_name}")

            pot -= self.uncalled_bet['bet'] * self.coef

        for winner in winners:
            player = self.players[winner['uuid']]
            prize = self._calculate_prize(pot, winner, winners, player['stack'])
            self.logger.ps(f"{player['name']} collected ${self.format_amount(prize)} from pot")

        self.logger.ps('*** SUMMARY ***')
        self.logger.ps(f"Total pot ${self.format_amount(pot)} | Rake $0 ")

        for num in range(len(round_state['seats'])):
            seat = round_state['seats'][num]
            player = self.players[seat['uuid']]
            if player['stack'] <= 0:
                continue

            summary = f"Seat {num + 1}: {seat['name']}"
            if num == round_state['dealer_btn']:
                summary += ' (button)'
            if num == round_state['small_blind_pos']:
                summary += ' (small blind)'
            if num == round_state['big_blind_pos']:
                summary += ' (big blind)'

            is_winner = False
            player_hand_info = list(filter(lambda hi: hi['uuid'] == seat['uuid'], hand_info))

            for winner in winners:
                if winner['uuid'] == seat['uuid']:
                    is_winner = True
                    prize = self._calculate_prize(pot, winner, winners, player['stack'])
                    if len(player_hand_info) > 0 and 'list' in player_hand_info[0]['hand']:
                        info = player_hand_info[0]["hand"]
                        card_list = ' '.join(format_cards(info["list"]))
                        formatted_hand = format_hand(info['hand']['strength'], info['hand']['strongest_cards'])
                        summary += f' showed [{card_list}] and won (${self.format_amount(prize)}) with {formatted_hand}'
                    else:
                        summary += f' collected (${self.format_amount(prize)})'

            if not is_winner:
                if 'summary' in player:
                    summary += f' {player["summary"]}'
                elif len(player_hand_info) > 0 and 'list' in player_hand_info[0]['hand']:
                    info = player_hand_info[0]["hand"]
                    card_list = ' '.join(format_cards(info["list"]))
                    formatted_hand = format_hand(info['hand']['strength'], info['hand']['strongest_cards'])
                    summary += f' showed [{card_list}] and lost with {formatted_hand}'

            self.logger.ps(summary)

        for i in range(4):
            self.logger.ps("")

    @staticmethod
    def _calculate_prize(pot, winner, winners, stack):
        prize = pot / len(winners)
        return prize


class FoldText(Enum):
    PREFLOP = "folded before Flop"
    FLOP = "folded on the Flop"
    TURN = "folded on the Turn"
    RIVER = "folded on the River"
    SHOW_DOWN = "show down"


class Strengths(Enum):
    HIGHCARD = 0, "high card"
    ONEPAIR = 1, "a pair of"
    TWOPAIR = 2, "two pair,"
    THREECARD = 3, "three of a kind,"
    STRAIGHT = 4, "a straight,"
    FLASH = 5, "a flush,"
    FULLHOUSE = 6, "a full house,"
    FOURCARD = 7, "four of a kind,"
    STRAIGHTFLASH = 8, "a straight flush,"

    def __new__(cls, value, name):
        member = object.__new__(cls)
        member._value_ = value
        member.fullname = name
        return member

    def __int__(self):
        return self.value


class EmptyLogger:
    def ps(self, message, *args, **kws):
        pass
