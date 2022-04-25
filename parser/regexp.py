import re

currency = '$€£'

preflop_start = '*** HOLE CARDS ***'
flop_start = '*** FLOP ***'
first_flop_start = '*** FIRST FLOP ***'
turn_start = '*** TURN ***'
river_start = '*** RIVER ***'
showdown = '*** SUMMARY ***'

hand_regexp = re.compile(r"^Hand #[0-9]+$")
game_type_regexp = re.compile(r".*Hand #([0-9].*):  (Hold'em No Limit|Omaha Pot Limit) \((.\d+(\.\d+)?\/.\d+(\.\d+)?).*\).*")
seat_regexp = re.compile('^Seat (\d): (.*) \((.\d+(\.\d+)?) in chips\)')
button_regexp = re.compile('^Table.*Seat #(\d) is the button')
skip_player_regexp = re.compile('^(.*) will be allowed to play after the button')
small_blind_regexp = re.compile('^(.*): posts small blind.*')
big_blind_regexp = re.compile('^(.*): posts big blind.*')
preflop_cards_regexp = re.compile("^Dealt to (.*) \[(.*)\]")
fold_action_regexp = re.compile("^(.*): folds")
call_action_regexp = re.compile("^(.*): calls [$€£]?(\d+(\.\d+)?)")
bet_action_regexp = re.compile("^(.*): bets [$€£]?(\d+(\.\d+)?)")
raise_action_regexp = re.compile("^(.*): raises [$€£]?(\d+(\.\d+)?) to [$€£]?(\d+(\.\d+)?)")
check_action_regexp = re.compile("^(.*): checks")
flop_cards_regexp = re.compile('^\*\*\* FLOP \*\*\* \[(.*)\]')
turn_cards_regexp = re.compile('^\*\*\* TURN \*\*\* \[(.*)\] \[(.*)\]')
river_cards_regexp = re.compile('^\*\*\* RIVER \*\*\* \[(.*)\] \[(.*)\]')
summary_total_pot_regexp = re.compile('^Total pot [$€£]?(\d+(\.\d+)?).*Rake [$€£]?(\d+(\.\d+)?)')
showdown_player_cards_regexp = re.compile("^Seat (\d+): (.*) showed \[(.*)\]")