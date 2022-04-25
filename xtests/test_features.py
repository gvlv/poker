from feature_extractor import FeatureExtractor
from features.features import FeaturesPack, CallTotalAmount
from hand import Hand
from player import Player
from xtests.examples import hand192510344085, hand204214924894


def test_order_players():
    players = {'ab': Player(2, 'ab', 10),
               'ac': Player(1, 'ac', 15),
               'ba': Player(4, 'ba', 9),
               'ca': Player(3, 'ca', 11)}
    assert FeaturesPack.order_players(players) == [Player(1, 'ac', 15),
                                                   Player(2, 'ab', 10),
                                                   Player(3, 'ca', 11),
                                                   Player(4, 'ba', 9)]


def test_get_our_position():
    players = [Player(1, 'ac', 15),
               Player(2, 'ab', 10),
               Player(3, 'ca', 11),
               Player(4, 'ba', 9)]
    assert FeaturesPack.get_our_position(players, 'ca') == 2
    assert FeaturesPack.get_our_position(players, 'ac') == 0
    assert FeaturesPack.get_our_position(players, 'ba') == 3
    assert FeaturesPack.get_our_position(players, 'ab') == 1


def test_features_empty_nicknames(parser):
    lines = [x.strip() for x in filter(lambda x: x != '', hand192510344085.split("\n"))]
    parser.add_lines('xx', lines)
    hand: Hand = parser.hands['xx_192510344085'][0]

    fe = FeatureExtractor([])
    assert fe.extract_features(hand) == []


def test_features_no_player_with_showndown_cards(parser):
    lines = [x.strip() for x in filter(lambda x: x != '', hand192510344085.split("\n"))]
    parser.add_lines('xx', lines)
    hand: Hand = parser.hands['xx_192510344085'][0]

    fe = FeatureExtractor(['EthanBinder', 'ja.sam.gale', 'Bit2Easy'])
    assert fe.extract_features(hand) == []


def test_hand192510344085(parser):
    lines = [x.strip() for x in filter(lambda x: x != '', hand192510344085.split("\n"))]
    parser.add_lines('xx', lines)
    hand: Hand = parser.hands['xx_192510344085'][0]

    fe = FeatureExtractor(['BigBlindBets', '0Human0'])
    features = fe.extract_features(hand)
    assert len(features) == 4
    assert features[0] == ['xx_192510344085', 'BigBlindBets', 'PREFLOP',
                           'RAISE',  # Player Action
                           3.0,  # Bet size
                           0,  # Call total amount
                           0,  # Check total amount
                           0,  # Bet total amount
                           0,  # Raise total amount
                           4,  # Fold total amount
                           0,  # Call street amount
                           0,  # Check street amount
                           0,  # Bet street amount
                           0,  # Raise street amount
                           4,  # Fold street amount
                           0,  # Player position
                           0,  # Players in pot
                           1.5,  # Current pot size
                           101.95,  # Current player stack size
                           0.5,  # Paid on all streets
                           0.5,  # Should pay for continue
                           1.0,  # Current Bet
                           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # Ranks
                           0, 0, 0, 0,  # Suits
                           'ONE_PAIR'  # Current combination
                           ]
    assert features[1] == ['xx_192510344085', 'BigBlindBets', 'FLOP',
                           'CHECK',  # Player Action
                           0.0,  # Bet size
                           1,  # Call total amount
                           0,  # Check total amount
                           0,  # Bet total amount
                           1,  # Raise total amount
                           4,  # Fold total amount
                           0,  # Call street amount
                           0,  # Check street amount
                           0,  # Bet street amount
                           0,  # Raise street amount
                           0,  # Fold street amount
                           0,  # Player position
                           2,  # Players in pot
                           6.0,  # Current pot size
                           99.45,  # Current player stack size
                           3.0,  # % Which we already pay
                           0.0,  # Should pay for continue
                           0.0,  # Current Bet
                           0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0,  # Ranks
                           0, 1, 0, 2,  # Suits S/H/D/C
                           'ONE_PAIR'  # Current combination
                           ]

    assert features[2] == ['xx_192510344085', 'BigBlindBets', 'TURN',
                           'CHECK',  # Player Action
                           0.0,  # Bet size
                           1,  # Call total amount
                           2,  # Check total amount
                           0,  # Bet total amount
                           1,  # Raise total amount
                           4,  # Fold total amount
                           0,  # Call street amount
                           0,  # Check street amount
                           0,  # Bet street amount
                           0,  # Raise street amount
                           0,  # Fold street amount
                           0,  # Player position
                           2,  # Players in pot
                           6.0,  # Current pot size
                           99.45,  # Current player stack size
                           3.0,  # % Which we already pay
                           0.0,  # Should pay for continue
                           0.0,  # Current Bet
                           1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0,  # Ranks
                           1, 1, 0, 2,  # Suits S/H/D/C
                           'ONE_PAIR'  # Current combination
                           ]

    assert features[3] == ['xx_192510344085', 'BigBlindBets', 'RIVER',
                           'CHECK',  # Player Action
                           0.0,  # Bet size
                           1,  # Call total amount
                           4,  # Check total amount
                           0,  # Bet total amount
                           1,  # Raise total amount
                           4,  # Fold total amount
                           0,  # Call street amount
                           0,  # Check street amount
                           0,  # Bet street amount
                           0,  # Raise street amount
                           0,  # Fold street amount
                           0,  # Player position
                           2,  # Players in pot
                           6.0,  # Current pot size
                           99.45,  # Current player stack size
                           3.,  # % Which we already pay
                           0.0,  # Should pay for continue
                           0.0,  # Current Bet
                           1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0,  # Ranks
                           1, 1, 0, 3,  # Suits S/H/D/C
                           'ONE_PAIR'  # Current combination
                           ]


def test_hand204214924894(parser):
    lines = [x.strip() for x in filter(lambda x: x != '', hand204214924894.split("\n"))]
    parser.add_lines('xx', lines)
    hand: Hand = parser.hands['xx_204214924894'][0]

    features = FeatureExtractor(['Real Suka', 'Aikocho']).extract_features(hand)
    assert len(features) == 4
    assert features[0] == ['xx_204214924894', 'Real Suka', 'PREFLOP',
                           'CALL',  # Player Action
                           1.,  # Bet size
                           0,  # Call total amount
                           0,  # Check total amount
                           0,  # Bet total amount
                           0,  # Raise total amount
                           0,  # Fold total amount
                           0,  # Call street amount
                           0,  # Check street amount
                           0,  # Bet street amount
                           0,  # Raise street amount
                           0,  # Fold street amount
                           2,  # Player position
                           0,  # Players in pot
                           1.5000000000000002,  # Current pot size
                           87.89999999999999,  # Current player stack size
                           0.,  # Paid on all streets
                           1.,  # Should pay for continue
                           1.0,  # Current Bet
                           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # Ranks
                           0, 0, 0, 0,  # Suits
                           'AIR'  # Current combination
                           ]

    assert features[1] == ['xx_204214924894', 'Real Suka', 'PREFLOP',
                           'RAISE',  # Player Action
                           87.89999999999999,  # Bet size
                           2,  # Call total amount
                           0,  # Check total amount
                           0,  # Bet total amount
                           1,  # Raise total amount
                           3,  # Fold total amount
                           2,  # Call street amount
                           0,  # Check street amount
                           0,  # Bet street amount
                           1,  # Raise street amount
                           3,  # Fold street amount
                           2,  # Player position
                           3,  # Players in pot
                           10.5,  # Current pot size
                           86.89999999999999,  # Current player stack size
                           0.9999999999999964,  # Paid on all streets
                           3.0000000000000004,  # Should pay for continue
                           4.0,  # Current Bet
                           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # Ranks
                           0, 0, 0, 0,  # Suits
                           'AIR'  # Current combination
                           ]

    assert features[2] == ['xx_204214924894', 'Aikocho', 'PREFLOP',
                           'CALL',  # Player Action
                           4.,  # Bet size
                           1,  # Call total amount
                           0,  # Check total amount
                           0,  # Bet total amount
                           1,  # Raise total amount
                           1,  # Fold total amount
                           1,  # Call street amount
                           0,  # Check street amount
                           0,  # Bet street amount
                           1,  # Raise street amount
                           1,  # Fold street amount
                           5,  # Player position
                           2,  # Players in pot
                           6.5,  # Current pot size
                           42.5,  # Current player stack size
                           0.,  # Paid on all streets
                           4.,  # Should pay for continue
                           4.0,  # Current Bet
                           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # Ranks
                           0, 0, 0, 0,  # Suits
                           'AIR'  # Current combination
                           ]

    assert features[3] == ['xx_204214924894', 'Aikocho', 'PREFLOP',
                           'CALL',  # Player Action
                           38.5,  # Bet size
                           2,  # Call total amount
                           0,  # Check total amount
                           0,  # Bet total amount
                           2,  # Raise total amount
                           4,  # Fold total amount
                           2,  # Call street amount
                           0,  # Check street amount
                           0,  # Bet street amount
                           2,  # Raise street amount
                           4,  # Fold street amount
                           5,  # Player position
                           2,  # Players in pot
                           97.39999999999999,  # Current pot size
                           38.5,  # Current player stack size
                           3.999999999999999,  # Paid on all streets
                           83.89999999999998,  # Should pay for continue
                           87.89999999999999,  # Current Bet
                           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # Ranks
                           0, 0, 0, 0,  # Suits
                           'AIR'  # Current combination
                           ]
