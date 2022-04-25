import math

from core.types import ActionType


class Action(object):
    def __init__(self, player: str, action_type: ActionType, bet_size=0):
        self.__player = player
        self.__action_type = action_type
        self.__bet_size = bet_size

    @property
    def player(self) -> str:
        return self.__player

    @property
    def action_type(self) -> ActionType:
        return self.__action_type

    @property
    def bet_size(self) -> float:
        return self.__bet_size

    def __eq__(self, other):
        if isinstance(other, Action):
            return self.player == other.player and self.action_type == other.action_type \
                   and math.isclose(self.bet_size, other.bet_size, abs_tol=0.00001)
        else:
            # don't attempt to compare against unrelated types
            return NotImplemented

    def __repr__(self):
        return f"{self.player}, {self.action_type}, {self.bet_size}"

    def __str__(self):
        return f"{self.player}, {self.action_type}, {self.bet_size}"
