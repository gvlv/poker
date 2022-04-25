from enum import Enum


class Streets(Enum):
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"


class Actions:
    FOLD = "fold"
    CALL = "call"
    RAISE = "raise"


class States:
    ALLIN = 'allin'
    PARTICIPATING = 'participating'
    FOLDED = 'folded'


Seats = ["BU", "SB", "BB", "UTG", "MP", "CO"]


class CardValues(Enum):
    C2 = 2,  "Two",   "Twos"
    C3 = 3,  "Three", "Threes"
    C4 = 4,  "Four",  "Fours"
    C5 = 5,  "Five",  "Fives"
    C6 = 6,  "Six",   "Sixes"
    C7 = 7,  "Seven", "Sevens"
    C8 = 8,  "Eight", "Eights"
    C9 = 9,  "Nine",  "Nines"
    CT = 10, "Ten",   "Tens"
    CJ = 11, "Jack",  "Jacks"
    CQ = 12, "Queen", "Queens"
    CK = 13, "King",  "Kings"
    CA = 14, "Ace",   "Aces"

    def __new__(cls, value, single, multiple):
        member = object.__new__(cls)
        member._value_ = value
        member.single = single
        member.multiple = multiple
        return member

    def __int__(self):
        return self.value
