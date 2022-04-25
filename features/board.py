from typing import List

from core.card import Card


class Board(object):
    def __init__(self, board: List[Card]):
        self.__board = board

    @property
    def board(self):
        return self.__board

    @staticmethod
    def features_names():
        return [
            "board_ace_amount",
            "board_king_amount",
            "board_queen_amount",
            "board_jack_amount",
            "board_10_amount",
            "board_9_amount",
            "board_8_amount",
            "board_7_amount",
            "board_6_amount",
            "board_5_amount",
            "board_4_amount",
            "board_3_amount",
            "board_2_amount",
            "board_spades_amount",
            "board_hearts_amount",
            "board_diamonds_amount",
            "board_clubs_amount",
        ]

    def extract_features(self):
        return [
            len(list(filter(lambda c: c.rank == 'A', self.board))),
            len(list(filter(lambda c: c.rank == 'K', self.board))),
            len(list(filter(lambda c: c.rank == 'Q', self.board))),
            len(list(filter(lambda c: c.rank == 'J', self.board))),
            len(list(filter(lambda c: c.rank == 'T', self.board))),
            len(list(filter(lambda c: c.rank == '9', self.board))),
            len(list(filter(lambda c: c.rank == '8', self.board))),
            len(list(filter(lambda c: c.rank == '7', self.board))),
            len(list(filter(lambda c: c.rank == '6', self.board))),
            len(list(filter(lambda c: c.rank == '5', self.board))),
            len(list(filter(lambda c: c.rank == '4', self.board))),
            len(list(filter(lambda c: c.rank == '3', self.board))),
            len(list(filter(lambda c: c.rank == '2', self.board))),

            len(list(filter(lambda c: c.suit == 'S', self.board))),
            len(list(filter(lambda c: c.suit == 'H', self.board))),
            len(list(filter(lambda c: c.suit == 'D', self.board))),
            len(list(filter(lambda c: c.suit == 'C', self.board)))
        ]
