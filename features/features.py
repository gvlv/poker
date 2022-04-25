from collections import Counter
from typing import List, Dict

from action import Action
from core.types import Street, ActionType
from player import Player


class Feature(object):
    def street_start(self, street: Street):
        raise NotImplemented()

    def handle_action(self, action: Action):
        raise NotImplemented()

    @property
    def value(self):
        raise NotImplemented()


class CurrentBet(Feature):
    """
    Размер текущей ставки
    """

    def __init__(self):
        self.__current_bet = 0.0
        self.__player2bet = {}

    def street_start(self, street: Street):
        self.__current_bet = 0.0
        self.__player2bet = Counter()

    def handle_action(self, action: Action):
        if action.action_type in [ActionType.SMALLBLIND, ActionType.BIGBLIND, ActionType.BET, ActionType.RAISE]:
            self.__current_bet = action.bet_size
            self.__player2bet[action.player] = action.bet_size
        if action.action_type == ActionType.CALL:
            self.__current_bet = action.bet_size
            self.__player2bet[action.player] += action.bet_size

    def get_player_bet(self, player_name: str) -> float:
        return self.__player2bet.get(player_name, 0.0)

    @property
    def value(self):
        return self.__current_bet


class ActionTotalAmount(Feature):
    """
    Сколько Action определенного типа было совершено всеми игроками на всех улицах
    """

    def __init__(self, action_type: ActionType):
        self.__action_type = action_type
        self.__action_amount: int = 0

    def street_start(self, street: Street):
        pass

    def handle_action(self, action: Action):
        if action.action_type == self.__action_type:
            self.__action_amount += 1

    @property
    def value(self):
        return self.__action_amount

    @value.setter
    def value(self, x):
        self.__action_amount = x


class CallTotalAmount(ActionTotalAmount):
    def __init__(self):
        super().__init__(ActionType.CALL)


class CheckTotalAmount(ActionTotalAmount):
    def __init__(self):
        super().__init__(ActionType.CHECK)


class BetTotalAmount(ActionTotalAmount):
    def __init__(self):
        super().__init__(ActionType.BET)


class RaiseTotalAmount(ActionTotalAmount):
    def __init__(self):
        super().__init__(ActionType.RAISE)


class FoldTotalAmount(ActionTotalAmount):
    def __init__(self):
        super().__init__(ActionType.FOLD)


class ActionStreetAmount(ActionTotalAmount):
    """
    Сколько Action определенного типа было совершено всеми игроками начиная с последней улицы
    """

    def __init__(self, action_type: ActionType):
        super().__init__(action_type)

    def street_start(self, street: Street):
        self.value = 0


class CallStreetAmount(ActionStreetAmount):
    def __init__(self):
        super().__init__(ActionType.CALL)


class CheckStreetAmount(ActionStreetAmount):
    def __init__(self):
        super().__init__(ActionType.CHECK)


class BetStreetAmount(ActionStreetAmount):
    def __init__(self):
        super().__init__(ActionType.BET)


class RaiseStreetAmount(ActionStreetAmount):
    def __init__(self):
        super().__init__(ActionType.RAISE)


class FoldStreetAmount(ActionStreetAmount):
    def __init__(self):
        super().__init__(ActionType.FOLD)


class PlayerPosition(Feature):
    """
    Позиция игрока за столом, sb-0, bb-1, utg-2 etc...
    """

    def __init__(self, player_name: str):
        self.__player_name = player_name
        self.__current_move = 0
        self.__player2position = {}

    def street_start(self, street: Street):
        self.__current_move = 0
        self.__player2position = {}

    def handle_action(self, action: Action):
        if action.player not in self.__player2position:
            self.__player2position[action.player] = self.__current_move
        self.__current_move += 1

    @property
    def value(self):
        return self.__player2position.get(self.__player_name, self.__current_move)


class PotSize(Feature):
    """
    Текущий размер банка
    """

    def __init__(self, current_bet: CurrentBet):
        self.__pot_size = 0
        self.__current_bet = current_bet

    def street_start(self, street: Street):
        pass

    def handle_action(self, action: Action):
        if action.action_type in [ActionType.SMALLBLIND, ActionType.BIGBLIND, ActionType.CALL, ActionType.BET]:
            self.__pot_size += action.bet_size
        if action.action_type == ActionType.RAISE:
            self.__pot_size += action.bet_size - self.__current_bet.get_player_bet(action.player)

    @property
    def value(self):
        return self.__pot_size


class LastRaisePlayer(Feature):
    """
    Имя игрока который последним сделал bb/bet/raise
    """

    def __init__(self):
        self.__last_raise_player = None

    def street_start(self, street: Street):
        self.__last_raise_player = None

    def handle_action(self, action: Action):
        if action.action_type in [ActionType.BIGBLIND, ActionType.BET, ActionType.RAISE]:
            self.__last_raise_player = action.player

    @property
    def value(self) -> str:
        return self.__last_raise_player


class FoldPlayers(Feature):
    """
    Игроки которые в рамках данной сессии уже сделали FOLD
    """

    def __init__(self):
        self.__fold_players = set()

    def street_start(self, street: Street):
        pass

    def handle_action(self, action: Action):
        if action.action_type in [ActionType.FOLD]:
            self.__fold_players.add(action.player)

    @property
    def value(self) -> List[str]:
        return list(self.__fold_players)


class PlayersInPot(Feature):
    """
    Сколько на текущий момент игроков в банке (Себя мы тут тоже считаем)
    """

    def __init__(self):
        self.__players_in_pot = set()

    def street_start(self, street: Street):
        pass

    def handle_action(self, action: Action):
        if action.action_type == ActionType.FOLD:
            self.__players_in_pot.discard(action.player)
        elif action.action_type in [ActionType.CALL, ActionType.BET, ActionType.RAISE]:
            self.__players_in_pot.add(action.player)

    @property
    def value(self):
        return len(self.__players_in_pot)


class PlayerChips(Feature):
    """
    Сколько на текущий момент у нас денег
    """

    def __init__(self, player_name: str, chips: float, current_bet: CurrentBet):
        self.__player_name = player_name
        self.__chips = chips
        self.__current_bet = current_bet

    def street_start(self, street: Street):
        pass

    def handle_action(self, action: Action):
        if action.player == self.__player_name:
            if action.action_type in [ActionType.BIGBLIND, ActionType.SMALLBLIND, ActionType.CALL, ActionType.BET,
                                      ]:
                self.__chips -= action.bet_size
            elif action.action_type == ActionType.RAISE:
                self.__chips -= (action.bet_size - self.__current_bet.get_player_bet(action.player))

    @property
    def value(self):
        return self.__chips


class PaidOnAllStreets(Feature):
    """
    Сколько денег мы уже заплатили на ВСЕХ улицах
    """

    def __init__(self, init_chips: float, player_chips: PlayerChips):
        self.__init_chips = init_chips
        self.__player_chips = player_chips

    def street_start(self, street: Street):
        pass

    def handle_action(self, action: Action):
        pass

    @property
    def value(self):
        return self.__init_chips - self.__player_chips.value


class MoneyPaidOnCurrentStreet(Feature):
    """
    Сколько денег мы уже внесли в рамках текущей улицы
    """

    def __init__(self, player_name: str):
        self.__player_name = player_name
        self.__amount = 0.0

    def street_start(self, street: Street):
        self.__amount = 0.0

    def handle_action(self, action: Action):
        if action.player == self.__player_name:
            if action.action_type in [ActionType.BIGBLIND, ActionType.SMALLBLIND, ActionType.CALL, ActionType.BET]:
                self.__amount += action.bet_size
            elif action.action_type == ActionType.RAISE:
                self.__amount = action.bet_size

    @property
    def value(self):
        return self.__amount


class ShouldPayForContinue(Feature):
    """
    Сколько денег мы должны довнести чтобы продолжить играть
    """

    def __init__(self, paid_on_curr_street: MoneyPaidOnCurrentStreet, current_bet: CurrentBet):
        self.__paid_on_curr_street = paid_on_curr_street
        self.__current_bet = current_bet

    def street_start(self, street: Street):
        pass

    def handle_action(self, action: Action):
        pass

    @property
    def value(self):
        return self.__current_bet.value - self.__paid_on_curr_street.value


class AfterUsDecisionPlayers(Feature):
    """
    Количество игроков которые примут решение после того как примем мы
    """

    def __init__(self,
                 player_name: str,
                 ordered_players: List[Player],
                 fold_players: FoldPlayers,
                 last_raise_player: LastRaisePlayer):
        self.__player_name = player_name
        self.__ordered_players = ordered_players
        self.__fold_players = fold_players
        self.__last_raise_player = last_raise_player

    def street_start(self, street: Street):
        pass

    def handle_action(self, action: Action):
        pass

    @property
    def value(self):
        players_count = len(self.__ordered_players)
        our_pos = FeaturesPack.get_our_position(self.__ordered_players, self.__player_name) % players_count
        next_pos = (our_pos + 1) % players_count
        answer = 0
        if self.__last_raise_player.value is None:
            finish_player = self.__ordered_players[our_pos].nick
        else:
            finish_player = self.__last_raise_player.value

        while self.__ordered_players[next_pos].nick != finish_player:
            if self.__ordered_players[next_pos].nick not in self.__fold_players.value:
                answer += 1
            next_pos = (next_pos + 1) % len(self.__ordered_players)

        if self.__ordered_players[next_pos].nick not in self.__fold_players.value and \
                self.__ordered_players[next_pos].nick != self.__ordered_players[our_pos].nick and \
                self.__ordered_players[next_pos].nick != finish_player:
            answer += 1
        return answer


class FeaturesPack(object):
    def __init__(self, players: Dict[str, Player], player_name: str, big_blind: float):
        self.player_name = player_name
        self.big_blind = big_blind
        current_bet = CurrentBet()
        player_chips = PlayerChips(player_name, players[player_name].chips, current_bet)
        paid_on_curr_street = MoneyPaidOnCurrentStreet(player_name)
        fold_players = FoldPlayers()
        last_raise_player = LastRaisePlayer()
        self.__pack = [
            CallTotalAmount(),
            CheckTotalAmount(),
            BetTotalAmount(),
            RaiseTotalAmount(),
            FoldTotalAmount(),

            CallStreetAmount(),
            CheckStreetAmount(),
            BetStreetAmount(),
            RaiseStreetAmount(),
            FoldStreetAmount(),

            PlayerPosition(player_name),
            PlayersInPot(),
            PotSize(current_bet),
            player_chips,
            PaidOnAllStreets(players[player_name].chips, player_chips),
            current_bet,
            paid_on_curr_street,
            ShouldPayForContinue(paid_on_curr_street, current_bet),
            last_raise_player,
            fold_players,
        ]

    @staticmethod
    def features_names():
        return [
            'hand_id',
            'player_name',
            'street',
            'action',
            'player_bet_size',

            'total_call_amount',
            'total_check_amount',
            'total_bet_amount',
            'total_raise_amount',
            'total_fold_amount',

            'street_call_amount',
            'street_check_amount',
            'street_bet_amount',
            'street_raise_amount',
            'street_fold_amount',

            'player_position',
            'players_in_pot',
            'current_pot_size',
            'player_stack_size',
            'paid_on_all_streets',
            'pay_for_continue_play',
            'current_bet',
        ]

    @staticmethod
    def order_players(players_dict: Dict):
        players = []
        for k, v in players_dict.items():
            players.append(v)
        players.sort(key=lambda p: p.position)
        return players

    @staticmethod
    def get_our_position(players: List[Player], nick: str):
        for pos, player in enumerate(players):
            if player.nick == nick:
                return pos
        raise Exception(f"Can't find player with name: {nick}")

    def collect_action(self, action: Action):
        for feature in self.__pack:
            feature.handle_action(action)

    def street_start(self, street: Street):
        for feature in self.__pack:
            feature.street_start(street)

    def collect_features(self):
        return [
            self.__collect_feature(CallTotalAmount),
            self.__collect_feature(CheckTotalAmount),
            self.__collect_feature(BetTotalAmount),
            self.__collect_feature(RaiseTotalAmount),
            self.__collect_feature(FoldTotalAmount),

            self.__collect_feature(CallStreetAmount),
            self.__collect_feature(CheckStreetAmount),
            self.__collect_feature(BetStreetAmount),
            self.__collect_feature(RaiseStreetAmount),
            self.__collect_feature(FoldStreetAmount),

            self.__collect_feature(PlayerPosition),  # Player position
            self.__collect_feature(PlayersInPot),  # Players in pot
            self.__collect_feature(PotSize) / self.big_blind,  # Current pot size
            self.__collect_feature(PlayerChips) / self.big_blind,  # Current player stack size
            self.__collect_feature(PaidOnAllStreets) / self.big_blind,  # Paid on all streets
            self.__collect_feature(ShouldPayForContinue) / self.big_blind,  # How much we should pay for continue play
            self.__collect_feature(CurrentBet) / self.big_blind
        ]

    def __collect_feature(self, feature_type: type):
        x = list(filter(lambda f: isinstance(f, feature_type), self.__pack))[0]
        return x.value
