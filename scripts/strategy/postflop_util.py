from itertools import groupby

from scripts.const import Actions, Seats, Streets
from scripts.util import _card_value, _filter_values, _sort_cards_by_value, _sort_cards_by_suit


class Pot:
    RAISE = 'raise'
    THREE_BET = '3bet'
    MULTIPOT = 'multipot'


class Strategy:
    RAISER = 'raiser'
    CALLER = 'caller'


class Hand:
    TOP_TWO_PAIR_PLUS = 14
    TWO_PAIR = 13
    TOP_PAIR_TOP_KICKER = 12
    TOP_PAIR_K_KICKER = 11
    TOP_PAIR_Q_KICKER = 10
    TOP_PAIR = 9
    OESD_FLASH_DRAW = 8
    SECOND_PAIR = 7
    THIRD_PAIR = 6
    TWO_OVERCARDS_WITH_A = 5
    TWO_OVERCARDS = 4
    GUTSHOT = 3
    DRY_BOARD = 2
    REST = 1


strategies = {
    Pot.RAISE: {
        Strategy.RAISER: {
            Hand.TOP_TWO_PAIR_PLUS: lambda postflop: _raise_raiser_top_two_pair_plus(postflop),
            Hand.TWO_PAIR: lambda postflop: _raise_raiser_two_pair(postflop),
            Hand.TOP_PAIR_TOP_KICKER: lambda postflop: _raise_raiser_top_pair_top_kicker(postflop),
            Hand.TOP_PAIR_K_KICKER: lambda postflop: _raise_raiser_top_pair_k_kicker(postflop),
            Hand.TOP_PAIR_Q_KICKER: lambda postflop: _raise_raiser_top_pair_q_kicker(postflop),
            Hand.TOP_PAIR: lambda postflop: _raise_raiser_top_pair(postflop),
            Hand.OESD_FLASH_DRAW: lambda postflop: _raise_raiser_oesd_flash_draw(postflop),
            Hand.SECOND_PAIR: lambda postflop: _raise_raiser_second_pair(postflop),
            Hand.THIRD_PAIR: lambda postflop: _raise_raiser_third_pair(postflop),
            Hand.TWO_OVERCARDS_WITH_A: lambda postflop: _raise_raiser_two_overcards_with_a(postflop),
            Hand.TWO_OVERCARDS: lambda postflop: _raise_raiser_two_overcards(postflop),
            Hand.GUTSHOT: lambda postflop: _raise_raiser_gutshot(postflop),
            Hand.DRY_BOARD: lambda postflop: _raise_raiser_dry_board(postflop),
            Hand.REST: lambda postflop: _raise_raiser_rest(postflop)
        },
        Strategy.CALLER: {
            Hand.TOP_TWO_PAIR_PLUS: lambda postflop: _raise_caller_top_two_pair_plus(postflop),
            Hand.TWO_PAIR: lambda postflop: _raise_caller_two_pair(postflop),
            Hand.TOP_PAIR_TOP_KICKER: lambda postflop: _raise_caller_top_pair_top_kicker(postflop),
            Hand.TOP_PAIR_K_KICKER: lambda postflop: _raise_caller_top_pair_k_kicker(postflop),
            Hand.TOP_PAIR_Q_KICKER: lambda postflop: _raise_caller_top_pair_q_kicker(postflop),
            Hand.TOP_PAIR: lambda postflop: _raise_caller_top_pair(postflop),
            Hand.OESD_FLASH_DRAW: lambda postflop: _raise_caller_oesd_flash_draw(postflop),
            Hand.SECOND_PAIR: lambda postflop: _raise_caller_second_pair(postflop),
            Hand.THIRD_PAIR: lambda postflop: _raise_caller_third_pair(postflop),
            Hand.TWO_OVERCARDS_WITH_A: lambda postflop: _raise_caller_two_overcards_with_a(postflop),
            Hand.TWO_OVERCARDS: lambda postflop: _raise_caller_two_overcards(postflop),
            Hand.GUTSHOT: lambda postflop: _raise_caller_gutshot(postflop),
            Hand.DRY_BOARD: lambda postflop: _raise_caller_dry_board(postflop),
            Hand.REST: lambda postflop: _raise_caller_rest(postflop)
        }
    },
    Pot.THREE_BET: {
        Strategy.RAISER: {
            Hand.TOP_TWO_PAIR_PLUS: lambda postflop: _3bet_raiser_top_two_pair_plus(postflop),
            Hand.TWO_PAIR: lambda postflop: _3bet_raiser_two_pair(postflop),
            Hand.TOP_PAIR_TOP_KICKER: lambda postflop: _3bet_raiser_top_pair_top_kicker(postflop),
            Hand.TOP_PAIR_K_KICKER: lambda postflop: _3bet_raiser_top_pair_k_kicker(postflop),
            Hand.TOP_PAIR_Q_KICKER: lambda postflop: _3bet_raiser_top_pair_q_kicker(postflop),
            Hand.TOP_PAIR: lambda postflop: _3bet_raiser_top_pair(postflop),
            Hand.OESD_FLASH_DRAW: lambda postflop: _3bet_raiser_oesd_flash_draw(postflop),
            Hand.SECOND_PAIR: lambda postflop: _3bet_raiser_second_pair(postflop),
            Hand.THIRD_PAIR: lambda postflop: _3bet_raiser_third_pair(postflop),
            Hand.TWO_OVERCARDS_WITH_A: lambda postflop: _3bet_raiser_two_overcards_with_a(postflop),
            Hand.TWO_OVERCARDS: lambda postflop: _3bet_raiser_two_overcards(postflop),
            Hand.GUTSHOT: lambda postflop: _3bet_raiser_gutshot(postflop),
            Hand.DRY_BOARD: lambda postflop: _3bet_raiser_dry_board(postflop),
            Hand.REST: lambda postflop: _3bet_raiser_rest(postflop)
        },
        Strategy.CALLER: {
            Hand.TOP_TWO_PAIR_PLUS: lambda postflop: _3bet_caller_top_two_pair_plus(postflop),
            Hand.TWO_PAIR: lambda postflop: _3bet_caller_two_pair(postflop),
            Hand.TOP_PAIR_TOP_KICKER: lambda postflop: _3bet_caller_top_pair_top_kicker(postflop),
            Hand.TOP_PAIR_K_KICKER: lambda postflop: _3bet_caller_top_pair_k_kicker(postflop),
            Hand.TOP_PAIR_Q_KICKER: lambda postflop: _3bet_caller_top_pair_q_kicker(postflop),
            Hand.TOP_PAIR: lambda postflop: _3bet_caller_top_pair(postflop),
            Hand.OESD_FLASH_DRAW: lambda postflop: _3bet_caller_oesd_flash_draw(postflop),
            Hand.SECOND_PAIR: lambda postflop: _3bet_caller_second_pair(postflop),
            Hand.THIRD_PAIR: lambda postflop: _3bet_caller_third_pair(postflop),
            Hand.TWO_OVERCARDS_WITH_A: lambda postflop: _3bet_caller_two_overcards_with_a(postflop),
            Hand.TWO_OVERCARDS: lambda postflop: _3bet_caller_two_overcards(postflop),
            Hand.GUTSHOT: lambda postflop: _3bet_caller_gutshot(postflop),
            Hand.DRY_BOARD: lambda postflop: _3bet_caller_dry_board(postflop),
            Hand.REST: lambda postflop: _3bet_caller_rest(postflop)
        }
    },
    Pot.MULTIPOT: {
        Strategy.RAISER: {
            Hand.TOP_TWO_PAIR_PLUS: lambda postflop: _multipot_raiser_top_two_pair_plus(postflop),
            Hand.TWO_PAIR: lambda postflop: _multipot_raiser_two_pair(postflop),
            Hand.TOP_PAIR_TOP_KICKER: lambda postflop: _multipot_raiser_top_pair_top_kicker(postflop),
            Hand.TOP_PAIR_K_KICKER: lambda postflop: _multipot_raiser_top_pair_k_kicker(postflop),
            Hand.TOP_PAIR_Q_KICKER: lambda postflop: _multipot_raiser_top_pair_q_kicker(postflop),
            Hand.TOP_PAIR: lambda postflop: _multipot_raiser_top_pair(postflop),
            Hand.OESD_FLASH_DRAW: lambda postflop: _multipot_raiser_oesd_flash_draw(postflop),
            Hand.SECOND_PAIR: lambda postflop: _multipot_raiser_second_pair(postflop),
            Hand.THIRD_PAIR: lambda postflop: _multipot_raiser_third_pair(postflop),
            Hand.TWO_OVERCARDS_WITH_A: lambda postflop: _multipot_raiser_two_overcards_with_a(postflop),
            Hand.TWO_OVERCARDS: lambda postflop: _multipot_raiser_two_overcards(postflop),
            Hand.GUTSHOT: lambda postflop: _multipot_raiser_gutshot(postflop),
            Hand.DRY_BOARD: lambda postflop: _multipot_raiser_dry_board(postflop),
            Hand.REST: lambda postflop: _multipot_raiser_rest(postflop)
        },
        Strategy.CALLER: {
            Hand.TOP_TWO_PAIR_PLUS: lambda postflop: _multipot_caller_top_two_pair_plus(postflop),
            Hand.TWO_PAIR: lambda postflop: _multipot_caller_two_pair(postflop),
            Hand.TOP_PAIR_TOP_KICKER: lambda postflop: _multipot_caller_top_pair_top_kicker(postflop),
            Hand.TOP_PAIR_K_KICKER: lambda postflop: _multipot_caller_top_pair_k_kicker(postflop),
            Hand.TOP_PAIR_Q_KICKER: lambda postflop: _multipot_caller_top_pair_q_kicker(postflop),
            Hand.TOP_PAIR: lambda postflop: _multipot_caller_top_pair(postflop),
            Hand.OESD_FLASH_DRAW: lambda postflop: _multipot_caller_oesd_flash_draw(postflop),
            Hand.SECOND_PAIR: lambda postflop: _multipot_caller_second_pair(postflop),
            Hand.THIRD_PAIR: lambda postflop: _multipot_caller_third_pair(postflop),
            Hand.TWO_OVERCARDS_WITH_A: lambda postflop: _multipot_caller_two_overcards_with_a(postflop),
            Hand.TWO_OVERCARDS: lambda postflop: _multipot_caller_two_overcards(postflop),
            Hand.GUTSHOT: lambda postflop: _multipot_caller_gutshot(postflop),
            Hand.DRY_BOARD: lambda postflop: _multipot_caller_dry_board(postflop),
            Hand.REST: lambda postflop: _multipot_caller_rest(postflop)
        }
    }
}


def _x_fold(raiser):
    if raiser is None:
        return Actions.CALL, 0
    return Actions.FOLD, 0


def _x_call(raiser, last_bet):
    if raiser is None:
        return Actions.CALL, last_bet
    return Actions.FOLD, 0


# Raise-Raiser


def _raise_raiser_top_two_pair_plus(postflop):
    if postflop.raiser is None:
        return Actions.RAISE, 0.75 * postflop.pot
    if postflop.street == Streets.FLOP.value:
        efficient_stack = min(postflop.players, key=lambda p: p['stack'])['stack']
        if efficient_stack / postflop.pot > 1.2:
            return Actions.RAISE, 2.7 * postflop.last_bet
        return Actions.RAISE, postflop.max_bet
    if postflop.street == Streets.TURN.value:
        return Actions.RAISE, postflop.max_bet
    if postflop.street == Streets.RIVER.value:
        if postflop.hand['strength'] in ['HIGHCARD', 'ONEPAIR', 'TWOPAIR', 'THREECARD']:
            for suit, cards in groupby(_sort_cards_by_suit(postflop.community), lambda c: c[0:1]):
                if len(list(cards)) >= 3:
                    return Actions.FOLD, 0
        return Actions.CALL, postflop.last_bet


def _raise_raiser_two_pair(postflop):
    if postflop.raiser is None:
        return Actions.RAISE, 0.75 * postflop.pot
    if postflop.street == Streets.FLOP.value:
        return Actions.CALL, postflop.last_bet
    if postflop.street == Streets.TURN.value:
        return Actions.CALL, postflop.last_bet
    if postflop.street == Streets.RIVER.value:
        return Actions.FOLD, 0


def _raise_raiser_top_pair_top_kicker(postflop):
    if postflop.raiser is None:
        return Actions.RAISE, 0.75 * postflop.pot
    if postflop.street == Streets.FLOP.value:
        if postflop.street_round <= 2:
            return Actions.CALL, postflop.last_bet
        return Actions.FOLD, 0
    if postflop.street == Streets.TURN.value:
        if postflop.street_round == 1:
            return Actions.CALL, postflop.last_bet
        return Actions.FOLD, 0
    if postflop.street == Streets.RIVER.value:
        return Actions.FOLD, 0


def _raise_raiser_top_pair_k_kicker(postflop):
    if postflop.raiser is None:
        if postflop.street == Streets.RIVER.value:
            sorted_cards = _sort_cards_by_suit(postflop.hole + postflop.community[:-1])
            for suit, cards in groupby(sorted_cards, lambda c: c[0:1]):
                if len(list(cards)) == 4:
                    return _x_call(postflop.raiser, postflop.last_bet)

            sorted_cards = _sort_cards_by_value(postflop.hole + postflop.community[:-1])
            sorted_cards = list(map(lambda c: _card_value(c), dict.fromkeys(_filter_values(sorted_cards))))

            # Check if Ace may finish postflop.street
            if 14 in sorted_cards:
                sorted_cards.append(1)

            for i in range(0, len(sorted_cards) - 3):
                gaps = 0
                for j in range(0, 3):
                    gaps += (sorted_cards[i + j] - sorted_cards[i + j + 1] - 1)
                if gaps < 2:
                    return _x_call(postflop.raiser, postflop.last_bet)

            return _x_fold(postflop.raiser)
        return Actions.RAISE, 0.75 * postflop.pot
    if postflop.street == Streets.FLOP.value:
        if postflop.street_round <= 2:
            return Actions.CALL, postflop.last_bet
        return Actions.FOLD, 0
    return Actions.FOLD, 0


def _raise_raiser_top_pair_q_kicker(postflop):
    return _raise_raiser_top_pair_k_kicker(postflop)


def _raise_raiser_top_pair(postflop):
    return _raise_raiser_top_pair_k_kicker(postflop)


def _raise_raiser_oesd_flash_draw(postflop):
    if postflop.raiser is None:
        if postflop.street == Streets.RIVER.value:
            return _x_fold(postflop.raiser)
        return Actions.RAISE, 0.75 * postflop.pot
    if postflop.street == Streets.FLOP.value:
        if postflop.street_round == 1:
            return Actions.CALL, postflop.last_bet
        if Seats.index(postflop.player['position']) < Seats.index(postflop.raiser['position']):
            return Actions.FOLD, 0
        return Actions.CALL, postflop.last_bet
    if postflop.street == Streets.TURN.value:
        if Seats.index(postflop.player['position']) < Seats.index(postflop.raiser['position']):
            return Actions.FOLD, 0
        return Actions.CALL, postflop.last_bet
    if postflop.street == Streets.RIVER.value:
        return Actions.FOLD, 0


def _raise_raiser_second_pair(postflop):
    if postflop.raiser is None:
        if postflop.street == Streets.RIVER.value:
            return _x_fold(postflop.raiser)
        return Actions.RAISE, 0.5 * postflop.pot
    if postflop.street == Streets.FLOP.value:
        if postflop.street_round == 1:
            return Actions.CALL, postflop.last_bet
        return Actions.FOLD, 0
    return Actions.FOLD, 0


def _raise_raiser_third_pair(postflop):
    if postflop.raiser is None:
        if postflop.street == Streets.FLOP.value:
            return Actions.RAISE, 0.5 * postflop.pot
        if postflop.street == Streets.TURN.value:
            return Actions.RAISE, 0.75 * postflop.pot
        if postflop.street == Streets.RIVER.value:
            return _x_fold(postflop.raiser)
    return Actions.FOLD, 0


def _raise_raiser_two_overcards_with_a(postflop):
    return _raise_raiser_third_pair(postflop)


def _raise_raiser_two_overcards(postflop):
    return _raise_raiser_third_pair(postflop)


def _raise_raiser_gutshot(postflop):
    return _raise_raiser_third_pair(postflop)


def _raise_raiser_dry_board(postflop):
    if postflop.raiser is None:
        if postflop.street == Streets.FLOP.value:
            return Actions.RAISE, 0.33 * postflop.pot
        return _x_fold(postflop.raiser)
    return Actions.FOLD, 0


def _raise_raiser_rest(postflop):
    return _x_fold(postflop.raiser)


# Raise-Caller


def _raise_caller_top_two_pair_plus(postflop):
    if postflop.street == Streets.FLOP.value:
        if postflop.raiser is not None:
            return Actions.RAISE, 3 * postflop.last_bet
        return Actions.CALL, 0
    if postflop.street == Streets.TURN.value:
        return Actions.RAISE, 0.75 * postflop.pot
    if postflop.street == Streets.RIVER.value:
        return Actions.RAISE, postflop.max_bet


def _raise_caller_two_pair(postflop):
    if postflop.street == Streets.FLOP.value:
        if postflop.raiser is not None:
            return Actions.RAISE, 3 * postflop.last_bet
        return Actions.CALL, 0
    if postflop.street == Streets.TURN.value:
        return Actions.RAISE, 0.75 * postflop.pot
    if postflop.street == Streets.RIVER.value:
        for suit, cards in groupby(_sort_cards_by_suit(postflop.community), lambda c: c[0:1]):
            if len(list(cards)) >= 3:
                return _x_fold(postflop.raiser)

        sorted_cards = list(
            map(lambda c: _card_value(c), dict.fromkeys(_filter_values(_sort_cards_by_value(postflop.hole + postflop.community[:-1])))))

        # Check if Ace may finish postflop.street
        if 14 in sorted_cards:
            sorted_cards.append(1)

        for i in range(0, len(sorted_cards) - 3):
            gaps = 0
            for j in range(0, 3):
                gaps += (sorted_cards[i + j] - sorted_cards[i + j + 1] - 1)
            if gaps < 2:
                return _x_fold(postflop.raiser)

        return Actions.RAISE, postflop.max_bet


def _raise_caller_top_pair_top_kicker(postflop):
    if postflop.street == Streets.RIVER.value:
        for suit, cards in groupby(_sort_cards_by_suit(postflop.community), lambda c: c[0:1]):
            if len(list(cards)) >= 3:
                return _x_fold(postflop.raiser)
    return Actions.CALL, postflop.last_bet


def _raise_caller_top_pair_k_kicker(postflop):
    return _raise_caller_top_pair_top_kicker(postflop)


def _raise_caller_top_pair_q_kicker(postflop):
    if postflop.street == Streets.FLOP.value or postflop.street == Streets.TURN.value:
        return Actions.CALL, postflop.last_bet
    return Actions.FOLD, 0


def _raise_caller_top_pair(postflop):
    return _raise_caller_top_pair_q_kicker(postflop)


def _raise_caller_oesd_flash_draw(postflop):
    if postflop.street == Streets.FLOP.value:
        if postflop.raiser is not None:
            return Actions.RAISE, 3 * postflop.last_bet
        return Actions.CALL, 0
    if postflop.street == Streets.TURN.value:
        return Actions.RAISE, 0.75 * postflop.pot
    if postflop.street == Streets.RIVER.value:
        return Actions.FOLD, 0


def _raise_caller_second_pair(postflop):
    if postflop.street == Streets.FLOP.value:
        return Actions.CALL, postflop.last_bet
    for suit, cards in groupby(_sort_cards_by_suit(postflop.community), lambda c: c[0:1]):
        if len(list(cards)) >= 4:
            return Actions.CALL, postflop.last_bet
    return Actions.FOLD, 0


def _raise_caller_third_pair(postflop):
    if postflop.street == Streets.FLOP.value:
        return Actions.CALL, postflop.last_bet
    return Actions.FOLD, 0


def _raise_caller_two_overcards_with_a(postflop):
    return _raise_caller_third_pair(postflop)


def _raise_caller_two_overcards(postflop):
    return _x_fold(postflop.raiser)


def _raise_caller_gutshot(postflop):
    return _raise_caller_third_pair(postflop)


def _raise_caller_dry_board(postflop):
    return _raise_caller_two_overcards(postflop)


def _raise_caller_rest(postflop):
    return _raise_caller_two_overcards(postflop)


# 3bet-Raiser


def _3bet_raiser_top_two_pair_plus(postflop):
    if postflop.raiser is None:
        if postflop.street == Streets.FLOP.value or postflop.street == Streets.TURN.value:
            return Actions.RAISE, 0.75 * postflop.pot
    return Actions.RAISE, postflop.max_bet


def _3bet_raiser_two_pair(postflop):
    return _3bet_raiser_top_two_pair_plus(postflop)


def _3bet_raiser_top_pair_top_kicker(postflop):
    return _3bet_raiser_top_two_pair_plus(postflop)


def _3bet_raiser_top_pair_k_kicker(postflop):
    if postflop.raiser is None:
        if postflop.street == Streets.RIVER.value:
            sorted_cards = _sort_cards_by_suit(postflop.hole + postflop.community[:-1])

            for suit, cards in groupby(sorted_cards, lambda c: c[0:1]):
                if len(list(cards)) == 4:
                    return _x_call(postflop.raiser, postflop.last_bet)

            sorted_cards = _sort_cards_by_value(postflop.hole + postflop.community[:-1])
            sorted_cards = list(map(lambda c: _card_value(c), dict.fromkeys(_filter_values(sorted_cards))))

            # Check if Ace may finish postflop.street
            if 14 in sorted_cards:
                sorted_cards.append(1)

            for i in range(0, len(sorted_cards) - 3):
                gaps = 0
                for j in range(0, 3):
                    gaps += (sorted_cards[i + j] - sorted_cards[i + j + 1] - 1)
                if gaps < 2:
                    return _x_call(postflop.raiser, postflop.last_bet)

            return _x_fold(postflop.raiser)
        return Actions.RAISE, 0.5 * postflop.pot
    return Actions.CALL, postflop.last_bet


def _3bet_raiser_top_pair_q_kicker(postflop):
    return _3bet_raiser_top_pair_k_kicker(postflop)


def _3bet_raiser_top_pair(postflop):
    return _3bet_raiser_top_pair_k_kicker(postflop)


def _3bet_raiser_oesd_flash_draw(postflop):
    if postflop.raiser is None:
        if postflop.street == Streets.RIVER.value:
            return _x_fold(postflop.raiser)
        return Actions.RAISE, 0.75 * postflop.pot
    if postflop.street == Streets.FLOP.value:
        return Actions.CALL, postflop.last_bet
    raises = []
    for key in postflop.history:
        raises.extend(postflop.history[key])
    raises = filter(lambda a: a['action'] in ['RAISE', 'SMALLBLIND', 'BIGBLIND'], raises)
    raises = list(sorted(raises, key=lambda a: a['amount'], reverse=True))
    if len(raises) > 1 and raises[0]['amount'] <= 2 * raises[1]['amount']:
        return Actions.CALL, postflop.last_bet
    return Actions.FOLD, 0


def _3bet_raiser_second_pair(postflop):
    if postflop.raiser is None:
        if postflop.street == Streets.RIVER.value:
            return _x_fold(postflop.raiser)
        return Actions.RAISE, 0.33 * postflop.pot
    if postflop.street == Streets.FLOP.value:
        if postflop.street_round == 1:
            return Actions.CALL, postflop.last_bet
        return Actions.FOLD, 0
    return Actions.FOLD, 0


def _3bet_raiser_third_pair(postflop):
    if postflop.raiser is None:
        if postflop.street == Streets.RIVER.value:
            return _x_fold(postflop.raiser)
        return Actions.RAISE, 0.5 * postflop.pot
    return Actions.FOLD, 0


def _3bet_raiser_two_overcards_with_a(postflop):
    return _3bet_raiser_third_pair(postflop)


def _3bet_raiser_two_overcards(postflop):
    return _3bet_raiser_third_pair(postflop)


def _3bet_raiser_gutshot(postflop):
    return _3bet_raiser_third_pair(postflop)


def _3bet_raiser_dry_board(postflop):
    if postflop.raiser is None:
        if postflop.street == Streets.FLOP.value:
            return Actions.RAISE, 0.33 * postflop.pot
        return _x_fold(postflop.raiser)
    return Actions.FOLD, 0


def _3bet_raiser_rest(postflop):
    if postflop.raiser is None:
        return _x_fold(postflop.raiser)
    return Actions.FOLD, 0


# 3bet-Caller


def _3bet_caller_top_two_pair_plus(postflop):
    if postflop.street == Streets.FLOP.value:
        if postflop.raiser is not None:
            return Actions.RAISE, 3 * postflop.last_bet
        return Actions.CALL, 0
    return Actions.RAISE, postflop.max_bet


def _3bet_caller_two_pair(postflop):
    return Actions.CALL, postflop.last_bet


def _3bet_caller_top_pair_top_kicker(postflop):
    return _3bet_caller_two_pair(postflop)


def _3bet_caller_top_pair_k_kicker(postflop):
    return _3bet_caller_two_pair(postflop)


def _3bet_caller_top_pair_q_kicker(postflop):
    return _3bet_caller_two_pair(postflop)


def _3bet_caller_top_pair(postflop):
    if postflop.street == Streets.FLOP.value or postflop.street == Streets.TURN.value:
        return Actions.CALL, postflop.last_bet
    return Actions.FOLD, 0


def _3bet_caller_oesd_flash_draw(postflop):
    return _3bet_caller_two_pair(postflop)


def _3bet_caller_second_pair(postflop):
    return _x_fold(postflop.raiser)


def _3bet_caller_third_pair(postflop):
    return _3bet_caller_second_pair(postflop)


def _3bet_caller_two_overcards_with_a(postflop):
    return _3bet_caller_second_pair(postflop)


def _3bet_caller_two_overcards(postflop):
    return _3bet_caller_second_pair(postflop)


def _3bet_caller_gutshot(postflop):
    if postflop.street == Streets.FLOP.value:
        return Actions.CALL, postflop.last_bet
    return Actions.FOLD, 0


def _3bet_caller_dry_board(postflop):
    return _3bet_caller_second_pair(postflop)


def _3bet_caller_rest(postflop):
    return _3bet_caller_second_pair(postflop)


# Multipot-Raiser


def _multipot_raiser_top_two_pair_plus(postflop):
    if postflop.raiser is None:
        return Actions.RAISE, 0.75 * postflop.pot
    if postflop.street == Streets.RIVER.value:
        if postflop.hand['strength'] in ['HIGHCARD', 'ONEPAIR', 'TWOPAIR', 'THREECARD']:
            for suit, cards in groupby(_sort_cards_by_suit(postflop.community), lambda c: c[0:1]):
                if len(list(cards)) >= 3:
                    return Actions.FOLD, 0
        return Actions.CALL, postflop.last_bet
    return Actions.RAISE, postflop.max_bet


def _multipot_raiser_two_pair(postflop):
    if postflop.raiser is None:
        if postflop.street == Streets.RIVER.value:
            for suit, cards in groupby(_sort_cards_by_suit(postflop.community), lambda c: c[0:1]):
                if len(list(cards)) >= 3:
                    return _x_fold(postflop.raiser)
        return Actions.RAISE, 0.75 * postflop.pot
    if postflop.street == Streets.FLOP.value and postflop.street_round <= 2:
        return Actions.CALL, postflop.last_bet
    return Actions.FOLD, 0


def _multipot_raiser_top_pair_top_kicker(postflop):
    if postflop.raiser is None:
        if postflop.street == Streets.RIVER.value:
            for suit, cards in groupby(_sort_cards_by_suit(postflop.community), lambda c: c[0:1]):
                if len(list(cards)) >= 3:
                    return _x_fold(postflop.raiser)
        return Actions.RAISE, 0.75 * postflop.pot
    return Actions.FOLD, 0


def _multipot_raiser_top_pair_k_kicker(postflop):
    if postflop.raiser is None:
        if postflop.street == Streets.RIVER.value:
            return _x_fold(postflop.raiser)
        return Actions.RAISE, 0.75 * postflop.pot
    return Actions.FOLD, 0


def _multipot_raiser_top_pair_q_kicker(postflop):
    return _multipot_raiser_top_pair_k_kicker(postflop)


def _multipot_raiser_top_pair(postflop):
    return _multipot_raiser_top_pair_k_kicker(postflop)


def _multipot_raiser_oesd_flash_draw(postflop):
    if postflop.raiser is None:
        if postflop.street == Streets.RIVER.value:
            return _x_fold(postflop.raiser)
        return Actions.RAISE, 0.75 * postflop.pot
    if postflop.street == Streets.FLOP.value:
        if postflop.street_round == 1:
            return Actions.CALL, postflop.last_bet
        if Seats.index(postflop.player['position']) < Seats.index(postflop.raiser['position']):
            return Actions.FOLD, 0
        return Actions.CALL, postflop.last_bet
    if postflop.street == Streets.TURN.value:
        if Seats.index(postflop.player['position']) < Seats.index(postflop.raiser['position']):
            return Actions.FOLD, 0
        return Actions.CALL, postflop.last_bet
    return Actions.FOLD, 0


def _multipot_raiser_second_pair(postflop):
    return _x_fold(postflop.raiser)


def _multipot_raiser_third_pair(postflop):
    return _multipot_raiser_second_pair(postflop)


def _multipot_raiser_two_overcards_with_a(postflop):
    return _multipot_raiser_second_pair(postflop)


def _multipot_raiser_two_overcards(postflop):
    return _multipot_raiser_second_pair(postflop)


def _multipot_raiser_gutshot(postflop):
    return _multipot_raiser_second_pair(postflop)


def _multipot_raiser_dry_board(postflop):
    return _multipot_raiser_second_pair(postflop)


def _multipot_raiser_rest(postflop):
    return _multipot_raiser_second_pair(postflop)


# Multipot-Caller


def _multipot_caller_top_two_pair_plus(postflop):
    if postflop.street == Streets.FLOP.value:
        if postflop.raiser is not None:
            return Actions.RAISE, 3 * postflop.last_bet
        return Actions.CALL, 0
    if postflop.street == Streets.TURN.value:
        return Actions.RAISE, 0.75 * postflop.pot
    return Actions.RAISE, postflop.max_bet


def _multipot_caller_two_pair(postflop):
    if postflop.street == Streets.FLOP.value:
        if postflop.raiser is not None:
            return Actions.RAISE, 3 * postflop.last_bet
        return Actions.CALL, 0
    if postflop.street == Streets.TURN.value:
        return Actions.RAISE, 0.75 * postflop.pot
    for suit, cards in groupby(_sort_cards_by_suit(postflop.community), lambda c: c[0:1]):
        if len(list(cards)) >= 3:
            return _x_fold(postflop.raiser)

    sorted_cards = list(
        map(lambda c: _card_value(c), dict.fromkeys(_filter_values(_sort_cards_by_value(postflop.hole + postflop.community[:-1])))))

    # Check if Ace may finish postflop.street
    if 14 in sorted_cards:
        sorted_cards.append(1)

    for i in range(0, len(sorted_cards) - 3):
        gaps = 0
        for j in range(0, 3):
            gaps += (sorted_cards[i + j] - sorted_cards[i + j + 1] - 1)
        if gaps < 2:
            return _x_fold(postflop.raiser)

    return Actions.RAISE, postflop.max_bet


def _multipot_caller_top_pair_top_kicker(postflop):
    if postflop.street_round == 1:
        return Actions.CALL, postflop.last_bet
    return Actions.FOLD, 0


def _multipot_caller_top_pair_k_kicker(postflop):
    return _multipot_caller_top_pair_top_kicker(postflop)


def _multipot_caller_top_pair_q_kicker(postflop):
    return _multipot_caller_top_pair_top_kicker(postflop)


def _multipot_caller_top_pair(postflop):
    return _multipot_caller_top_pair_top_kicker(postflop)


def _multipot_caller_oesd_flash_draw(postflop):
    if postflop.street_round <= 2:
        return Actions.CALL, postflop.last_bet
    return Actions.FOLD, 0


def _multipot_caller_second_pair(postflop):
    return _x_fold(postflop.raiser)


def _multipot_caller_third_pair(postflop):
    return _multipot_caller_second_pair(postflop)


def _multipot_caller_two_overcards_with_a(postflop):
    return _multipot_caller_second_pair(postflop)


def _multipot_caller_two_overcards(postflop):
    return _multipot_caller_second_pair(postflop)


def _multipot_caller_gutshot(postflop):
    return _multipot_caller_second_pair(postflop)


def _multipot_caller_dry_board(postflop):
    return _multipot_caller_second_pair(postflop)


def _multipot_caller_rest(postflop):
    return _multipot_caller_second_pair(postflop)
