from scripts.const import Actions, Seats
import random as rand


class Preflop: 
    
    def __init__(self, player_seat, raiser_seat, limper, bb, bet_count, last_bet_size, hole_card, valid_actions,
                 player_uuid, action_histories):
        self.player_seat = player_seat
        self.raiser_seat = raiser_seat
        self.limper = limper
        self.bb = bb
        self.bet_count = bet_count
        self.last_bet_size = last_bet_size
        self.hole_card = hole_card
        self.valid_actions = valid_actions
        self.player_uuid = player_uuid
        self.action_histories = action_histories

    def declare_action(self):
        action = Actions.FOLD
        amount = 0

        if self.bet_count >= 3:
            self.raiser_seat = None

        if self.raiser_seat is not None and (self.player_seat + 'vs' + self.raiser_seat) in _strategies:
            strategies = _strategies[self.player_seat + 'vs' + self.raiser_seat]
        else:
            strategies = _strategies[self.player_seat]

        # Если префлоп рейз сайзингом 9бб и выше, то 88+, АJ,AQ,AK играются через 3бет на пол стэка (на 4бет - пушим).
        # Если оппонент заколировал наш 3бет, то пушим любой флоп (не важно попали мы как то в него или нет)
        if self.bet_count < 4 and self.last_bet_size >= 9 * self.bb:
            strategies = strategies.copy()
            strategies.append(Strategy(
                    cards=['AA', 'AKs', 'AKo', 'AQs', 'AQo', 'AJs', 'AJo', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44'],
                    action_function=lambda preflop: _3bet_half_5bet_push(preflop)
                ))

        for s in strategies:
            if self.hole_card in s.cards:
                action, amount = s.declare_action(self)

        if self.bet_count == 1 and action == Actions.CALL:
            action = Actions.RAISE
            amount = _raise_amount(self)

        if self.bet_count >= 3:
            street_history = self.action_histories['preflop']
            raises = list(filter(lambda a: a['action'] in ['RAISE'] and a['uuid'] == self.player_uuid, street_history))
            if len(raises) == 0 and self.hole_card not in strategies[0].cards:
                action = Actions.FOLD
                amount = 0

        return action, amount


class Strategy(object):

    def __init__(self, cards, action_function):
        self.cards = cards
        self._action_function = action_function

    def declare_action(self, preflop):
        return self._action_function(preflop)


_strategies = {
    "UTG": [
        Strategy(
            cards=['AA', 'KK'],
            action_function=lambda preflop: _4bet_push(preflop)
        ), Strategy(
            cards=['AKs', 'AQs', 'AJs', 'ATs', 'AKo', 'KQs', 'KJs', 'QQ', 'QJs', 'JJ', 'JTs', 'TT', '99', '88', '77'],
            action_function=lambda preflop: _call_3bet(preflop)
        ), Strategy(
            cards=['A8s', 'A7s', 'A5s'],
            action_function=lambda preflop: _4bet_fold(preflop)
        ), Strategy(
            cards=['A9s', 'KTs', 'K9s', 'AQo', 'KQo', 'QTs', 'AJo', 'KJo', 'ATo', 'T9s', '98s', '87s', '66', '55'],
            action_function=lambda preflop: _call(preflop)
        )],
    "MP": [
        Strategy(
            cards=['AA', 'KK'],
            action_function=lambda preflop: _4bet_push(preflop)
        ), Strategy(
            cards=['AKs', 'AQs', 'AJs', 'ATs', 'A9s', 'AKo', 'KQs', 'KJs', 'AQo' 'QQ', 'QJs', 'JJ', 'JTs', 'TT', '99',
                   '88', '77', '66', '55'],
            action_function=lambda preflop: _call_3bet(preflop)
        ), Strategy(
            cards=['A7s', 'A5s', 'A4s', 'A3s'],
            action_function=lambda preflop: _4bet_fold(preflop)
        ), Strategy(
            cards=['A8s', 'A6s', 'KTs', 'K9s', 'K8s', 'KQo', 'QTs', 'Q9s', 'AJo', 'KJo', 'QJo', 'J9s', 'J8s', 'ATo',
                   'KTo' 'QTo', 'JTo', 'T9s', 'T8s', '98s', '87s', '44'],
            action_function=lambda preflop: _call(preflop)
        )],
    "MPvsUTG": [
        Strategy(
            cards=['AA', 'A5s', 'KK'],
            action_function=lambda preflop: _3bet_5bet_push_100(preflop)
        ), Strategy(
            cards=['AKs', 'AKo', 'QQ'],
            action_function=lambda preflop: _3bet_4bet_call_100(preflop)
        ), Strategy(
            cards=['98s'],
            action_function=lambda preflop: _3bet_4bet_call_50(preflop)
        ), Strategy(
            cards=['A4s', 'A3s', 'A2s', 'J9s'],
            action_function=lambda preflop: _3bet_4bet_fold_100(preflop)
        ), Strategy(
            cards=['ATs', 'KTs', 'QTs', 'JTs', 'T9s'],
            action_function=lambda preflop: _3bet_4bet_fold_50(preflop)
        ), Strategy(
            cards=['AQs', 'AJs', 'KQs', 'KJs', 'AQo', 'KQo', 'QJs', 'JJ', 'TT', '99', '88', '77', '66', '55'],
            action_function=lambda preflop: _call(preflop)
        )],
    "CO": [
        Strategy(
            cards=['AA', 'AKs', 'AKo', 'KK', 'QQ'],
            action_function=lambda preflop: _4bet_push(preflop)
        ), Strategy(
            cards=['AQs', 'AJs', 'ATs', 'A9s', 'A5s', 'A4s', 'A3s', 'KQs', 'KJs', 'KTs', 'AQo', 'QJs', 'QTs', 'JJ',
                   'JTs', 'TT', 'T9s', 'T8s', '99', '98s', '88', '87s', '77', '66', '55'],
            action_function=lambda preflop: _call_3bet(preflop)
        ), Strategy(
            cards=['A8s', 'A2s', 'K9s', 'AJo', 'J9s', '76s'],
            action_function=lambda preflop: _4bet_fold(preflop)
        ), Strategy(
            cards=['A7s', 'A6s', 'K8s', 'K7s', 'K6s', 'K5s', 'KQo', 'Q9s', 'Q8s', 'Q7s', 'KJo', 'QJo', 'J8s', 'J7s',
                   'ATo', 'KTo', 'QTo', 'JTo', 'T7s', 'A9o', '97s', '86s', '44', '33', '22'],
            action_function=lambda preflop: _call(preflop)
        )],
    "COvsUTG": [
        Strategy(
            cards=['AA', 'A5s', 'KK'],
            action_function=lambda preflop: _3bet_5bet_push_100(preflop)
        ), Strategy(
            cards=['AKs', 'AKo', 'QQ'],
            action_function=lambda preflop: _3bet_4bet_call_100(preflop)
        ), Strategy(
            cards=['98s'],
            action_function=lambda preflop: _3bet_4bet_call_50(preflop)
        ), Strategy(
            cards=['A4s', 'A3s', 'A2s', 'J9s'],
            action_function=lambda preflop: _3bet_4bet_fold_100(preflop)
        ), Strategy(
            cards=['ATs', 'KTs', 'QTs', 'JTs', 'T9s'],
            action_function=lambda preflop: _3bet_4bet_fold_50(preflop)
        ), Strategy(
            cards=['AQs', 'AJs', 'KQs', 'KJs', 'AQo', 'KQo', 'QJs', 'JJ', 'TT', '99', '88', '77', '66', '55'],
            action_function=lambda preflop: _call(preflop)
        )],
    "COvsMP": [
        Strategy(
            cards=['AA', 'A5s', 'KK'],
            action_function=lambda preflop: _3bet_5bet_push_100(preflop)
        ), Strategy(
            cards=['AKs', 'AKo', 'QQ'],
            action_function=lambda preflop: _3bet_4bet_call_100(preflop)
        ), Strategy(
            cards=['98s'],
            action_function=lambda preflop: _3bet_4bet_call_50(preflop)
        ), Strategy(
            cards=['A4s', 'A3s', 'A2s', 'J9s'],
            action_function=lambda preflop: _3bet_4bet_fold_100(preflop)
        ), Strategy(
            cards=['ATs', 'KTs', 'QTs', 'JTs', 'T9s'],
            action_function=lambda preflop: _3bet_4bet_fold_50(preflop)
        ), Strategy(
            cards=['AQs', 'AJs', 'KQs', 'KJs', 'AQo', 'KQo', 'QJs', 'JJ', 'TT', '99', '88', '77', '66', '55'],
            action_function=lambda preflop: _call(preflop)
        )],
    "BU": [
        Strategy(
            cards=['AA', 'AKs', 'AKo', 'KK', 'QQ', 'JJ'],
            action_function=lambda preflop: _4bet_push(preflop)
        ), Strategy(
            cards=['AQs', 'AJs', 'ATs', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s', 'A4s', 'A3s', 'KQs', 'KJs', 'KTs', 'K9s',
                   'AQo', 'KQo', 'QJs', 'QTs', 'Q9s', 'AJo', 'KJo', 'QJo', 'JTs', 'J9s', 'J8s', 'TT', 'T9s', 'T8s',
                   '99', '98s', '97s', '88', '87s', '86s', '77', '75s', '66', '65s', '55', '54s', '44', '33', '22'],
            action_function=lambda preflop: _call_3bet(preflop)
        ), Strategy(
            cards=['A2s', 'K8s', 'K7s', 'K6s', 'Q8s', 'ATo', '76s', '64s'],
            action_function=lambda preflop: _4bet_fold(preflop)
        ), Strategy(
            cards=['K5s', 'K4s', 'K3s', 'K2s', 'Q7s', 'Q6s', 'Q5s', 'Q4s', 'Q3s', 'Q2s', 'J7s', 'J6s', 'KTo', 'QTo',
                   'JTo', 'T7s', 'A9o', 'K9o', 'Q9o', 'J9o', 'T9o', '96s', 'A8o', 'K8o', 'Q8o', 'J8o', 'T8o', '98o',
                   '85s', 'A7o', '74s', 'A6o', '63s', 'A5o', '53s', 'A4o', '43s', 'A3o', 'A2o'],
            action_function=lambda preflop: _call(preflop)
        )],
    "BUvsUTG": [
        Strategy(
            cards=['AA', 'A5s', 'KK'],
            action_function=lambda preflop: _3bet_5bet_push_100(preflop)
        ), Strategy(
            cards=['AKs', 'AKo', 'QQ'],
            action_function=lambda preflop: _3bet_4bet_call_100(preflop)
        ), Strategy(
            cards=['98s'],
            action_function=lambda preflop: _3bet_4bet_call_50(preflop)
        ), Strategy(
            cards=['KTs', 'QTs', 'T9s'],
            action_function=lambda preflop: _3bet_4bet_fold_50(preflop)
        ), Strategy(
            cards=['AQs', 'AJs', 'ATs', 'A4s', 'A3s', 'A2s', 'KQs', 'KJs', 'AQo', 'KQo', 'QJs', 'JJ', 'JTs', 'J9s',
                   'TT', 'T8s' '99', '88', '77', '66', '55'],
            action_function=lambda preflop: _call(preflop)
        )],
    "BUvsMP": [
        Strategy(
            cards=['AA', 'A5s', 'KK'],
            action_function=lambda preflop: _3bet_5bet_push_100(preflop)
        ), Strategy(
            cards=['AKs', 'AKo', 'QQ'],
            action_function=lambda preflop: _3bet_4bet_call_100(preflop)
        ), Strategy(
            cards=['98s'],
            action_function=lambda preflop: _3bet_4bet_call_50(preflop)
        ), Strategy(
            cards=['KTs', 'QTs', 'T9s'],
            action_function=lambda preflop: _3bet_4bet_fold_50(preflop)
        ), Strategy(
            cards=['AQs', 'AJs', 'ATs', 'A4s', 'A3s', 'A2s', 'KQs', 'KJs', 'AQo', 'KQo', 'QJs', 'JJ', 'JTs', 'J9s',
                   'TT', 'T8s', '99', '88', '77', '66', '55'],
            action_function=lambda preflop: _call(preflop)
        )],
    "BUvsCO": [
        Strategy(
            cards=['AA', 'AKs', 'AKo', 'KK', 'QQ', '33', '22'],
            action_function=lambda preflop: _3bet_5bet_push_100(preflop)
        ), Strategy(
            cards=['88', '77'],
            action_function=lambda preflop: _3bet_5bet_push_50(preflop)
        ), Strategy(
            cards=['AQs', 'JJ'],
            action_function=lambda preflop: _3bet_4bet_call_100(preflop)
        ), Strategy(
            cards=['KQs', 'QJs', 'JTs', 'T9s', '98s', '87s'],
            action_function=lambda preflop: _3bet_4bet_call_50(preflop)
        ), Strategy(
            cards=['A5s', 'A4s', 'A3s', 'A2s', '65s'],
            action_function=lambda preflop: _3bet_4bet_fold_100(preflop)
        ), Strategy(
            cards=['ATs', 'A9s', 'KJs', 'KTs', 'AQo', 'KQo', 'QTs', 'AJo', '76s'],
            action_function=lambda preflop: _3bet_4bet_fold_50(preflop)
        ), Strategy(
            cards=['AJs', 'K9s', 'Q9s', 'J9s', 'TT', '99', '66', '55', '44'],
            action_function=lambda preflop: _call(preflop)
        )],
    "SB": [
        Strategy(
            cards=['AA', 'KK', 'QQ', 'JJ', 'TT'],
            action_function=lambda preflop: _4bet_push(preflop)
        ), Strategy(
            cards=['AKs', 'AQs', 'AJs', 'ATs', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s', 'A4s', 'A3s', 'AKo', 'KQs', 'KJs',
                   'KTs', 'K9s', 'K8s', 'AQo', 'KQo', 'QJs', 'QTs', 'Q9s', 'AJo', 'KJo', 'QJo', 'JTs', 'J9s', 'T9s',
                   'T8s', '99', '98s', '97s', '88', '87s', '86s', '77', '76s', '66', '65s', '55', '54s', '44'],
            action_function=lambda preflop: _call_3bet(preflop)
        ), Strategy(
            cards=['A2s', 'K7s', 'K6s', 'Q8s', 'Q7s', 'J8s', 'ATo', '75s', '64s'],
            action_function=lambda preflop: _4bet_fold(preflop)
        ), Strategy(
            cards=['K5s', 'K4s', 'K3s', 'K2s', 'Q6s', 'Q5s', 'Q4s', 'Q3s', 'Q2s', 'J7s', 'J6s', 'J5s', 'J4s', 'J3s',
                   'J2s', 'KTo', 'QTo', 'JTo', 'T7s', 'T6s', 'T5s', 'T4s', 'T3s', 'T2s', 'A9o', 'K9o', 'Q9o', 'J9o',
                   'T9o', '96s', 'A8o', 'K8o', 'Q8o', 'J8o', 'T8o', '98o', '85s', 'A7o', 'K7o', 'Q7o', '74s', 'A6o',
                   '63s', 'A5o', '53s', 'A4o', '43s', 'A3o', '33', 'A2o', '22'],
            action_function=lambda preflop: _call(preflop)
        )],
    "SBvsUTG": [
        Strategy(
            cards=['AA', 'A5s', 'KK'],
            action_function=lambda preflop: _3bet_5bet_push_100(preflop)
        ), Strategy(
            cards=['AKs'],
            action_function=lambda preflop: _3bet_4bet_call_100(preflop)
        ), Strategy(
            cards=['ATs', 'JTs', 'T9s'],
            action_function=lambda preflop: _3bet_4bet_fold_100(preflop)
        ), Strategy(
            cards=['AQs', 'AJs', 'AKo', 'KQs', 'KJs', 'KTs', 'QQ', 'QJs', 'QTs', 'JJ', 'TT', '99', '88', '77'],
            action_function=lambda preflop: _3bet_4bet_fold_50(preflop)
        )],
    "SBvsMP": [
        Strategy(
            cards=['AA', 'A5s', 'KK'],
            action_function=lambda preflop: _3bet_5bet_push_100(preflop)
        ), Strategy(
            cards=['AKs'],
            action_function=lambda preflop: _3bet_4bet_call_100(preflop)
        ), Strategy(
            cards=['ATs', 'JTs', 'T9s'],
            action_function=lambda preflop: _3bet_4bet_fold_100(preflop)
        ), Strategy(
            cards=['AQs', 'AJs', 'AKo', 'KQs', 'KJs', 'KTs', 'QQ', 'QJs', 'QTs', 'JJ', 'TT', '99', '88', '77'],
            action_function=lambda preflop: _3bet_4bet_fold_50(preflop)
        )],
    "SBvsCO": [
        Strategy(
            cards=['AA', 'AKs', 'AKo', 'KK', 'QQ', 'JJ', 'TT', '66'],
            action_function=lambda preflop: _3bet_5bet_push_100(preflop)
        ), Strategy(
            cards=['AQs'],
            action_function=lambda preflop: _3bet_4bet_call_100(preflop)
        ), Strategy(
            cards=['A5s', 'A4s', 'A3s', 'A2s', 'AQo', 'T9s', '98s', '87s', '55'],
            action_function=lambda preflop: _3bet_4bet_fold_100(preflop)
        ), Strategy(
            cards=['AJs', 'ATs', 'A9s', 'KQs', 'KJs', 'KTs', 'KQo', 'QJs', 'QTs', 'AJo', 'JTs', '99', '88', '77'],
            action_function=lambda preflop: _call(preflop)
        )],
    "SBvsBU": [
        Strategy(
            cards=['AA', 'AKs', 'AKo', 'KK', 'QQ', 'JJ', 'TT', '55', '44'],
            action_function=lambda preflop: _3bet_5bet_push_100(preflop)
        ), Strategy(
            cards=['AQs'],
            action_function=lambda preflop: _3bet_4bet_call_100(preflop)
        ), Strategy(
            cards=['AJs', 'A8s', 'A7s', 'A6s', 'A5s', 'A4s', 'A3s', 'A2s', 'K9s', 'Q9s', 'J9s', 'T8s', '97s', '76s'],
            action_function=lambda preflop: _3bet_4bet_fold_100(preflop)
        ), Strategy(
            cards=['ATs', 'A9s', 'KQs', 'KJs', 'KTs', 'AQo', 'KQo', 'QJs', 'QTs', 'AJo', 'KJo', 'QJo', 'JTs', 'ATo',
                   'T9s', '99', '98s', '88', '87s', '77', '66'],
            action_function=lambda preflop: _call(preflop)
        )],
    "BB": [
        Strategy(
            cards=['AA', 'AKs', 'AQs', 'AJs', 'ATs', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s', 'A4s', 'A3s', 'A2s', 'AKo',
                   'KK', 'KQs', 'KJs', 'KTs', 'AQo', 'KQo', 'QQ', 'QJs', 'QTs', 'AJo', 'KJo', 'QJo', 'JJ', 'JTs', 'ATo',
                   'KTo', 'TT', 'A9o', '99', '88', '77'],
            action_function=lambda preflop: _isolate(preflop)
        )],
    "BBvsUTG": [
        Strategy(
            cards=['AA', 'AKs', 'A5s', 'KK'],
            action_function=lambda preflop: _3bet_5bet_push_100(preflop)
        ), Strategy(
            cards=['AKo', 'QQ'],
            action_function=lambda preflop: _3bet_4bet_call_50(preflop)
        ), Strategy(
            cards=['A7s', 'A6s'],
            action_function=lambda preflop: _3bet_4bet_fold_100(preflop)
        ), Strategy(
            cards=['ATs', 'KTs', 'QTs', '76s', '65s'],
            action_function=lambda preflop: _3bet_4bet_fold_50(preflop)
        ), Strategy(
            cards=['AQs', 'AJs', 'A9s', 'A8s', 'A4s', 'A3s', 'A2s', 'KQs', 'KJs', 'AQo', 'KQo', 'QJs', 'AJo', 'JJ',
                   'JTs', 'J9s', 'TT', 'T9s', '99', '98s', '88', '87s', '77', '66', '55', '44', '33', '22'],
            action_function=lambda preflop: _call(preflop)
        )],
    "BBvsMP": [
        Strategy(
            cards=['AA', 'AKs', 'A5s'],
            action_function=lambda preflop: _3bet_5bet_push_100(preflop)
        ), Strategy(
            cards=['QQ'],
            action_function=lambda preflop: _3bet_4bet_call_100(preflop)
        ), Strategy(
            cards=['AKo'],
            action_function=lambda preflop: _3bet_4bet_call_50(preflop)
        ), Strategy(
            cards=['AQs', 'A7s', 'A6s'],
            action_function=lambda preflop: _3bet_4bet_fold_100(preflop)
        ), Strategy(
            cards=['ATs', 'KTs', 'QTs', '76s', '65s'],
            action_function=lambda preflop: _3bet_4bet_fold_50(preflop)
        ), Strategy(
            cards=['KK'],
            action_function=lambda preflop: _3bet_push_call(preflop)
        ), Strategy(
            cards=['AJs', 'A9s', 'A8s', 'A4s', 'A3s', 'A2s', 'KQs', 'KJs', 'AQo', 'KQo', 'QJs', 'AJo', 'JJ', 'JTs',
                   'J9s', 'TT', 'T9s', 'T8s', '99', '98s', '97s', '88', '87s', '86s', '77', '66', '55', '44', '33', '22'],
            action_function=lambda preflop: _call(preflop)
        )],
    "BBvsCO": [
        Strategy(
            cards=['AKs', 'AQs', 'AJs', 'A5s', 'AKo', 'KK'],
            action_function=lambda preflop: _3bet_5bet_push_100(preflop)
        ), Strategy(
            cards=['A8s', 'A7s', 'A6s'],
            action_function=lambda preflop: _3bet_4bet_fold_100(preflop)
        ), Strategy(
            cards=['ATs', 'KTs', 'QTs', 'JTs', '76s', '65s', '54s'],
            action_function=lambda preflop: _3bet_4bet_fold_50(preflop)
        ), Strategy(
            cards=['AA', 'QQ', 'JJ'],
            action_function=lambda preflop: _3bet_push_call(preflop)
        ), Strategy(
            cards=['A9s', 'A4s', 'A3s', 'A2s', 'KQs', 'KJs', 'K9s', 'K8s', 'K7s', 'K6s', 'K5s', 'AQo', 'KQo', 'QJs',
                   'Q9s', 'Q8s', 'Q7s', 'AJo', 'KJo', 'QJo', 'J9s', 'J8s', 'ATo', 'KTo', 'QTo', 'TT', 'T9s', 'T8s',
                   '99', '98s', '97s', '88', '87s', '86s', '77', '75s', '66', '64s', '55', '44', '33', '22'],
            action_function=lambda preflop: _call(preflop)
        )],
    "BBvsBU": [
        Strategy(
            cards=['AKs', 'AQs', 'AJs', 'A5s', 'A4s', 'AKo', 'KK', 'QQ', 'JJ'],
            action_function=lambda preflop: _3bet_5bet_push_100(preflop)
        ), Strategy(
            cards=['TT', '77'],
            action_function=lambda preflop: _3bet_5bet_push_50(preflop)
        ), Strategy(
            cards=['T9s', '99', '98s', '88', '87s'],
            action_function=lambda preflop: _3bet_4bet_call_50(preflop)
        ), Strategy(
            cards=['A3s'],
            action_function=lambda preflop: _3bet_4bet_fold_100(preflop)
        ), Strategy(
            cards=['A8s', 'A7s', 'A6s', 'KQs', 'KJs', 'KTs', 'K9s', 'K8s', 'K7s', 'KQo', 'QJs', 'QTs', 'Q9s', 'Q8s',
                   'Q7s', 'JTs', 'J9s', 'J8s', 'J7s', 'T8s', 'T7s', '97s'],
            action_function=lambda preflop: _3bet_4bet_fold_50(preflop)
        ), Strategy(
            cards=['AA'],
            action_function=lambda preflop: _3bet_push_call(preflop)
        ), Strategy(
            cards=['ATs', 'A9s', 'A2s', 'K6s', 'K5s', 'K4s', 'K3s', 'K2s', 'AQo', 'Q6s', 'Q5s', 'Q4s', 'Q3s', 'Q2s',
                   'AJo', 'KJo', 'QJo', 'J6s', 'J5s', 'J4s', 'J3s', 'J2s', 'ATo', 'KTo', 'QTo', 'JTo', 'T6s', 'T5s',
                   'T4s', 'T3s', 'T2s', 'A9o', 'K9o', 'Q9o', 'J9o', 'T9o', '96s', '95s', 'A8o', 'K8o', 'Q8o', 'J8o',
                   'T8o', '98o', '86s', '85s', 'A7o', 'K7o', 'Q7o', '97o', '87o', '76s', '75s', 'A6o', 'K6o', '76o',
                   '66', '65s', '64s', 'A5o', 'K5o', '55', '54s', '53s', 'A4o', '44', '43s', '42s', 'A3o', '33', '32s',
                   'A2o', '22'],
            action_function=lambda preflop: _call(preflop)
        )],
    "BBvsSB": [
        Strategy(
            cards=['AKs', 'A5s', 'A4s', 'AKo', 'KK'],
            action_function=lambda preflop: _3bet_5bet_push_100(preflop)
        ), Strategy(
            cards=['JJ'],
            action_function=lambda preflop: _3bet_4bet_call_100(preflop)
        ), Strategy(
            cards=['AQs', 'AJs', 'KQs', 'JTs', 'T9s', '98s', '87s', '76s'],
            action_function=lambda preflop: _3bet_4bet_call_50(preflop)
        ), Strategy(
            cards=['A3s', 'A2s', 'KJs', 'T8o', '97o', 'A6o', '76o', '54s'],
            action_function=lambda preflop: _3bet_4bet_fold_100(preflop)
        ), Strategy(
            cards=['AQo', 'KQo', 'QJs', '65s'],
            action_function=lambda preflop: _3bet_4bet_fold_50(preflop)
        ), Strategy(
            cards=['AA', 'QQ'],
            action_function=lambda preflop: _3bet_push_call(preflop)
        ), Strategy(
            cards=['ATs', 'A9s', 'A8s', 'A7s', 'A6s', 'KTs', 'K9s', 'K8s', 'K7s', 'K6s', 'K5s', 'K4s', 'K3s', 'K2s',
                   'QTs', 'Q9s', 'Q8s', 'Q7s', 'Q6s', 'Q5s', 'Q4s', 'Q3s', 'Q2s', 'AJo', 'KJo', 'QJo', 'J9s', 'J8s',
                   'J7s', 'J6s', 'J5s', 'J4s', 'J3s', 'J2s', 'ATo', 'KTo', 'QTo', 'JTo', 'TT', 'T8s', 'T7s', 'T6s',
                   'T5s', 'T4s', 'T3s', 'T2s', 'A9o', 'K9o', 'Q9o', 'J9o', 'T9o', '99', '97s', '96s', '95s', 'A8o',
                   'K8o', 'Q8o', 'J8o', '98o', '88', '86s', '85s', 'A7o', 'K7o', 'Q7o', '87o', '77', '75s', 'K6o',
                   '66', '64s', 'A5o', 'K5o', '55', '53s', 'A4o', '44', '43s', '42s', 'A3o', '33', '32s', 'A2o', '22'],
            action_function=lambda preflop: _call(preflop)
        )]
}


def _4bet_fold(preflop):
    all_in = preflop.valid_actions[2]['amount']['max']
    if preflop.bet_count < 4:
        return Actions.RAISE, _raise_amount(preflop)
    return Actions.FOLD, all_in


def _call_3bet(preflop):
    if preflop.bet_count < 3:
        return Actions.RAISE, _raise_amount(preflop)
    return Actions.CALL, preflop.valid_actions[1]['amount']


def _4bet_push(preflop):
    all_in = preflop.valid_actions[2]['amount']['max']
    if preflop.bet_count < 4:
        return Actions.RAISE, _raise_amount(preflop)
    return Actions.RAISE, all_in


def _call(preflop):
    return Actions.CALL, preflop.valid_actions[1]['amount']


def _3bet_5bet_push_100(preflop):
    all_in = preflop.valid_actions[2]['amount']['max']
    if preflop.bet_count < 5:
        return Actions.RAISE, _raise_amount(preflop)
    return Actions.RAISE, all_in


def _3bet_5bet_push_50(preflop):
    r = rand.random()
    all_in = preflop.valid_actions[2]['amount']['max']
    if preflop.bet_count < 5:
        if r < 0.5:
            return Actions.RAISE, _raise_amount(preflop)
        else:
            return Actions.RAISE, all_in
    return Actions.RAISE, all_in


def _3bet_4bet_call_100(preflop):
    if preflop.bet_count < 4:
        return Actions.RAISE, _raise_amount(preflop)
    return Actions.CALL, preflop.valid_actions[1]['amount']


def _3bet_4bet_call_50(preflop):
    r = rand.random()
    if preflop.bet_count < 4:
        if r < 0.5:
            return Actions.RAISE, _raise_amount(preflop)
        else:
            return Actions.CALL, preflop.valid_actions[1]['amount']
    return Actions.CALL, preflop.valid_actions[1]['amount']


def _3bet_4bet_fold_100(preflop):
    if preflop.bet_count < 4:
        return Actions.RAISE, _raise_amount(preflop)
    return Actions.FOLD, 0


def _3bet_4bet_fold_50(preflop):
    r = rand.random()
    if preflop.bet_count < 4:
        if r < 0.5:
            return Actions.RAISE, _raise_amount(preflop)
        else:
            return Actions.FOLD, 0
    return Actions.FOLD, 0


def _3bet_push_call(preflop):
    all_in = preflop.valid_actions[2]['amount']['max']
    if preflop.bet_count < 3:
        return Actions.RAISE, _raise_amount(preflop)
    else:
        r = rand.random()
        if r < 0.5:
            return Actions.RAISE, all_in
        else:
            return Actions.CALL, preflop.valid_actions[1]['amount']


def _3bet_half_5bet_push(preflop):
    half = preflop.bb * 50
    all_in = preflop.valid_actions[2]['amount']['max']
    if preflop.bet_count < 4:
        return Actions.RAISE, half
    return Actions.RAISE, all_in


def _isolate(preflop):
    if preflop.limper == Seats[1]:
        amount = 4 * preflop.bb
    else:
        amount = 5 * preflop.bb
    return Actions.RAISE, amount


def _raise_amount(preflop):
    if preflop.bet_count == 1:
        if preflop.limper is None:
            return 2.5 * preflop.bb
        # Out of position
        if Seats.index(preflop.limper) > Seats.index(preflop.player_seat):
            return 4 * preflop.bb
        else:
            return 5 * preflop.bb

    if preflop.bet_count == 2:
        coef = preflop.bet_count / preflop.bb
        # Out of position
        if Seats.index(preflop.raiser_seat) > Seats.index(preflop.player_seat):
            if coef >= 5:
                return 16 * preflop.bb
            if coef >= 4.5:
                return 15 * preflop.bb
            if coef >= 4:
                return 13 * preflop.bb
            if coef >= 3.5:
                return 12 * preflop.bb
            if coef >= 3:
                return 10.5 * preflop.bb
            if coef >= 2.5:
                return 10 * preflop.bb
            return 9 * preflop.bb
        # In position
        else:
            if coef >= 5:
                return 14 * preflop.bb
            if coef >= 4.5:
                return 12 * preflop.bb
            if coef >= 4:
                return 11 * preflop.bb
            if coef >= 3.5:
                return 10 * preflop.bb
            if coef >= 3:
                return 9 * preflop.bb
            if coef >= 2.5:
                return 8 * preflop.bb
            return 7 * preflop.bb

    if preflop.bet_count == 3:
        return 2.3 * preflop.bb

    all_in = preflop.valid_actions[2]['amount']['max']
    if all_in / preflop.bb > 150:
        return 180 * preflop.bb
    return 100 * preflop.bb
