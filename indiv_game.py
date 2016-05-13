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
                elif event.key == pygame.K_q:
                    if not(SENSOR_ACTIVE):
                        self.force_array[0] = self.PRESS_FORCE_THRESHOLD
                elif event.key == pygame.K_w:
                    if not(SENSOR_ACTIVE):
                        self.force_array[1] = self.PRESS_FORCE_THRESHOLD
                elif event.key == pygame.K_e:
                    if not(SENSOR_ACTIVE):
                        self.force_array[2] = self.PRESS_FORCE_THRESHOLD
                elif event.key == pygame.K_r:
                    if not(SENSOR_ACTIVE):
                        self.force_array[3] = self.PRESS_FORCE_THRESHOLD
                elif event.key == pygame.K_LEFT:
                    self.set_run('debug')
                elif event.key == pygame.K_RIGHT:
                    self.set_run('test')
                elif event.key == pygame.K_UP:
                    self.set_run('train')
                elif event.key == pygame.K_DOWN:
                    self.set_run('scan')
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_q:
                    if not(SENSOR_ACTIVE):
                        self.force_array[0] = self.MIN_KEY_FORCE
                elif event.key == pygame.K_w:
                    if not(SENSOR_ACTIVE):
                        self.force_array[1] = self.MIN_KEY_FORCE
                elif event.key == pygame.K_e:
                    if not(SENSOR_ACTIVE):
                        self.force_array[2] = self.MIN_KEY_FORCE
                elif event.key == pygame.K_r:
                    if not(SENSOR_ACTIVE):
                        self.force_array[3] = self.MIN_KEY_FORCE
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

    def run(self):
        while True:
            time_passed = self.clock.tick_busy_loop(self.FRAME_RATE)
            self.check_input()
            self.draw_background()
            # gg.draw_keyboard(game, 'debug')
            if self.run_trials:
                if not(self.timers['rest'].time_limit_hit):
                    self.timers['rest'].update(time_passed)
                    gr.run_rest(self)
                elif not(self.timers['cue'].time_limit_hit):
                    self.timers['cue'].update(time_passed)
                    gr.run_cue(self)
                elif not(self.current_press_complete):
                    if not(self.ready_for_press):
                        gr.run_rest(self)
                        if (self.force_array[self.current_finger]
                                < self.PRESS_FORCE_KEEP_BELOW):
                            self.ready_for_press = True
                    else:
                        self.timers['press_limit'].update(time_passed)
                        gr.run_press(self)
                elif self.mode == 'test':
                    if not(self.timers['press_limit'].time_limit_hit):
                        self.timers['press_limit'].update(time_passed)
                        gr.run_rest(self)
                    elif not(self.timers['press_limit'].count_limit_hit):
                        gr.reset_for_next_press(self)
                    elif self.trial_count < self.trials_per_run:
                        gr.reset_for_next_trial(self)
                    else:
                        self.run_trials = False
                elif self.mode == 'train':
                    if not(self.timers['feedback'].time_limit_hit):
                        self.timers['feedback'].update(time_passed)
                        gr.run_feedback(self)
                    elif not(self.timers['feedback'].count_limit_hit):
                        gr.reset_for_next_press(self)
                    elif self.trial_count < self.trials_per_run:
                        gr.reset_for_next_trial(self)
                    else:
                        self.run_trials = False
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
