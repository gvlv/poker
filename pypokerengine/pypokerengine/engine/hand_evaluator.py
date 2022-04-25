from functools import reduce
from itertools import groupby

from pypokerengine.engine.card import Card


class HandEvaluator:

  HIGHCARD      = 0
  ONEPAIR       = 1 << 8
  TWOPAIR       = 1 << 9
  THREECARD     = 1 << 10
  STRAIGHT      = 1 << 11
  FLASH         = 1 << 12
  FULLHOUSE     = 1 << 13
  FOURCARD      = 1 << 14
  STRAIGHTFLASH = 1 << 15

  HAND_STRENGTH_MAP = {
      HIGHCARD: "HIGHCARD",
      ONEPAIR: "ONEPAIR",
      TWOPAIR: "TWOPAIR",
      THREECARD: "THREECARD",
      STRAIGHT: "STRAIGHT",
      FLASH: "FLASH",
      FULLHOUSE: "FULLHOUSE",
      FOURCARD: "FOURCARD",
      STRAIGHTFLASH: "STRAIGHTFLASH"
  }

  @classmethod
  def gen_hand_rank_info(self, hole, community):
    hand = self.eval_hand(hole, community)
    row_strength = self.mask_hand_strength(hand)
    strength = self.HAND_STRENGTH_MAP[row_strength]
    hand_high = self.mask_hand_high_rank(hand)
    hand_low = self.mask_hand_low_rank(hand)
    hole_high = self.mask_hole_high_rank(hand)
    hole_low = self.mask_hole_low_rank(hand)

    hole_list = []
    for card in hole:
        hole_list.append(str(card))

    strongest_cards = []

    cards = hole + community

    if strength == "HIGHCARD":
        strongest_cards.append(sorted([card.rank for card in hole], reverse=True)[0])

    if strength == "ONEPAIR":
        strongest_cards.append(self.eval_onepair(cards) >> 4)

    if strength == "TWOPAIR":
        strongest_cards.extend(self.search_twopair(cards))

    if strength == "THREECARD":
        strongest_cards.append(self.search_threecard(cards))

    if strength == "STRAIGHT":
        low_card = self.search_straight(cards)
        strongest_cards.append(low_card)
        strongest_cards.append(low_card + 4)

    if strength == "FLASH":
        strongest_cards.append(self.search_flash(cards))

    if strength == "FULLHOUSE":
        strongest_cards.extend(self.search_fullhouse(cards))

    if strength == "FOURCARD":
        strongest_cards.append(self.search_fourcard(cards))

    if strength == "STRAIGHTFLASH":
        low_card = self.search_straightflash(cards)
        strongest_cards.append(low_card)
        strongest_cards.append(low_card + 4)

    strongest_cards_values = []
    for card in strongest_cards:
        strongest_cards_values.extend(Card.RANK_MAP[card])

    return {
        "hand" : {
          "strength" : strength,
          "strongest_cards" : strongest_cards_values,
          "high" : hand_high,
          "low" : hand_low
        },
        "hole" : {
          "high" : hole_high,
          "low" : hole_low
        },
        "list" : hole_list
    }

  @classmethod
  def eval_hand(self, hole, community):
    ranks = sorted([card.rank for card in hole])
    hole_flg = ranks[1] << 4 | ranks[0]
    hand_flg = self.calc_hand_info_flg(hole, community) << 8
    return hand_flg | hole_flg

  # Return Format
  # [Bit flg of hand][rank1(4bit)][rank2(4bit)]
  # ex.)
  #       HighCard hole card 3,4   =>           100 0011
  #       OnePair of rank 3        =>        1 0011 0000
  #       TwoPair of rank A, 4     =>       10 1110 0100
  #       ThreeCard of rank 9      =>      100 1001 0000
  #       Straight of rank 10      =>     1000 1010 0000
  #       Flash of rank 5          =>    10000 0101 0000
  #       FullHouse of rank 3, 4   =>   100000 0011 0100
  #       FourCard of rank 2       =>  1000000 0010 0000
  #       straight flash of rank 7 => 10000000 0111 0000
  @classmethod
  def calc_hand_info_flg(self, hole, community):
    cards = hole + community
    if self.is_straightflash(cards): return self.STRAIGHTFLASH | self.eval_straightflash(cards)
    if self.is_fourcard(cards): return self.FOURCARD | self.eval_fourcard(cards)
    if self.is_fullhouse(cards): return self.FULLHOUSE | self.eval_fullhouse(cards)
    if self.is_flash(cards): return self.FLASH | self.eval_flash(cards)
    if self.is_straight(cards): return self.STRAIGHT | self.eval_straight(cards)
    if self.is_threecard(cards): return self.THREECARD | self.eval_threecard(cards)
    if self.is_twopair(cards): return self.TWOPAIR | self.eval_twopair(cards)
    if self.is_onepair(cards): return self.ONEPAIR | (self.eval_onepair(cards))
    return self.eval_holecard(hole)

  @classmethod
  def eval_holecard(self, hole):
    ranks = sorted([card.rank for card in hole])
    return ranks[1] << 4 | ranks[0]

  @classmethod
  def is_onepair(self, cards):
    return self.eval_onepair(cards) != 0

  @classmethod
  def eval_onepair(self, cards):
    rank = 0
    memo = 0  # bit memo
    for card in cards:
      mask = 1 << card.rank
      if memo & mask != 0: rank = max(rank, card.rank)
      memo |= mask
    return rank << 4

  @classmethod
  def is_twopair(self, cards):
    return len(self.search_twopair(cards)) == 2

  @classmethod
  def eval_twopair(self, cards):
    ranks = self.search_twopair(cards)
    return ranks[0] << 4 | ranks[1]

  @classmethod
  def search_twopair(self, cards):
    ranks = []
    memo = 0
    for card in cards:
      mask = 1 << card.rank
      if memo & mask != 0: ranks.append(card.rank)
      memo |= mask
    return sorted(ranks)[::-1][:2]

  @classmethod
  def is_threecard(self, cards):
    return self.search_threecard(cards) != -1

  @classmethod
  def eval_threecard(self, cards):
    return self.search_threecard(cards) << 4

  @classmethod
  def search_threecard(self, cards):
    rank = -1
    bit_memo = reduce(lambda memo,card: memo + (1 << (card.rank-1)*3), cards, 0)
    for r in range(2, 15):
      bit_memo >>= 3
      count = bit_memo & 7
      if count >= 3: rank = r
    return rank

  @classmethod
  def is_straight(self, cards):
    return self.search_straight(cards) != -1

  @classmethod
  def eval_straight(self, cards):
    return self.search_straight(cards) << 4

  @classmethod
  def search_straight(self, cards):
    bit_memo = reduce(lambda memo, card: memo | 1 << card.rank, cards, 0)
    rank = -1
    straight_check = lambda acc, i: acc & (bit_memo >> (r+i) & 1) == 1
    for r in range(2, 15):
      if reduce(straight_check, range(5), True): rank = r
    return rank

  @classmethod
  def is_flash(self, cards):
    return self.search_flash(cards) != -1

  @classmethod
  def eval_flash(self, cards):
    return self.search_flash(cards) << 4

  @classmethod
  def search_flash(self, cards):
    best_suit_rank = -1
    fetch_suit = lambda card: card.suit
    fetch_rank = lambda card: card.rank
    for suit, group_obj in groupby(sorted(cards, key=fetch_suit), key=fetch_suit):
      g = list(group_obj)
      if len(g) >= 5:
        max_rank_card = max(g, key=fetch_rank)
        best_suit_rank = max(best_suit_rank, max_rank_card.rank)
    return best_suit_rank

  @classmethod
  def is_fullhouse(self, cards):
    r1, r2 = self.search_fullhouse(cards)
    return r1 and r2

  @classmethod
  def eval_fullhouse(self, cards):
    r1, r2 = self.search_fullhouse(cards)
    return r1 << 4 | r2

  @classmethod
  def search_fullhouse(self, cards):
    fetch_rank = lambda card: card.rank
    three_card_ranks, two_pair_ranks = [], []
    for rank, group_obj in groupby(sorted(cards, key=fetch_rank), key=fetch_rank):
      g = list(group_obj)
      if len(g) >= 3:
        three_card_ranks.append(rank)
      if len(g) >= 2:
        two_pair_ranks.append(rank)
    two_pair_ranks = [rank for rank in two_pair_ranks if not rank in three_card_ranks]
    if len(three_card_ranks) == 2:
      two_pair_ranks.append(min(three_card_ranks))
    max_ = lambda l: None if len(l)==0 else max(l)
    return max_(three_card_ranks), max_(two_pair_ranks)

  @classmethod
  def is_fourcard(self, cards):
    return self.eval_fourcard(cards) != 0

  @classmethod
  def eval_fourcard(self, cards):
    rank = self.search_fourcard(cards)
    return rank << 4

  @classmethod
  def search_fourcard(self, cards):
    fetch_rank = lambda card: card.rank
    for rank, group_obj in groupby(sorted(cards, key=fetch_rank), key=fetch_rank):
      g = list(group_obj)
      if len(g) >= 4:
        return rank
    return 0

  @classmethod
  def is_straightflash(self, cards):
    return self.search_straightflash(cards) != -1

  @classmethod
  def eval_straightflash(self, cards):
    return self.search_straightflash(cards) << 4

  @classmethod
  def search_straightflash(self, cards):
    flash_cards = []
    fetch_suit = lambda card: card.suit
    for suit, group_obj in groupby(sorted(cards, key=fetch_suit), key=fetch_suit):
      g = list(group_obj)
      if len(g) >= 5: flash_cards = g
    return self.search_straight(flash_cards)

  @classmethod
  def mask_hand_strength(self, bit):
    mask = 511 << 16
    return (bit & mask) >> 8  # 511 = (1 << 9) -1

  @classmethod
  def mask_hand_high_rank(self, bit):
    mask = 15 << 12
    return (bit & mask) >> 12

  @classmethod
  def mask_hand_low_rank(self, bit):
    mask = 15 << 8
    return (bit & mask) >> 8

  @classmethod
  def mask_hole_high_rank(self, bit):
    mask = 15 << 4
    return (bit & mask) >> 4

  @classmethod
  def mask_hole_low_rank(self, bit):
    mask = 15
    return bit & mask

