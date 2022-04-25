import numpy as np
from pypokerengine.utils.card_utils import Card, Deck
import random
from scripts.const import CardValues, Seats

suits = list(Card.SUIT_MAP.keys())
ranks = list(Card.RANK_MAP.keys())


def gen_card_im(card):
    a = np.zeros((4, 13))
    s = suits.index(card.suit)
    r = ranks.index(card.rank)
    a[s, r] = 1
    return np.pad(a, ((6, 7), (2, 2)), 'constant', constant_values=0)


streep_map = {
    'preflop': 0,
    'flop': 1,
    'turn': 2,
    'river': 3
}
 

def get_street(s):
    val = [0, 0, 0, 0]
    val[streep_map[s]] = 1
    return val


def process_img(img):
    return np.reshape(img, [17 * 17 * 1])


class ExperienceBuffer():
    def __init__(self, buffer_size=5_000):
        self.buffer = []
        self.buffer_size = buffer_size

    def add(self, experience):
        if len(self.buffer) + len(experience) >= self.buffer_size:
            self.buffer[0:len(self.buffer) + len(experience) - self.buffer_size] = []
        self.buffer.extend(experience)

    def sample(self, size):
        return np.reshape(np.array(random.sample(self.buffer, size)), [size, 7])


def get_action_by_num(action_num, valid_actions, is_train=True):
    if action_num == 0:
        action, amount = valid_actions[0]['action'], valid_actions[0]['amount']
    elif action_num == 1:
        action, amount = valid_actions[1]['action'], valid_actions[1]['amount']
    elif action_num == 2:
        action, amount = valid_actions[2]['action'], valid_actions[2]['amount']['min']
    elif action_num == 3:
        action, amount = valid_actions[2]['action'], valid_actions[2]['amount']['max']
    elif action_num == 4:
        action, amount = valid_actions[2]['action'], int(valid_actions[2]['amount']['max'] // 2)

    if amount == -1:
        action, amount = valid_actions[1]['action'], valid_actions[1]['amount']
        # print(action, amount)
    return action, amount


def img_from_state(hole_card, round_state):
    imgs = np.zeros((8, 17, 17))
    for i, c in enumerate(hole_card):
        imgs[i] = gen_card_im(Card.from_str(c))

    for i, c in enumerate(round_state['community_card']):
        imgs[i + 2] = gen_card_im(Card.from_str(c))

    imgs[7] = imgs[:7].sum(axis=0)
    #     return imgs
    # print(imgs)
    return np.swapaxes(imgs, 0, 2)[:, :, -1:]


def format_hole(hole_card):
    res = ''.join(list(sorted(map(lambda c: c[1], hole_card), key=lambda c: CardValues['C' + c].value, reverse=True)))
    if res[0] is not res[1]:
        res += 's' if hole_card[0][0] == hole_card[1][0] else 'o'
    return res


# TODO: Fix for 7+ players
def get_seat_name(seats, player, button):
    seats = 6 if seats > 6 else seats
    return Seats[(player - button + seats) % seats]


def _sort_cards_by_value(cards):
    return list(sorted(cards, key=lambda c: _card_value(c[1:]), reverse=True))


def _sort_cards_by_suit(cards):
    return list(sorted(cards, key=lambda c: c[0:1], reverse=True))


def _filter_values(cards):
    return list(map(lambda c: c[1:], cards))


def _filter_suites(cards):
    return list(map(lambda c: c[0:1], cards))


def _card_value(card):
    return CardValues['C' + card]._value_
