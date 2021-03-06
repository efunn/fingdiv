import yaml, sys
import pygame
import numpy as np
import fileutils as fu
from timer import Timer

def generate_constants(game):
    with open('config.yaml') as f:
        game.CONFIG = yaml.load(f)

    # screen
    game.SCREEN_WIDTH = 1024
    game.SCREEN_HEIGHT = 768
    game.FRAME_RATE = 60
    game.KEY_YPOS = 0.5*game.SCREEN_HEIGHT
    game.KEY_XPOS = 0.15*game.SCREEN_HEIGHT
    game.KEY_HEIGHT = 0.4*game.SCREEN_HEIGHT
    game.KEY_WIDTH = 0.1*game.SCREEN_WIDTH
    game.FRAME_HEIGHT = 0.2*game.SCREEN_HEIGHT
    game.BEST_LINE_HEIGHT = 4
    game.NUMBER_OFFSET = 10
    game.STAR_OFFSET = 40
    game.FIXATION_OFFSET = -5
    game.FRAME_RECT_BORDER_WIDTH = 0.01*game.SCREEN_WIDTH

    # daq
    game.DEVICE_NAME = 'Dev4/ai0:3'
    game.LP_FILT_FREQ = 14
    game.LP_FILT_ORDER = 3
    game.FORCE_PARAMS = 'force_params.txt'

    # colors
    game.BG_COLOR = 40,40,40
    game.CUE_COLOR = 40,160,40
    game.PRESS_COLOR = 100,100,100
    game.GOOD_CORR_COLOR = 60,120,60
    game.BAD_CORR_COLOR = 160,40,40
    game.BEST_COLOR = 200,200,200
    game.PASSIVE_COLOR = 70,70,70
    game.FIXATION_COLOR = 255,255,255

    # time
    game.REST_TIME = 1.35
    game.CUE_TIME = 1.35
    game.PRESS_TIME = 1.35
    game.FEEDBACK_TIME = 1.35

    # trials and runs
    game.PRESSES_PER_TRIAL = {'debug': 5,
                              'test': 5,
                              'train': 5,
                              'scan': 5}
    game.TRIALS_PER_RUN = {'debug': 4,
                           'test': 16,
                           'train': 16,
                           'scan': 24}
    game.RUNS_PER_EXPERIMENT = {'debug': 4,
                                'test': 10,
                                'train': 15,
                                'scan': 6}

    # forces and fingers
    game.PRESS_FORCE_THRESHOLD = 2.5
    game.PRESS_FORCE_KEEP_BELOW = 1.
    game.MIN_KEY_FORCE = 0.1
    game.MAX_KEY_FORCE = float(game.CONFIG['max-key-force'])
    game.VALID_FINGERS_LIST = [0,1,2,3]
    game.REST_FINGER = -1


def generate_variables(game):
        game.subj_id = game.CONFIG['subject-id']
        game.subj_dir = 'datasets/' + game.subj_id
        fu.write_all_headers(game)

        game.mode = game.CONFIG['starting-mode']
        game.presses_per_trial = game.PRESSES_PER_TRIAL[game.mode]
        game.trials_per_run = game.TRIALS_PER_RUN[game.mode]
        game.runs_per_experiment = game.RUNS_PER_EXPERIMENT[game.mode]

        game.run_trials = False
        game.debug_bool = False

        game.timers = {}
        game.trial_count = 0
        game.run_count = 0
        init_timers(game)

        # score variables
        game.execution_time_array = np.array(([]))
        game.error_array = np.array([])
        game.points_total = 0
        game.last_trial_recorded_bool = False

        # force variables
        game.force_array = game.MAX_KEY_FORCE*np.array([.25,.5,.8,.4]) # test array
        game.feedback_force_array = game.MAX_KEY_FORCE*np.array([[1,1,1,1],
                                                                 [1,1,1,1],
                                                                 [1,1,1,1],
                                                                 [1,1,1,1]]) # test array
        game.best_feedback_force_array = game.MAX_KEY_FORCE*np.array([[1,1,1,1],
                                                                      [1,1,1,1],
                                                                      [1,1,1,1],
                                                                      [1,1,1,1]]) # test array

        # game logic
        game.ready_for_press = False
        game.current_press_complete = False
        game.current_finger = -1
        game.finger_list = []
        game.show_thermometer_keyboard_bool = False

def init_timers(game):
    game.timers['rest'] = Timer(game.REST_TIME)
    game.timers['cue'] = Timer(game.CUE_TIME)
    game.timers['feedback'] = Timer(game.FEEDBACK_TIME,
                                    game.presses_per_trial)
    game.timers['press'] = Timer(sys.maxint)
    game.timers['press_limit'] = Timer(game.PRESS_TIME,
                                       game.presses_per_trial)
    if game.mode == 'scan':
        game.self_paced_bool = False 
    else:
        game.self_paced_bool = True
