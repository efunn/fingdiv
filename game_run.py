import game_graphics as gg
import fileutils as fu
import numpy as np

def reset_for_next_run(game):
    game.set_sequences()
    reset_for_next_sequence_trial(game)
    game.run_count += 1
    game.trial_count = 1
    reset_score_stats(game)

def reset_score_stats(game):
    game.execution_time_array = np.array(([]))
    game.error_array = np.array([])
    game.points_total = 0
    game.last_trial_recorded_bool = False

def reset_for_next_sequence_trial(game):
    game.timers['cue'].soft_reset()
    reset_for_next_sequence_execution(game, draw_progress_bool=False)
    game.current_sequence = game.sequence_list[
        np.mod(game.trial_count,len(game.sequence_list))]
    game.trial_count += 1
    game.timers['score'].count_limit_hit = False
    game.timers['score'].count = 0

def run_sequence_cue(game):
    #############
    # 5 3 4 1 2 #
    #############
    gg.draw_cue(game)

def run_sequence_move(game):
    #|*|*|* * *
    #############
    #     *     #
    #############
    if (game.current_key != game.last_key_pressed
            and game.current_key != 'none'):
        game.last_key_pressed = game.current_key
        if game.current_key == game.current_sequence[game.key_in_sequence]:
            game.sequence_progress[game.key_in_sequence] = 'correct'
            game.key_in_sequence += 1
        else:
            game.sequence_progress[game.key_in_sequence] = 'wrong'
            game.key_in_sequence += 1
    if game.key_in_sequence > 4:
        game.current_sequence_complete = True
    gg.draw_sequence_progress(game)

def run_sequence_score(game):
    #############
    #   * * *   #
    #############

    if not(game.last_trial_recorded_bool):
        record_score(game)
        game.last_trial_recorded_bool = True
    if game.sequence_progress == game.SEQUENCE_CORRECT:
        color = game.ACTIVE_COLOR
        if (game.timers['move'].time < 0.8*np.median(game.execution_time_array)
                and game.mode != 'scan'):
            gg.draw_fixation(game, xpos=.5*game.SCREEN_WIDTH+game.KEY_XPOS, color=color)
            gg.draw_fixation(game, xpos=.5*game.SCREEN_WIDTH-game.KEY_XPOS, color=color)
        elif game.timers['move'].time > 1.2*np.median(game.execution_time_array):
            color = game.SLOW_COLOR
    else:
        color = game.WRONG_COLOR
    gg.draw_fixation(game, xpos=.5*game.SCREEN_WIDTH, color=color)

def run_sequence_score_rest(game):
    gg.draw_fixation(game, xpos=.5*game.SCREEN_WIDTH, color=game.FIXATION_COLOR)

def record_score(game):
    fu.trial_record(game, game.f_trial)
    game.execution_time_array = np.append(game.execution_time_array,
                                          game.timers['move'].time)
    if game.sequence_progress == game.SEQUENCE_CORRECT:
        game.error_array = np.append(game.error_array, 0)
        game.points_total += 1
        if game.timers['move'].time < 0.8*np.median(game.execution_time_array):
            game.points_total += 2
        elif game.timers['move'].time > 1.2*np.median(game.execution_time_array):
            game.points_total -= 1
    else:
        game.error_array = np.append(game.error_array, 1)
        game.points_total -= 1

def reset_for_next_sequence_execution(game, draw_progress_bool=True):
    game.last_trial_recorded_bool = False
    gg.draw_fixation(game, xpos=.5*game.SCREEN_WIDTH, color=game.FIXATION_COLOR)
    game.timers['move'].reset()
    game.timers['move_limit'].soft_reset()
    game.current_sequence_complete = False
    game.timers['score'].time_limit_hit = False
    game.sequence_progress[:] = game.SEQUENCE_INCOMPLETE
    game.key_in_sequence = 0
    game.last_key_pressed = -1
    if draw_progress_bool:
        gg.draw_sequence_progress(game)

##########################
##########################
##########################

# - five numbers for 2.7s
# - then fixation cross w/ 5 stars above
# - 2.7s to execute in scanner; after 5th press outside scanner
# - star for each press goes green if correct, red if wrong
#   also yellow if greater than 8.9N
# - 0.8s feedback phase
# - green if 100% (+1), red if <100% (-1)
#   blue if 100% but 20% slower than median (0)
#   3 green stars if 100% and 20% faster than median (+3)
# - repeat 3 times in scanner, 5 times outside
# - 12 sequences total (just do 4?), no 3 finger ascending/descending
#   no indication of which were selected, they did a 5 person pilot

# - pre-test: 36 trials, 8 sequences, each repeated twice per hand (10 trials)

# - each training session:
#   24 runs (96 trials, 480 sequence executions)
# - after each run:
#   given MT, error rate, and points
#   if error rate < 20%: go faster
#   if error rate > 20%: focus on accuracy

# - scanning:
#   8 runs of 16 trials (4 per sequence)
#   
