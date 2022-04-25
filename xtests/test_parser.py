from action import Action
from core.card import Card
from core.types import GameType, ActionType
from hand import Hand
from xtests.examples import hand228, hand127, hand5222, hand192510344085, hand204214924894, hand207718751903


def test_parser_hand199880364584(parser):
    lines = [x.strip() for x in filter(lambda x: x != '', hand228.split("\n"))]
    parser.add_lines('xx', lines)
    assert len(parser.hands) == 1
    assert 'xx_199880364584' in parser.hands
    assert len(parser.hands['xx_199880364584']) == 1
    hand: Hand = parser.hands['xx_199880364584'][0]
    assert hand.game_type == GameType.HOLDEM_NO_LIMIT
    assert hand.small_blind == 1.
    assert hand.big_blind == 2
    assert hand.players_count == 6
    assert hand.total_pot == 5
    assert hand.rake == 0
    assert hand.players['rodito_139'].player_cards is None
    assert hand.players['AcceptMe77'].player_cards is None
    assert hand.players['ValentjNN'].player_cards is None
    assert hand.players['@lexxx8'].player_cards is None
    assert Card('C', '3') in hand.players['ValeraBart'].player_cards and \
           Card('D', '7') in hand.players['ValeraBart'].player_cards
    assert hand.players['VilelaVictor'].player_cards is None
    assert len(hand.flop_cards) == 0


def test_parser_hand199880482022(parser):
    lines = [x.strip() for x in filter(lambda x: x != '', hand127.split("\n"))]
    parser.add_lines('xx', lines)
    assert len(parser.hands) == 1
    assert 'xx_199880482022' in parser.hands
    assert len(parser.hands['xx_199880482022']) == 1
    hand: Hand = parser.hands['xx_199880482022'][0]
    assert hand.hand_id == 'xx_199880482022'
    assert hand.game_type == GameType.HOLDEM_NO_LIMIT
    assert hand.big_blind == 2.
    assert hand.small_blind == 1.
    assert hand.players_count == 6
    assert hand.total_pot == 48.26
    assert hand.rake == 2.41

    assert hand.players['Tigriana'].player_cards is None
    assert hand.players['cryingkevin'].player_cards == [Card('C', '6'), Card('D', '9')]
    assert hand.players['cpatras1'].player_cards is None
    assert hand.players['AIvers2'].player_cards is None
    assert hand.players['ValeraBart'].player_cards == [Card('D', '6'), Card('H', '4')]
    assert hand.players['sauloCosta10'].player_cards == [Card('H', '8'), Card('H', '7')]

    assert hand.flop_cards == [Card('D', '7'), Card('C', '2'), Card('C', '4')]
    assert hand.turn_cards == [Card('D', '7'), Card('C', '2'), Card('C', '4'), Card('S', '4')]
    assert hand.river_cards == [Card('D', '7'), Card('C', '2'), Card('C', '4'), Card('S', '4'), Card('H', 'T')]

    # Check preflop actions
    assert hand.preflop_actions == [Action('cryingkevin', ActionType.SMALLBLIND, 1.),
                                    Action('cpatras1', ActionType.BIGBLIND, 2.),
                                    Action('AIvers2', ActionType.FOLD),
                                    Action('sauloCosta10', ActionType.RAISE, 4.30),
                                    Action('ValeraBart', ActionType.FOLD),
                                    Action('Tigriana', ActionType.FOLD),
                                    Action('cryingkevin', ActionType.CALL, 3.3),
                                    Action('cpatras1', ActionType.FOLD)]

    # Check flop actions
    assert hand.flop_actions == [Action('cryingkevin', ActionType.CHECK),
                                 Action('sauloCosta10', ActionType.BET, 3.02),
                                 Action('cryingkevin', ActionType.CALL, 3.02)]

    # Check turn actions
    assert hand.turn_actions == [Action('cryingkevin', ActionType.CHECK), Action('sauloCosta10', ActionType.CHECK)]

    # Check river actions
    assert hand.river_actions == [Action('cryingkevin', ActionType.BET, 15.81),
                                  Action('sauloCosta10', ActionType.CALL, 15.81)]


def test_parser_hand195114127680(parser):
    lines = [x.strip() for x in filter(lambda x: x != '', hand5222.split("\n"))]
    parser.add_lines('xx', lines)
    assert len(parser.hands) == 1
    assert 'xx_195114127680' in parser.hands
    assert len(parser.hands['xx_195114127680']) == 1
    hand: Hand = parser.hands['xx_195114127680'][0]

    assert hand.hand_id == 'xx_195114127680'
    assert hand.game_type == GameType.HOLDEM_NO_LIMIT
    assert hand.big_blind == 10.
    assert hand.small_blind == 5.
    assert hand.players_count == 6
    assert hand.total_pot == 125.4
    assert hand.rake == 3

    assert hand.flop_cards == [Card('D', 'Q'), Card('H', 'T'), Card('C', 'J')]
    assert hand.turn_cards == [Card('D', 'Q'), Card('H', 'T'), Card('C', 'J'), Card('C', 'Q')]
    assert hand.river_cards == []

    players = hand.players
    assert players['BastianX'].chips == 1830.61 and players['BastianX'].position == 1 \
           and players['BastianX'].player_cards is None
    assert players['Evelyne17'].chips == 1000 and players['Evelyne17'].position == 2 \
           and players['Evelyne17'].player_cards is None
    assert players['drx8tyz9'].chips == 1000 and players['drx8tyz9'].position == 3 \
           and players['drx8tyz9'].player_cards is None
    assert players['zas91'].chips == 1999.67 and players['zas91'].position == 4 \
           and players['zas91'].player_cards is None
    assert players['Mukhin1'].chips == 1202.75 and players['Mukhin1'].position == 5 \
           and players['Mukhin1'].player_cards is None
    assert players['ValeraBart'].chips == 1280.61 and players['ValeraBart'].position == 6 \
           and players['ValeraBart'].player_cards == [Card('S', '4'), Card('C', 'A')]

    # Check preflop actions
    assert hand.preflop_actions == [Action('ValeraBart', ActionType.SMALLBLIND, 5.),
                                    Action('BastianX', ActionType.BIGBLIND, 10.),
                                    Action('Evelyne17', ActionType.FOLD),
                                    Action('drx8tyz9', ActionType.RAISE, 22.3),
                                    Action('zas91', ActionType.FOLD),
                                    Action('Mukhin1', ActionType.FOLD),
                                    Action('ValeraBart', ActionType.FOLD),
                                    Action('BastianX', ActionType.CALL, 12.3)]

    # Check flop actions
    assert hand.flop_actions == [Action('BastianX', ActionType.CHECK),
                                 Action('drx8tyz9', ActionType.BET, 37.9),
                                 Action('BastianX', ActionType.CALL, 37.9)]

    # Check turn actions
    assert hand.turn_actions == [Action('BastianX', ActionType.CHECK), Action('drx8tyz9', ActionType.BET, 120),
                                 Action('BastianX', ActionType.FOLD)]

    # Check river actions
    assert hand.river_actions == []


def test_parser_hand192510344085(parser):
    lines = [x.strip() for x in filter(lambda x: x != '', hand192510344085.split("\n"))]
    parser.add_lines('xx', lines)
    assert len(parser.hands) == 1
    assert 'xx_192510344085' in parser.hands
    assert len(parser.hands['xx_192510344085']) == 1
    hand: Hand = parser.hands['xx_192510344085'][0]

    assert hand.hand_id == 'xx_192510344085'
    assert hand.game_type == GameType.HOLDEM_NO_LIMIT

    assert hand.big_blind == 100.
    assert hand.small_blind == 50.
    assert hand.players_count == 6
    assert hand.total_pot == 600.
    assert hand.rake == 5.

    assert hand.flop_cards == [Card('H', '6'), Card('C', '4'), Card('C', 'K')]
    assert hand.turn_cards == [Card('H', '6'), Card('C', '4'), Card('C', 'K'), Card('S', 'A')]
    assert hand.river_cards == [Card('H', '6'), Card('C', '4'), Card('C', 'K'), Card('S', 'A'), Card('C', 'J')]

    players = hand.players
    assert players['0Human0'].chips == 11219.75 and players['0Human0'].position == 1 \
           and players['0Human0'].player_cards is None
    assert players['EthanBinder'].chips == 14558.07 and players['EthanBinder'].position == 2 \
           and players['EthanBinder'].player_cards is None
    assert players['BigBlindBets'].chips == 10245 and players['BigBlindBets'].position == 3 \
           and players['BigBlindBets'].player_cards == [Card('S', '3'), Card('C', '3')]
    assert players['ja.sam.gale'].chips == 10100 and players['ja.sam.gale'].position == 4 \
           and players['ja.sam.gale'].player_cards is None
    assert players['mamamamama70'].chips == 10337.50 and players['mamamamama70'].position == 5 \
           and players['mamamamama70'].player_cards is None
    assert players['Bit2Easy'].chips == 10000 and players['Bit2Easy'].position == 6 \
           and players['Bit2Easy'].player_cards is None

    # Check preflop actions
    assert hand.preflop_actions == [Action('BigBlindBets', ActionType.SMALLBLIND, 50.),
                                    Action('ja.sam.gale', ActionType.BIGBLIND, 100.),
                                    Action('mamamamama70', ActionType.FOLD),
                                    Action('Bit2Easy', ActionType.FOLD),
                                    Action('0Human0', ActionType.FOLD),
                                    Action('EthanBinder', ActionType.FOLD),
                                    Action('BigBlindBets', ActionType.RAISE, 300.),
                                    Action('ja.sam.gale', ActionType.CALL, 200.)]

    # Check flop actions
    assert hand.flop_actions == [Action('BigBlindBets', ActionType.CHECK),
                                 Action('ja.sam.gale', ActionType.CHECK)]

    # Check turn actions
    assert hand.turn_actions == [Action('BigBlindBets', ActionType.CHECK),
                                 Action('ja.sam.gale', ActionType.CHECK)]

    # Check river actions
    assert hand.river_actions == [Action('BigBlindBets', ActionType.CHECK),
                                  Action('ja.sam.gale', ActionType.CHECK)]


def test_parser_hand204214924894(parser):
    lines = [x.strip() for x in filter(lambda x: x != '', hand204214924894.split("\n"))]
    parser.add_lines('xx', lines)
    assert len(parser.hands) == 1
    assert 'xx_204214924894' in parser.hands
    assert len(parser.hands['xx_204214924894']) == 1
    hand: Hand = parser.hands['xx_204214924894'][0]

    assert hand.hand_id == 'xx_204214924894'
    assert hand.game_type == GameType.HOLDEM_NO_LIMIT

    assert hand.big_blind == 0.10
    assert hand.small_blind == 0.05
    assert hand.players_count == 6
    assert hand.total_pot == 9.05
    assert hand.rake == 0.41

    assert hand.flop_cards == [Card('S', '6'), Card('D', 'J'), Card('C', '6')]
    assert hand.turn_cards == [Card('S', '6'), Card('D', 'J'), Card('C', '6'), Card('S', '3')]
    assert hand.river_cards == [Card('S', '6'), Card('D', 'J'), Card('C', '6'), Card('S', '3'), Card('S', 'J')]

    players = hand.players
    assert players['Real Suka'].chips == 8.79 and players['Real Suka'].position == 1 \
           and players['Real Suka'].player_cards == [Card('C', '5'), Card('C', 'K')]
    assert players['LFGK'].chips == 10.05 and players['LFGK'].position == 2 \
           and players['LFGK'].player_cards is None
    assert players['lastfox'].chips == 10 and players['lastfox'].position == 3 \
           and players['lastfox'].player_cards is None
    assert players['Aikocho'].chips == 4.25 and players['Aikocho'].position == 4 \
           and players['Aikocho'].player_cards == [Card('C', 'T'), Card('C', 'A')]
    assert players['Bluebell89'].chips == 10.09 and players['Bluebell89'].position == 5 \
           and players['Bluebell89'].player_cards is None
    assert players['Burda19'].chips == 10 and players['Burda19'].position == 6 \
           and players['Burda19'].player_cards is None

    # Check preflop actions
    assert hand.preflop_actions == [Action('Bluebell89', ActionType.SMALLBLIND, 0.05),
                                    Action('Burda19', ActionType.BIGBLIND, 0.10),
                                    Action('Real Suka', ActionType.CALL, 0.1),
                                    Action('LFGK', ActionType.RAISE, 0.4),
                                    Action('lastfox', ActionType.FOLD),
                                    Action('Aikocho', ActionType.CALL, 0.4),
                                    Action('Bluebell89', ActionType.FOLD),
                                    Action('Burda19', ActionType.FOLD),
                                    Action('Real Suka', ActionType.RAISE, 8.79),
                                    Action('LFGK', ActionType.FOLD),
                                    Action('Aikocho', ActionType.CALL, 3.85)]

    # Check flop actions
    assert hand.flop_actions == []

    # Check turn actions
    assert hand.turn_actions == []

    # Check river actions
    assert hand.river_actions == []


def test_parser_hand207718751903(parser):
    lines = [x.strip() for x in filter(lambda x: x != '', hand207718751903.split("\n"))]
    parser.add_lines('xx', lines)
    assert len(parser.hands) == 1
    assert 'xx_207718751903' in parser.hands
    assert len(parser.hands['xx_207718751903']) == 1
    hand: Hand = parser.hands['xx_207718751903'][0]

    assert hand.hand_id == 'xx_207718751903'
    assert hand.game_type == GameType.HOLDEM_NO_LIMIT

    assert hand.big_blind == 100.
    assert hand.small_blind == 50.
    assert hand.players_count == 4
    assert hand.total_pot == 19800.
    assert hand.rake == 3.

    assert hand.flop_cards == [Card('H', '4'), Card('D', '9'), Card('D', '5')]
    assert hand.turn_cards == [Card('H', '4'), Card('D', '9'), Card('D', '5'), Card('S', '5')]
    assert hand.river_cards == [Card('H', '4'), Card('D', '9'), Card('D', '5'), Card('S', '5'), Card('H', '5')]

    players = hand.players
    assert players['0Human0'].chips == 11883.23 and players['0Human0'].position == 1 \
           and players['0Human0'].player_cards is None
    assert players['MMAsherdog'].chips == 9850 and players['MMAsherdog'].position == 2 \
           and players['MMAsherdog'].player_cards == [Card('C', '7'), Card('H', '7')]
    assert players['Stefan11222'].chips == 24855.34 and players['Stefan11222'].position == 3 \
           and players['Stefan11222'].player_cards == [Card('S', 'A'), Card('S', 'J')]
    assert players['ga207'].chips == 10787.41 and players['ga207'].position == 6 \
           and players['ga207'].player_cards is None

    # Check preflop actions
    assert hand.preflop_actions == [Action('Stefan11222', ActionType.SMALLBLIND, 50.),
                                    Action('ga207', ActionType.BIGBLIND, 100.),
                                    Action('0Human0', ActionType.FOLD),
                                    Action('MMAsherdog', ActionType.RAISE, 250.),
                                    Action('Stefan11222', ActionType.RAISE, 1200.),
                                    Action('ga207', ActionType.FOLD),
                                    Action('MMAsherdog', ActionType.CALL, 950.)]


    # Check flop actions
    assert hand.flop_actions == [Action('Stefan11222', ActionType.BET, 624.25),
                                 Action('MMAsherdog', ActionType.CALL, 624.25)]

    # Check turn actions
    assert hand.turn_actions == [Action('Stefan11222', ActionType.BET, 2472.03),
                                 Action('MMAsherdog', ActionType.CALL, 2472.03)]

    # Check river actions
    assert hand.river_actions == [Action('Stefan11222', ActionType.CHECK),
                                  Action('MMAsherdog', ActionType.BET, 5553.72),
                                  Action('Stefan11222', ActionType.CALL, 5553.72)]