import re

currency = '$€£'

preflop_start = '** Dealing down cards **'
flop_start = '** Dealing flop **'
turn_start = '** Dealing turn **'
river_start = '** Dealing river **'
showdown = '** Summary **'

hand_regexp = re.compile('#Game No : [0-9]')
seat_regexp = re.compile('^Seat (\d): (.*) \( (.\d+(\.\d+)?) \)') # +
button_regexp = re.compile('^Seat (\d) is the button')  # +
small_blind_regexp = re.compile('(.*) posts small blind.*')  # +
big_blind_regexp = re.compile('(.*) posts big blind.*') # +
preflop_cards_regexp = re.compile("(.*) shows \[(.*)\]") # +
fold_action_regexp = re.compile("^(.*) folds") #  +
call_action_regexp = re.compile("(.*) calls [$€£]?(\d+(\.\d+)?)")
bet_action_regexp = re.compile("(.*) bets [$€£]?(\d+(\.\d+)?)")
raise_action_regexp = re.compile("(.*) raises [$€£]?(\d+(\.\d+)?)")
check_action_regexp = re.compile("(.*) checks")
flop_cards_regexp = re.compile('\*\* Dealing flop \*\* \[(.*)\]')   # +
turn_card_regexp = re.compile('\*\* Dealing turn \*\* \[(.*)\]')    # +
river_card_regexp = re.compile('\*\* Dealing river \*\* \[(.*)\]')  # +
summary_total_pot_regexp = re.compile('(.*) collected [$€£]?(\d+(\.\d+)?)')