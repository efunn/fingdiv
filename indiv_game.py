import pygame
import sys
import numpy as np

import game_init as gi
import game_run as gr
import game_graphics as gg
from timer import Timer
try: 
    from pydaq import Pydaq
    SENSOR_ACTIVE = True
except:
    SENSOR_ACTIVE = False


class Game(object):

    def __init__(self):
        gi.generate_constants(self)        
        gi.generate_variables(self)        
        pygame.init()
        pygame.mouse.set_visible(not pygame.mouse.set_visible)
        self.clock = pygame.time.Clock()
        if SENSOR_ACTIVE:
            self.daq = Pydaq(self.DEVICE_NAME,
                             self.FRAME_RATE,
                             self.LP_FILT_FREQ,
                             self.LP_FILT_ORDER,
                             self.FORCE_PARAMS)
        if self.CONFIG['fullscreen']:
            self.screen = pygame.display.set_mode(
                            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
                             pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(
                            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))


    def check_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: self.quit()
                elif ((event.key == pygame.K_SPACE
                       or event.key == pygame.K_5)
                      and not(self.run_trials)):
                    self.run_trials = True
                    gr.reset_for_next_run(game)
                elif event.key == pygame.K_p:
                    self.run_trials = False
                elif event.key == pygame.K_LEFT:
                    self.set_run('debug')
                elif event.key == pygame.K_RIGHT:
                    self.set_run('test')
                elif event.key == pygame.K_UP:
                    self.set_run('train')
                elif event.key == pygame.K_DOWN:
                    self.set_run('scan')
            elif event.type == pygame.KEYUP:
                pass
        if SENSOR_ACTIVE:
            self.check_keys()

    def check_keys(self):
        self.force_array[:] = self.daq.get_force()

    def set_run(self, mode):
        self.run_count = 0
        self.mode = mode
        self.trials_per_run = self.TRIALS_PER_RUN[mode]
        self.runs_per_experiment = self.RUNS_PER_EXPERIMENT[mode]
        gi.init_timers(self)

    def set_fingers(self):
        game.finger_list = []
        for block in range(game.trials_per_run/len(game.VALID_FINGERS_LIST)):
            np.random.shuffle(game.VALID_FINGERS_LIST)
            game.finger_list += game.VALID_FINGERS_LIST

    def draw_splash(self):
        if game.run_count < game.runs_per_experiment:
            splash_msg = ('Ready for Run ' + str(game.run_count+1)
                          + ' of ' + str(game.runs_per_experiment))
        else:
            splash_msg = ('Done!')
        gg.draw_msg(self.screen, splash_msg,
                    loc='center', pos=(.5*self.SCREEN_WIDTH,
                                       .5*self.SCREEN_HEIGHT), size=50)
        gg.draw_msg(self.screen, ('mode: ' + game.mode),
                    loc='right', pos=(.975*self.SCREEN_WIDTH,
                                      .05*self.SCREEN_HEIGHT), size=24)
        # can add scoring message here
        # if game.run_count > 0:
        #     points_msg = ('Points this run: ' + str(game.points_total))
        #     gg.draw_msg(self.screen, points_msg,
        #                 loc='center', pos=(.5*self.SCREEN_WIDTH,
        #                                    .6*self.SCREEN_HEIGHT), size=35)

    # def run(self):
    #     while True:
    #         time_passed = self.clock.tick_busy_loop(self.FRAME_RATE)
    #         self.check_input()
    #         self.draw_background()
    #         gg.draw_keyboard(self)
    #         pygame.display.flip()

    def run(self):
        while True:
            time_passed = self.clock.tick_busy_loop(self.FRAME_RATE)
            self.check_input()
            self.draw_background()
            if self.run_trials:
                self.timers['trial'].update(time_passed)
                if self.timers['trial'].time < 1000*game.TRIAL_START_REST:
                    gr.run_rest(self)
                elif (self.timers['trial'].time
                        < 1000*(game.TRIAL_START_REST+game.CUE_TIME)):
                    gr.run_cue(self)
                elif (self.timers['trial'].time
                        < 1000*(game.TRIAL_START_REST+game.CUE_TIME
                                +game.PRESS_TIME)):
                    gr.run_press(self)
                elif (self.timers['trial'].time
                        < 1000*(game.TRIAL_START_REST+game.CUE_TIME
                                +game.PRESS_TIME+game.PRE_FEEDBACK_TIME)):
                    gr.run_rest(self)
                elif ((game.mode == 'train' or game.mode == 'scan') and
                        (self.timers['trial'].time
                            < 1000*(game.TRIAL_START_REST+game.CUE_TIME
                            +game.PRESS_TIME+game.PRE_FEEDBACK_TIME+game.FEEDBACK_TIME))):
                    gr.run_feedback(self)
                elif not(self.timers['trial'].time_limit_hit):
                    gr.run_rest(self)
                elif self.trial_count < self.trials_per_run:
                    gr.reset_for_next_trial(self)
                else:
                    self.run_trials = False
                # add timing logic
                # if not(self.timers['cue'].time_limit_hit):
                #     self.timers['cue'].update(time_passed)
                #     gr.run_sequence_cue(self)
                # elif not(self.current_sequence_complete):
                #     self.timers['move'].update(time_passed)
                #     if not(self.self_paced_bool):
                #         self.timers['move_limit'].update(time_passed)
                #         if self.timers['move_limit'].time_limit_hit:
                #             self.current_sequence_complete = True
                #     gr.run_sequence_move(self)
                # elif (not(self.self_paced_bool)
                #           and not(self.timers['move_limit'].time_limit_hit)):
                #     self.timers['move_limit'].update(time_passed)
                #     gg.draw_sequence_progress(self)
                # elif not(self.timers['score'].time_limit_hit):
                #     self.timers['score'].update(time_passed)
                #     if game.current_sequence == game.REST_SEQUENCE:
                #         gr.run_sequence_score_rest(self)
                #     else:
                #         gr.run_sequence_score(self)
                # elif not(self.timers['score'].count_limit_hit):
                #     gr.reset_for_next_sequence_execution(self)
                # elif self.trial_count < self.trials_per_run:
                #     gr.reset_for_next_sequence_trial(self)
                # else:
                #     self.run_trials = False
            else:
                self.draw_splash()
            pygame.display.flip()


    def draw_background(self):
        self.screen.fill(self.BG_COLOR)

    def quit(self):
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
