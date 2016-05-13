import game_graphics as gg
import fileutils as fu
import numpy as np

def reset_for_next_run(game):
    game.set_fingers()
    game.trial_count = 0
    reset_for_next_trial(game)
    game.run_count += 1

def reset_for_next_trial(game):
    game.timers['rest'].soft_reset()
    game.timers['cue'].soft_reset()
    game.current_finger = game.finger_list[game.trial_count]
    game.trial_count += 1
    game.timers['press_limit'].count_limit_hit = False
    game.timers['press_limit'].count = 0
    game.timers['feedback'].count_limit_hit = False
    game.timers['feedback'].count = 0
    gg.draw_keyboard(game, 'rest')

def run_rest(game):
    ###########
    # . * . . #
    ###########
    gg.draw_keyboard(game, 'rest')

def run_cue(game):
    ###########
    # . * . . #
    ###########
    gg.draw_keyboard(game, 'cue')

def run_press(game):
    ###########
    # . I . . #
    ###########
    gg.draw_keyboard(game, 'press')
    if (game.force_array[game.current_finger]
            >= game.PRESS_FORCE_THRESHOLD):
        game.current_press_complete = True
        game.feedback_force_array[:] = game.force_array[:]
        for finger in range(len(game.force_array)):
            if game.feedback_force_array[finger] >= game.MIN_KEY_FORCE:
                game.best_feedback_force_array[finger] = min(
                    game.best_feedback_force_array[finger],
                    game.feedback_force_array[finger])

def run_feedback(game):
    ###########
    # i I i i #
    ###########
    gg.draw_keyboard(game, 'feedback')

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

def reset_for_next_press(game):
    game.last_trial_recorded_bool = False
    gg.draw_keyboard(game, mode='rest')
    game.timers['press'].reset()
    game.current_press_complete = False
    game.ready_for_press = False
    game.timers['press_limit'].time_limit_hit = False
    game.timers['feedback'].time_limit_hit = False
