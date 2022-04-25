from typing import List, Dict

from action import Action
from core.card import Card
from core.types import ActionType, GameType
from player import Player
from regexp import *


def create_card(val: str):
    rank, suit = val[0], val[1].upper()
    return Card(suit, rank)


def create_cards(cards: List[str]):
    return [create_card(c) for c in cards]


class Hand(object):
    @property
    def hand_id(self):
        return f"{self.__id_prefix}_{self.__id}"

    @property
    def game_type(self):
        if self.__game_type == "Hold'em No Limit":
            return GameType.HOLDEM_NO_LIMIT
        elif self.__game_type == "Omaha Pot Limit":
            return GameType.OMAHA_POT_LIMIT
        return GameType.UNKNOWN

    @property
    def big_blind(self) -> float:
        return self.__big_blind

    @property
    def small_blind(self) -> float:
        return self.__small_blind

    @property
    def players(self) -> Dict[str, Player]:
        return self.__players

    @property
    def players_count(self) -> int:
        return len(self.__players)

    @property
    def flop_cards(self) -> List[Card]:
        return self.__flop_cards

    @property
    def turn_cards(self) -> List[Card]:
        return self.__turn_cards

    @property
    def river_cards(self) -> List[Card]:
        return self.__river_cards

    @property
    def preflop_actions(self) -> List[Action]:
        return self.__pre_flop_actions

    @property
    def flop_actions(self) -> List[Action]:
        return self.__flop_actions

    @property
    def turn_actions(self) -> List[Action]:
        return self.__turn_actions

    @property
    def river_actions(self) -> List[Action]:
        return self.__river_actions

    @property
    def total_pot(self) -> float:
        return self.__total_pot

    @property
    def rake(self) -> float:
        return self.__rake

    def __init__(self, id_prefix, lines: List[str]):
        self.__id_prefix = id_prefix
        self.__turn_cards = []
        self.__flop_cards = []
        self.__river_cards = []

        self.__pre_flop_actions = []
        self.__flop_actions = []
        self.__turn_actions = []
        self.__river_actions = []

        self.__players = {}
        self.__skip_players = []
        self.__extract_game_type_and_hand_id(lines[0])
        self.__extract_button(lines[1])
        iteration = 2
        while True:
            if not lines[iteration].startswith('Seat'):
                break
            self.__extract_player(lines[iteration])
            iteration += 1

        while True:
            if 'small blind' in lines[iteration]:
                self.__extract_small_blind_player(lines[iteration])
                iteration += 1
                break
            iteration += 1
        while True:
            if 'big blind' in lines[iteration]:
                self.__extract_big_blind_player(lines[iteration])
                iteration += 1
                break
            iteration += 1

        self.__pre_flop_actions.append(Action(self.__small_blind_player, ActionType.SMALLBLIND, self.__small_blind))
        self.__pre_flop_actions.append(Action(self.__big_blind_player, ActionType.BIGBLIND, self.__big_blind))

        while lines[iteration] != preflop_start:
            iteration += 1

        assert lines[iteration] == preflop_start

        iteration += 1
        if self.__extract_preflop_cards(lines[iteration]):
            iteration += 1

        # Collect all preflop actions
        while iteration < len(lines) and not lines[iteration].startswith(flop_start) and not lines[
            iteration].startswith(showdown) \
                and not lines[iteration].startswith(first_flop_start):
            action = self.__handle_action(lines[iteration])
            if action:
                self.__pre_flop_actions.append(action)
            iteration += 1

        if lines[iteration].startswith(flop_start):
            self.__extract_flop_cards(lines[iteration])
            iteration += 1
            # Collect all flop actions
            while iteration < len(lines) and not lines[iteration].startswith(turn_start) \
                    and not lines[iteration].startswith(showdown):
                action = self.__handle_action(lines[iteration])
                if action:
                    self.__flop_actions.append(action)
                iteration += 1

        if lines[iteration].startswith(turn_start):
            self.__extract_turn_cards(lines[iteration])
            iteration += 1
            while iteration < len(lines) and not lines[iteration].startswith(river_start) and not lines[
                iteration].startswith(showdown):
                action = self.__handle_action(lines[iteration])
                if action:
                    self.__turn_actions.append(action)
                iteration += 1

        if lines[iteration].startswith(river_start):
            self.__extract_river_cards(lines[iteration])
            iteration += 1
            while iteration < len(lines) and not lines[iteration].startswith(showdown):
                action = self.__handle_action(lines[iteration])
                if action:
                    self.__river_actions.append(action)
                iteration += 1

        # Collect summary information
        assert lines[iteration].startswith(showdown), lines[iteration]
        iteration += 1
        self.__extract_total_pot(lines[iteration])
        iteration += 1
        if lines[iteration].startswith('Board'):
            iteration += 1
        # Collect showdown actions
        while iteration < len(lines) and lines[iteration].startswith('Seat'):
            self.__extract_showdown_player_cards(lines[iteration])
            iteration += 1

    def __handle_action(self, line):
        if fold_action_regexp.search(line):
            return self.__extract_fold_action(line)
        elif call_action_regexp.search(line):
            return self.__extract_call_action(line)
        elif bet_action_regexp.search(line):
            return self.__extract_bet_action(line)
        elif check_action_regexp.search(line):
            return self.__extract_check_action(line)
        elif raise_action_regexp.search(line):
            return self.__extract_raise_action(line)
        elif line.find("doesn't show hand") != -1:
            pass
        elif line.find("leaves the table") != -1:
            pass
        elif line.find("Uncalled bet") != -1:
            pass
        elif line.find("is disconnected") != -1:
            pass
        elif line.find("said,") != -1:
            pass
        elif line.find(" collected ") != -1:
            pass
        elif line.find("has timed out") != -1:
            pass
        elif line.find("joins the table at seat") != -1:
            pass
        elif line.find("is connected") != -1:
            pass
        elif line.find("was removed from the table for failing to post") != -1:
            pass
        else:
            return None

    def __extract_total_pot(self, line):
        match = summary_total_pot_regexp.search(line)
        self.__total_pot = float(match.group(1))
        self.__rake = float(match.group(3))

    def __extract_fold_action(self, line):
        player = fold_action_regexp.search(line).group(1)
        return Action(player, ActionType.FOLD)

    def __extract_check_action(self, line):
        player = check_action_regexp.search(line).group(1)
        return Action(player, ActionType.CHECK)

    def __extract_call_action(self, line):
        match = call_action_regexp.search(line)
        player, call_size = match.group(1), float(match.group(2))
        return Action(player, ActionType.CALL, call_size)

    def __extract_bet_action(self, line):
        match = bet_action_regexp.search(line)
        player, bet_size = match.group(1), float(match.group(2))
        return Action(player, ActionType.BET, bet_size)

    def __extract_raise_action(self, line):
        match = raise_action_regexp.search(line)
        player, raise_size, bet_size = match.group(1), float(match.group(2)), float(match.group(4))
        return Action(player, ActionType.RAISE, float(bet_size))

    def __extract_preflop_cards(self, line) -> bool:
        match = preflop_cards_regexp.search(line)
        if not match:
            return False
        player = match.group(1)
        cards = create_cards(match.group(2).split())
        if player and cards:
            self.players[player].player_cards = cards
            return True
        return False

    def __extract_flop_cards(self, line):
        self.__flop_cards = create_cards(flop_cards_regexp.search(line).group(1).split(' '))

    def __extract_turn_cards(self, line):
        match = turn_cards_regexp.search(line)
        c = match.group(1).split(' ')
        c.append(match.group(2))
        self.__turn_cards = create_cards(c)

    def __extract_river_cards(self, line):
        match = river_cards_regexp.search(line)
        c = match.group(1).split(' ')
        c.append(match.group(2))
        self.__river_cards = create_cards(c)

    def __extract_showdown_player_cards(self, line):
        match = showdown_player_cards_regexp.search(line)
        if not match:
            return
        player = match.group(2)
        cards = create_cards(match.group(3).split())
        if player and cards:
            if player.endswith(' (big blind)'):
                player = player[:-12]
            if player.endswith(' (small blind)'):
                player = player[:-14]
            if player.endswith(' (button)'):
                player = player[:-9]
            self.players[player].player_cards = cards

    def __extract_button(self, line):
        self.__button = button_regexp.search(line).group(1)

    def __extract_game_type_and_hand_id(self, line):
        match = game_type_regexp.search(line)
        self.__id = match.group(1)
        self.__game_type = match.group(2)
        self.__small_blind, self.__big_blind = match.group(3).split('/')
        self.__small_blind = self.__small_blind.strip(currency)
        self.__big_blind = self.__big_blind.strip(currency)
        self.__small_blind, self.__big_blind = float(self.__small_blind), float(self.__big_blind)

    def __extract_skip_players(self, line):
        self.__skip_players.append(skip_player_regexp.search(line).group(1))

    def __extract_small_blind_player(self, line):
        self.__small_blind_player = small_blind_regexp.search(line).group(1)

    def __extract_big_blind_player(self, line):
        self.__big_blind_player = big_blind_regexp.search(line).group(1)

    def __extract_player(self, line):
        match = seat_regexp.search(line)
        self.__players[match.group(2)] = Player(match.group(1), match.group(2), match.group(3))
