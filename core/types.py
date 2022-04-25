from enum import Enum, auto


class Street(Enum):
    PREFLOP = auto()
    FLOP = auto()
    TURN = auto()
    RIVER = auto()


class ActionType(Enum):
    CHECK = 1
    FOLD = 2
    CALL = 3
    BET = 4
    RAISE = 5
    SMALLBLIND = 6
    BIGBLIND = 7


class GameType(Enum):
    HOLDEM_NO_LIMIT = 1
    OMAHA_POT_LIMIT = 2
    UNKNOWN = 3
