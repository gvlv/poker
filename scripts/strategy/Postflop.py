from itertools import groupby

from scripts.const import Actions, Streets
from scripts.strategy.postflop_util import Hand, Pot, Strategy, strategies
from scripts.util import _filter_values, _sort_cards_by_value, _sort_cards_by_suit, _card_value


class Postflop:

    def __init__(self, pot_type, strategy, hand, hole, community, street, player, raiser, pot, last_bet, max_bet,
                 players, history):
        self.street = None
        self.street_round = 1
        
        self.pot_type = pot_type
        self.strategy = strategy
        self.hand = hand
        self.hole = hole
        self.community = community
        self.street = street
        self.player = player
        self.raiser = raiser
        self.pot = pot
        self.last_bet = last_bet
        self.max_bet = max_bet
        self.players = players
        self.history = history
        
    def declare_action(self):
        if self.street is not self.street:
            self.street = self.street
            self.street_round = 1
        else:
            self.street_round += 1

        hand = _get_hand(self.hand, self.hole, self.community)

        street_history = self.history[self.street]

        if self.pot_type == Pot.RAISE and self.street is not Streets.FLOP.value:
            checks = list(filter(lambda a: a['action'] == 'CALL' and a['amount'] == 0, self.history['flop']))
            if len(self.history['flop']) == len(checks) and _is_bluff(hand):
                if len(street_history) == 0 or len(list(filter(lambda a: a['action'] == 'RAISE', street_history))) == 0:
                    return Actions.RAISE, 0.75 * self.pot
                else:
                    return Actions.FOLD, 0

        if self.pot_type == Pot.RAISE and len(street_history) > 0:
            if self.strategy == Strategy.RAISER and _is_donk_bet(self.street, self.history):
                self.strategy = Strategy.CALLER
            elif self.strategy == Strategy.CALLER:
                opponent_last_action = street_history[len(street_history) - 1]
                if opponent_last_action['action'].lower() == Actions.CALL and opponent_last_action['amount'] == 0:
                    if _is_bluff(hand):
                        return Actions.RAISE, 0.5 * self.pot
                    else:
                        self.strategy = Strategy.RAISER

        if self.pot_type == Pot.THREE_BET:
            if self.strategy == Strategy.CALLER and len(street_history) > 0:
                opponent_last_action = street_history[len(street_history) - 1]
                if opponent_last_action['action'].lower() == Actions.CALL and opponent_last_action['amount'] == 0:
                    if _is_bluff(hand):
                        return Actions.RAISE, 0.5 * self.pot
                    else:
                        self.strategy = Strategy.RAISER

        if self.pot_type == Pot.MULTIPOT:
            if self.strategy == Strategy.RAISER and _is_donk_bet(self.street, self.history):
                self.strategy = Strategy.CALLER

        if self.pot_type == Pot.THREE_BET and self.street == Streets.RIVER.value and len(self.community) > 3:
            street_4 = False
            flash_4 = False

            for suit, cards in groupby(_sort_cards_by_suit(self.community), lambda c: c[0:1]):
                if len(list(cards)) == 4:
                    flash_4 = True

            sorted_community = \
                list(map(lambda c: _card_value(c), dict.fromkeys(_filter_values(_sort_cards_by_value(self.community)))))

            # Check if Ace may finish self.street
            if 14 in sorted_community:
                sorted_community.append(1)

            for i in range(0, len(sorted_community) - 3):
                gaps = 0
                for j in range(0, 3):
                    gaps += (sorted_community[i + j] - sorted_community[i + j + 1] - 1)
                if gaps < 2:
                    street_4 = True

            if street_4 or flash_4:
                return Actions.RAISE, 0.5 * self.pot

        action, amount = strategies[self.pot_type][self.strategy][hand](self)

        return action, amount


def _is_bluff(hand):
    return hand <= Hand.THIRD_PAIR or hand == Hand.OESD_FLASH_DRAW


def _is_donk_bet(street, history):
    street_history = history[street]
    if len(street_history) == 0:
        return False

    first_player_uuid = street_history[0]['uuid']
    preflop_actions = list(filter(lambda a: a['uuid'] == first_player_uuid, history['preflop']))
    if preflop_actions[len(preflop_actions) - 1]['action'].lower() != Actions.CALL:
        return False

    return street_history[0]['action'].lower() == Actions.RAISE


def _get_hand(hand, hole, community):
    if _is_top_two_pair_plus(hand, hole, community):
        return Hand.TOP_TWO_PAIR_PLUS
    if _is_two_pair(hand, hole, community):
        return Hand.TWO_PAIR
    if _is_top_pair_top_kicker(hand, hole, community):
        return Hand.TOP_PAIR_TOP_KICKER
    if _is_top_pair_k_kicker(hand, hole, community):
        return Hand.TOP_PAIR_K_KICKER
    if _is_top_pair_q_kicker(hand, hole, community):
        return Hand.TOP_PAIR_Q_KICKER
    if _is_top_pair(hand, hole, community):
        return Hand.TOP_PAIR
    if _is_oesd_flash_draw(hand, hole, community):
        return Hand.OESD_FLASH_DRAW
    if _is_second_pair(hand, hole, community):
        return Hand.SECOND_PAIR
    if _is_third_pair(hand, hole, community):
        return Hand.THIRD_PAIR
    if _is_two_overcards_with_a(hand, hole, community):
        return Hand.TWO_OVERCARDS_WITH_A
    if _is_two_overcards(hand, hole, community):
        return Hand.TWO_OVERCARDS
    if _is_gutshot(hand, hole, community):
        return Hand.GUTSHOT
    if _is_dry_board(hand, hole, community):
        return Hand.DRY_BOARD
    return Hand.REST


def _is_top_two_pair_plus(hand, hole, community):
    strength = hand['strength']

    if strength not in ['HIGHCARD', 'ONEPAIR', 'TWOPAIR']:
        return _is_contain_card_in_hole(hand, hole, community)

    filtered_hole = _filter_values(hole)
    sorted_cards = _filter_values(_sort_cards_by_value(hole + community))
    return strength == 'TWOPAIR' and len(sorted_cards) > 3 and sorted_cards[0] == sorted_cards[1] and \
           sorted_cards[2] == sorted_cards[3] and sorted_cards[0] in filtered_hole and sorted_cards[2] in filtered_hole


def _is_two_pair(hand, hole, community):
    if hand['strength'] is not 'TWOPAIR':
        return False
    filtered_hole = _filter_values(hole)
    return hand['strongest_cards'][0] in filtered_hole and hand['strongest_cards'][1] in filtered_hole


def _is_top_pair_top_kicker(hand, hole, community):
    if hand['strength'] is not 'ONEPAIR':
        return False

    sorted_community = _filter_values(_sort_cards_by_value(community))
    sorted_hole = _filter_values(_sort_cards_by_value(hole))

    if sorted_community[0] in sorted_hole:
        kicker = sorted_hole[(sorted_hole.index(sorted_community[0]) + 1) % 2]
        community_values = list(map(lambda c: _card_value(c), sorted_community))
        top_kicker = [c for c in range(14, 1, -1) if c not in community_values][0]
        return _card_value(kicker) == top_kicker

    return False


def _is_top_pair_k_kicker(hand, hole, community):
    if hand['strength'] is not 'ONEPAIR':
        return False

    sorted_community = _filter_values(_sort_cards_by_value(community))
    sorted_hole = _filter_values(_sort_cards_by_value(hole))

    if sorted_community[0] in sorted_hole:
        kicker = sorted_hole[(sorted_hole.index(sorted_community[0]) + 1) % 2]
        return _card_value(kicker) == 13

    return False


def _is_top_pair_q_kicker(hand, hole, community):
    if hand['strength'] is not 'ONEPAIR':
        return False

    sorted_community = _filter_values(_sort_cards_by_value(community))
    sorted_hole = _filter_values(_sort_cards_by_value(hole))

    if sorted_community[0] in sorted_hole:
        kicker = sorted_hole[(sorted_hole.index(sorted_community[0]) + 1) % 2]
        return _card_value(kicker) == 12

    return False


def _is_top_pair(hand, hole, community):
    hole = _filter_values(hole)
    community = _filter_values(community)
    return hand['strength'] == 'ONEPAIR' and max(community, key=lambda c: _card_value(c)) in hole


def _is_oesd_flash_draw(hand, hole, community):
    card_values = list(map(lambda c: _card_value(c), _filter_values(_sort_cards_by_value(hole + community))))

    # Check if Ace may finish street
    if 14 in card_values:
        card_values.append(1)

    prev_card = 0
    row = 1
    oesd_set = [card_values[0]]
    for c in card_values:
        if row >= 4:
            for c in oesd_set:
                if str(c) in _filter_values(hole):
                    return True

        if prev_card - c == 1:
            row += 1
            oesd_set.append(c)
        elif prev_card - c > 1:
            row = 1
            oesd_set = [c]
        prev_card = c

    if row >= 4:
        return True

    sorted_cards = _sort_cards_by_suit(hole + community)
    for suit, cards in groupby(sorted_cards, lambda c: c[0:1]):
        card_list = list(cards)
        if len(card_list) >= 4:
            for c in card_list:
                if c in hole:
                    return True

    return False


def _is_second_pair(hand, hole, community):
    if hand['strength'] is not 'ONEPAIR':
        return False

    sorted_community = list(dict.fromkeys(_filter_values(_sort_cards_by_value(community))))
    hole = _filter_values(hole)
    return len(sorted_community) > 1 and sorted_community[1] in hole


def _is_third_pair(hand, hole, community):
    if hand['strength'] is not 'ONEPAIR':
        return False

    sorted_community = list(dict.fromkeys(_filter_values(_sort_cards_by_value(community))))
    hole = _filter_values(hole)
    return len(sorted_community) > 2 and sorted_community[2] in hole


def _is_two_overcards_with_a(hand, hole, community):
    return _is_two_overcards(hand, hole, community) and 'A' in _filter_values(hole)


def _is_two_overcards(hand, hole, community):
    sorted_cards = _filter_values(_sort_cards_by_value(hole + community))
    hole = _filter_values(hole)
    return len(sorted_cards) > 1 and sorted_cards[0] in hole and sorted_cards[1] in hole


def _is_gutshot(hand, hole, community):
    sorted_cards = list(dict.fromkeys(_filter_values(_sort_cards_by_value(hole + community))))

    if len(sorted_cards) < 3:
        return False

    sorted_cards = list(map(lambda c: _card_value(c), sorted_cards))

    # Check if Ace may finish street
    if 14 in sorted_cards:
        sorted_cards.append(1)

    if len(sorted_cards) < 4:
        return False

    for i in range(0, len(sorted_cards) - 3):
        gaps = 0
        gutshot_set = [sorted_cards[i]]
        for j in range(0, 3):
            gaps += (sorted_cards[i + j] - sorted_cards[i + j + 1] - 1)
            gutshot_set.append(sorted_cards[i + j + 1])
        if gaps == 1:
            for c in gutshot_set:
                if str(c) in _filter_values(hole) and c not in _filter_values(community):
                    return True

    return False


def _is_dry_board(hand, hole, community):
    sorted_cards = list(dict.fromkeys(_filter_values(_sort_cards_by_value(hole + community))))
    hole = _filter_values(hole)
    if hole[0] == hole[1] and sorted_cards.index(hole[0]) >= 3:
        return False

    for suit, cards in groupby(_sort_cards_by_suit(community), lambda c: c[0:1]):
        if len(list(cards)) >= 2:
            return False

    sorted_community = list(dict.fromkeys(_filter_values(_sort_cards_by_value(community))))

    if len(sorted_community) < 3:
        return False

    sorted_community = list(map(lambda c: _card_value(c), sorted_community))

    # Check if Ace may finish street
    if 14 in sorted_community:
        sorted_community.append(1)

    for i in range(0, len(sorted_community) - 2):
        gaps = 0
        gutshot_set = [sorted_cards[i]]
        for j in range(0, 2):
            gaps += (sorted_community[i + j] - sorted_community[i + j + 1] - 1)
            gutshot_set.append(sorted_community[i + j + 1])
        if gaps <= 2:
            for c in gutshot_set:
                if str(c) in _filter_values(hole) and c not in _filter_values(community):
                    return False

    return True


def _is_contain_card_in_hole(hand, hole, community):
    hole_values = _filter_values(hole)
    community_values = _filter_values(community)
    for c in hand['strongest_cards']:
        if c in hole_values and c not in community_values:
            return True
    return False
