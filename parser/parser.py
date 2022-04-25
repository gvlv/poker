import logging
from typing import List

from hand import Hand
from regexp import *

log = logging.getLogger(__name__)


class Parser(object):
    def __init__(self):
        self.__hands = {}

    @property
    def hands(self):
        return self.__hands

    def handle_hand(self, id_prefix: str, hand: List[str]):
        h = Hand(id_prefix, hand)
        if h.hand_id in self.__hands:
            self.__hands[h.hand_id].append(h)
        else:
            self.__hands[h.hand_id] = [h]

    def add_lines(self, id_prefix, lines):
        hand = []
        hand_started = False
        bad_hands = 0
        for line in lines:
            line = line.strip()
            if hand_regexp.match(line):
                continue
            if game_type_regexp.match(line):
                hand_started = True
                # Start new hand
                if len(hand) > 0:
                    try:
                        self.handle_hand(id_prefix, hand)
                    except Exception as e:
                        log.debug(e)
                        bad_hands += 1
                    hand = []
            if hand_started:
                hand.append(line)
        if len(hand) > 0:
            try:
                self.handle_hand(id_prefix, hand)
            except Exception as e:
                log.debug(e)
                bad_hands += 1
        log.debug(f"Bad hands: {bad_hands}")
