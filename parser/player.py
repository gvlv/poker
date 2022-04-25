from typing import List

from core.card import Card
from regexp import *


class Player(object):
    def __init__(self, position, nickname, chips, player_cards=None):
        self.__position = int(position)
        self.__nick = nickname
        self.__chips = float(str(chips).strip(currency))
        self.__player_cards = player_cards

    def __eq__(self, other):
        return self.position == other.position and self.nick == other.nick and self.chips == other.chips

    @property
    def position(self) -> int:
        return self.__position

    @property
    def nick(self) -> str:
        return self.__nick

    @property
    def chips(self) -> float:
        return self.__chips

    @property
    def player_cards(self) -> List[Card]:
        return self.__player_cards

    @player_cards.setter
    def player_cards(self, value: List[Card]):
        self.__player_cards = value

    def __repr__(self):
        return f"{self.position}, {self.nick}, {self.chips}, {self.player_cards}"

    def __str__(self):
        return f"{self.position}, {self.nick}, {self.chips}, {self.player_cards}"
