from enum import Enum, auto
from typing import List
import copy
from core.card import Card


class ReadyCombinationType(Enum):
    STRAIGHT_FLUSH = auto()
    FOUR_OF_A_KIND = auto()
    FULL_HOUSE = auto()
    FLUSH = auto()
    STRAIGHT = auto()
    THREE_OF_A_KIND = auto()
    TWO_PAIR = auto()
    ONE_PAIR = auto()
    HIGH_CARD = auto()
    AIR = auto()


class DrawCombinationType(Enum):
    FLUSH_DRAW = auto()
    DOUBLE_STRAIGHT_DRAW = auto()
    GUTSHOT = auto()
    NO_DRAW_COMBINATIONS = auto()
    BACKDOOR_STRAIGHT = auto()
    BACKDOOR_FLUSH = auto()
    DOUBLE_BACKDOOR = auto()


class Combination(object):
    def __init__(self, board: List[Card], player_cards: List[Card]):
        self.__board = board
        self.__player_cards = player_cards
        self.RANK_LOOKUP = "23456789TJQKA"
        self.SUIT_LOOKUP = "SCDH"

    @staticmethod
    def features_names():
        return [
            "ready_combination",
        ]

    @property
    def board(self):
        return self.__board

    @property
    def player_cards(self):
        return self.__player_cards

    def ready_combination(self) -> ReadyCombinationType:
        all_cards = self.board + self.player_cards
        board = self.board
        hand = self.player_cards
        rank_counters_all = [0] * len(self.RANK_LOOKUP)
        rank_counters_board = [0] * len(self.RANK_LOOKUP)
        rank_counters_hand = [0] * len(self.RANK_LOOKUP)
        suit_counters_all = [0] * len(self.SUIT_LOOKUP)

        for card in hand:
            rank_counters_hand[self.RANK_LOOKUP.index(card.rank)] += 1
        for card in board:
            rank_counters_board[self.RANK_LOOKUP.index(card.rank)] += 1
        for card in all_cards:
            rank_counters_all[self.RANK_LOOKUP.index(card.rank)] += 1
            suit_counters_all[self.SUIT_LOOKUP.index(card.suit)] += 1

        highest_player_card = self.RANK_LOOKUP.index(
            sorted(self.player_cards, key=lambda c: self.RANK_LOOKUP.index(c.rank))[-1].rank)

        sorted_board_cards = sorted(self.board, key=lambda c: self.RANK_LOOKUP.index(c.rank))
        highest_board_card = None
        if sorted_board_cards:
            highest_board_card = self.RANK_LOOKUP.index(sorted_board_cards[-1].rank)

        if self.__is_flush(suit_counters_all) and self.__is_straight(rank_counters_all):
            return ReadyCombinationType.STRAIGHT_FLUSH
        elif self.__is_four_of_a_kind(rank_counters_all):
            return ReadyCombinationType.FOUR_OF_A_KIND
        elif self.__is_full_house(rank_counters_all):
            return ReadyCombinationType.FULL_HOUSE
        elif self.__is_flush(suit_counters_all):
            return ReadyCombinationType.FLUSH
        elif self.__is_straight(rank_counters_all):
            return ReadyCombinationType.STRAIGHT
        elif self.__is_three_of_a_kind(rank_counters_all):
            return ReadyCombinationType.THREE_OF_A_KIND
        elif self.__is_two_pairs(rank_counters_all):
            return ReadyCombinationType.TWO_PAIR
        elif self.__is_one_pair(rank_counters_all):
            return ReadyCombinationType.ONE_PAIR
        elif self.__is_high_card(highest_player_card, highest_board_card):
            return ReadyCombinationType.HIGH_CARD
        return ReadyCombinationType.AIR

    def __is_high_card(self, highest_player_card, highest_board_card):
        return highest_board_card and highest_board_card < highest_player_card

    def __is_four_of_a_kind(self, rank_counters):
        for c in rank_counters:
            if c >= 4:
                return True
        return False

    def __is_full_house(self, rank_counters):
        pair_ranks, set_ranks = set(), set()
        for rank, c in enumerate(rank_counters):
            if c >= 2:
                pair_ranks.add(rank)
            if c >= 3:
                set_ranks.add(rank)
        return len(pair_ranks.union(set_ranks)) >= 2 and len(set_ranks) > 0

    def __is_flush(self, suit_counters):
        for c in suit_counters:
            if c >= 5:
                return True
        return False

    def __is_straight(self, rank_counters):
        r_c = copy.deepcopy(rank_counters)
        r_c.insert(0, r_c[-1])
        seq = 0
        for c in r_c:
            if c > 0:
                seq += 1
                if seq == 5:
                    return True
            else:
                seq = 0
        return False

    def __is_three_of_a_kind(self, rank_counters):
        for c in rank_counters:
            if c >= 3:
                return True
        return False

    def __is_two_pairs(self, rank_counters):
        p = 0
        for c in rank_counters:
            if c >= 2:
                p += 1
        return p >= 2

    def __is_one_pair(self, rank_counters):
        for c in rank_counters:
            if c >= 2:
                return True
        return False

    def draw_combination(self) -> DrawCombinationType:
        all_cards = self.board + self.player_cards
        board = self.board
        hand = self.player_cards
        rank_counters_all = [0] * len(self.RANK_LOOKUP)
        rank_counters_board = [0] * len(self.RANK_LOOKUP)
        suit_counters_hand = [0] * len(self.SUIT_LOOKUP)
        suit_counters_board = [0] * len(self.SUIT_LOOKUP)
        rank_counters_hand = [0] * len(self.RANK_LOOKUP)
        suit_counters_all = [0] * len(self.SUIT_LOOKUP)

        for card in hand:
            rank_counters_hand[self.RANK_LOOKUP.index(card.rank)] += 1
            suit_counters_hand[self.SUIT_LOOKUP.index(card.suit)] += 1
        for card in board:
            rank_counters_board[self.RANK_LOOKUP.index(card.rank)] += 1
            suit_counters_board[self.SUIT_LOOKUP.index(card.suit)] += 1
        for card in all_cards:
            rank_counters_all[self.RANK_LOOKUP.index(card.rank)] += 1
            suit_counters_all[self.SUIT_LOOKUP.index(card.suit)] += 1

        if self.__is_flush_draw(suit_counters_all):
            return DrawCombinationType.FLUSH_DRAW
        elif self.__is_backdoor_straight(rank_counters_all, rank_counters_board) and \
                self.__is_backdoor_flush(suit_counters_all, rank_counters_board, suit_counters_board):
            return DrawCombinationType.DOUBLE_BACKDOOR
        elif self.__is_double_straight_draw(rank_counters_all):
            return DrawCombinationType.DOUBLE_STRAIGHT_DRAW
        elif self.__is_gutshot(rank_counters_all):
            return DrawCombinationType.GUTSHOT
        elif self.__is_backdoor_straight(rank_counters_all, rank_counters_board):
            return DrawCombinationType.BACKDOOR_STRAIGHT
        elif self.__is_backdoor_flush(suit_counters_all, rank_counters_board, suit_counters_board):
            return DrawCombinationType.BACKDOOR_FLUSH
        return DrawCombinationType.NO_DRAW_COMBINATIONS

    def __is_flush_draw(self, suit_counters):
        """флэш дро"""
        for c in suit_counters:
            if c == 4:
                return True
        return False

    def __is_double_straight_draw(self, rank_counters):
        """двусторонний стрит дро"""
        rank_counters = [rank_counters[-1]] + rank_counters[:]
        for i in range(len(rank_counters) - 5):
            counter = 0
            if rank_counters[i] == 0 or rank_counters[i + 4] == 0:
                for j in range(5):
                    if rank_counters[i + j]:
                        counter += 1
                if counter == 4:
                    return True
        return False

    def __is_gutshot(self, rank_counters):
        """гатшот"""
        rank_counters = [rank_counters[-1]] + rank_counters[:]
        for i in range(len(rank_counters) - 5):
            counter = 0
            if rank_counters[i] == 1 and rank_counters[i + 4] == 1:
                for j in range(5):
                    if rank_counters[i + j]:
                        counter += 1
                if counter == 4:
                    return True
        return False

    def __is_backdoor_flush(self, suit_counters_all, rank_counter_board, suit_counters_board):
        """бэкдор флэш дро"""
        if sum(rank_counter_board) == 3:
            for board_suit in suit_counters_board:
                if board_suit == 3:
                    return False
            for all_suit in suit_counters_all:
                if all_suit == 3:
                    return True

    def __is_backdoor_straight(self, rank_counters_all, rank_counters_board):
        """бэкдор стрит дро"""
        if sum(rank_counters_board) == 3:
            rank_counters_all = [rank_counters_all[-1]] + rank_counters_all[:]
            for i in range(len(rank_counters_board) - 5):
                counter = 0
                for j in range(5):
                    if rank_counters_board[i + j]:
                        counter += 1
                if counter == 3:
                    return False
            for i in range(len(rank_counters_all) - 5):
                counter = 0
                for j in range(5):
                    if rank_counters_all[i + j]:
                        counter += 1
                if counter == 3:
                    return True
