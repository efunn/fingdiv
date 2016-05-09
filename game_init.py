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
    game.KEY_HEIGHT = 0.3*game.SCREEN_HEIGHT
    game.FRAME_HEIGHT = 0.2*game.SCREEN_HEIGHT
    game.KEY_WIDTH = 0.1*game.SCREEN_WIDTH
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
    game.GOOD_CORR_COLOR = 60,120,60
    game.BAD_CORR_COLOR = 120,60,60
    game.PASSIVE_COLOR = 70,70,70
    game.FIXATION_COLOR = 255,255,255

    # time
    game.CUE_TIME = 0.5
    game.PRESS_TIME = 6.
    game.PRE_FEEDBACK_TIME = 0.5
    game.FEEDBACK_TIME = 2.
    game.TRIAL_TIME = 10.

    # trials and runs
    game.TRIALS_PER_RUN = {'debug': 2,
                           'test': 4,
                           'train': 4,
                           'scan': 20}
    game.RUNS_PER_EXPERIMENT = {'debug': 2,
                                'test': 9,
                                'train': 24,
                                'scan': 6}

    # forces
    game.MAX_KEY_FORCE = 7.


def generate_variables(game):
        game.subj_id = game.CONFIG['subject-id']
        game.subj_dir = 'datasets/' + game.subj_id
        fu.write_all_headers(game)

        game.mode = game.CONFIG['starting-mode']
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
        game.force_array = np.array([3.5,14.,1.,6.5]) # test array

def init_timers(game):
    game.timers['cue'] = Timer(game.CUE_TIME)
    game.timers['trial'] = Timer(game.TRIAL_TIME,
                                 game.trials_per_run)
    game.timers['feedback'] = Timer(game.FEEDBACK_TIME)
