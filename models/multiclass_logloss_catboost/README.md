### 1. Параметры модели (model_params):
+ eval_metric, MultiClass
+ iterations, 500
+ fold_permutation_block, 64
+ leaf_estimation_method, Newton
+ observations_to_bootstrap, TestOnly
+ grow_policy, SymmetricTree
+ boosting_type, Plain
+ ctr_history_unit, Sample
+ feature_border_type, GreedyLogSum
+ bayesian_matrix_reg, 0.10000000149011612
+ pinned_memory_bytes, 104857600
+ random_strength, 0.800000011920929
+ boost_from_average, False
+ gpu_cat_features_storage, GpuRam
+ fold_size_loss_normalization, False
+ max_ctr_complexity, 4
+ model_size_reg, 0.5
+ class_names, ['BET', 'CALL', 'CHECK', 'FOLD', 'RAISE']
+ loss_function, MultiClass
+ learning_rate, 0.029999999329447743
+ score_function, Cosine
+ bootstrap_type, Bernoulli


### 2. Score :
+ `0.7713050871983516`


### 3. Features:
+ General type:
    + 'street',  
    + 'total_call_amount',
    + 'total_check_amount',
    + 'total_bet_amount',
    + 'total_raise_amount',
    + 'total_fold_amount',
    + 'street_call_amount',
    + 'street_check_amount',
    + 'street_bet_amount',
    + 'street_raise_amount',
    + 'street_fold_amount',
    + 'player_position',
    + 'players_in_pot',
    + 'after_us_decision_players',
    + 'current_pot_size',
    + 'player_stack_size',
    + 'percent_deposited_of_current_stack',
    + 'pay_for_continue_play',
    + 'current_bet',
+ Board:
    + 'board_ace_amount',
    + 'board_king_amount',
    + 'board_queen_amount',
    + 'board_jack_amount',
    + 'board_10_amount',
    + 'board_9_amount',
    + 'board_8_amount', 
    + 'board_7_amount',
    + 'board_6_amount',
    + 'board_5_amount', 
    + 'board_4_amount',
    + 'board_3_amount',
    + 'board_2_amount',
    + 'board_spades_amount', 
    + 'board_hearts_amount',
    + 'board_diamonds_amount',
    + 'board_clubs_amount',
+ Combination:
    + 'ready_combination'         


### 4. Notebook link:
     https://gitlab.com/bestpok-ai/pokerai-master/-/blob/master/notebooks/catboost_multiclass%20.ipynb


### 5. Dataset link:
