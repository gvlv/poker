import pytest

from core.card import Card
from features.board import Board


@pytest.mark.parametrize(
    "board, expected",
    [(Board([Card('H', '2'), Card('H', '8'), Card('H', '4'), Card('C', 'K'), Card('D', '3')]),
      [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 3, 1, 1]),
     (Board([Card('S', 'A'), Card('C', '3'), Card('D', 'Q'), Card('C', 'K')]),
      [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 2]),
     (Board([Card('H', '3'), Card('C', '3'), Card('D', '2')]),
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 1, 1, 1]),
     (Board([Card('D', '3'), Card('S', '2'), Card('D', '7'), Card('C', '6'), Card('H', 'J')]),
      [0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 2, 1]),
     (Board([Card('C', '4'), Card('D', '4'), Card('C', 'J')]),
      [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 1, 2]),
     (Board([Card('C', '4'), Card('C', '5'), Card('C', '7'), Card('H', 'Q')]),
      [0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 3]),
     (Board([Card('D', 'K'), Card('S', '5'), Card('C', '4'), Card('D', '4'), Card('C', 'J')]),
      [0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 2, 0, 0, 1, 0, 2, 2])
     ],
)
def test_board(board, expected):
    assert board.extract_features() == expected
