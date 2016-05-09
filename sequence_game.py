import pygame
import sys
import numpy as np
import game_init as gi
import game_run as gr
import game_graphics as gg
import fileutils as fu
from timer import Timer
try: 
    from pydaq import Pydaq
    SENSOR_ACTIVE = True
except:
    SENSOR_ACTIVE = False

class SequenceGame(object):

    def __init__(self):
        gi.generate_constants(self)        
        gi.generate_variables(self)        
        pygame.init()
        pygame.mouse.set_visible(not pygame.mouse.set_visible)
        self.clock = pygame.time.Clock()
        if SENSOR_ACTIVE:
            self.daq = Pydaq('Dev3/ai0:1', 60,
                             lp_filt_freq=14,
                             lp_filt_order=3,
                             force_params='force_params.txt')
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
                elif event.key == pygame.K_m:
                    if self.input_mode == 'keyboard':
                        self.input_mode = 'sensor'
                    elif self.input_mode == 'sensor':
                        self.input_mode = 'keyboard'
                elif event.key == pygame.K_n:
                    self.show_keyboard = not(self.show_keyboard)
                elif ((event.key == pygame.K_SPACE
                       or event.key == pygame.K_5)
                      and not(self.run_trials)):
                    self.run_trials = True
                    gr.reset_for_next_run(game)
                elif event.key == pygame.K_p:
                    self.run_trials = False
                elif event.key == pygame.K_d:
                    self.debug_bool = not(self.debug_bool)
                elif event.key == pygame.K_LEFT:
                    self.set_run('debug')
                elif event.key == pygame.K_RIGHT:
                    self.set_run('test')
                elif event.key == pygame.K_UP:
                    self.set_run('train')
                elif event.key == pygame.K_DOWN:
                    self.set_run('scan')
                if self.input_mode == 'keyboard':
                    if event.key == self.key_codes[0]: self.keydown[0] = True
                    elif event.key == self.key_codes[1]: self.keydown[1] = True
                    elif event.key == self.key_codes[2]: self.keydown[2] = True
                    elif event.key == self.key_codes[3]: self.keydown[3] = True
                    elif event.key == self.key_codes[4]: self.keydown[4] = True
            elif event.type == pygame.KEYUP:
                if self.input_mode == 'keyboard':
                    if event.key == self.key_codes[0]: self.keydown[0] = False
                    elif event.key == self.key_codes[1]: self.keydown[1] = False
                    elif event.key == self.key_codes[2]: self.keydown[2] = False
                    elif event.key == self.key_codes[3]: self.keydown[3] = False
                    elif event.key == self.key_codes[4]: self.keydown[4] = False
        if self.input_mode == 'sensor':
            # add sensor logic here
            # - keypress recognized if force > 2.5N in one finger 
            #   and less than 2.2N in rest of fingers
            pass

    def check_key_status(self):
        if self.keydown.count(True) == 0:
            self.current_key = 'none'
        elif self.keydown.count(True) == 1:
            self.current_key = self.keydown.index(True)+1

    def set_run(self, mode):
        self.run_count = 0
        self.mode = mode
        self.sequences_per_trial = self.SEQUENCES_PER_TRIAL[mode]
        self.trials_per_run = self.TRIALS_PER_RUN[mode]
        self.runs_per_experiment = self.RUNS_PER_EXPERIMENT[mode]
        self.timers['score'] = Timer(self.FEEDBACK_TIME,
                                     self.sequences_per_trial)
        if self.mode == 'scan':
            self.self_paced_bool = False 
        else:
            self.self_paced_bool = True 
        if game.mode == 'debug' or game.mode == 'train':
            game.sequence_set = game.TRAIN_SEQUENCES
        elif game.mode == 'test' or game.mode == 'scan':
            game.sequence_set = game.TEST_SEQUENCES

    def set_sequences(self):
        if self.mode == 'scan':
            self.sequence_list = []
            temp_sequence_set = game.sequence_set
            for block in range(4):
                np.random.shuffle(temp_sequence_set)
                for sequence in temp_sequence_set:
                    self.sequence_list.append(sequence)
        elif self.mode == 'test':
            self.sequence_list = self.sequence_set[:-1]
            np.random.shuffle(game.sequence_list)
        else:
            self.sequence_list = self.sequence_set
            np.random.shuffle(game.sequence_list)

    def run(self):
        while True:
            ###################
            # FEATURES TO ADD #
            ###################
            # 1. interspersed rest blocks (add 'rest' sequence)
            # 2. frame-by-frame recording
            # 3. trial-by-trial recording for rest blocks
            # 4. fix timing resets to add remainder times (1-2 frames)
            time_passed = self.clock.tick_busy_loop(self.FRAME_RATE)
            self.check_input()
            self.check_key_status()
            self.draw_background()
            if self.show_keyboard:
                gg.draw_keyboard(self)
            if self.run_trials:
                gg.draw_frame_rectangle(self)
                if not(self.timers['cue'].time_limit_hit):
                    self.timers['cue'].update(time_passed)
                    gr.run_sequence_cue(self)
                elif not(self.current_sequence_complete):
                    self.timers['move'].update(time_passed)
                    if not(self.self_paced_bool):
                        self.timers['move_limit'].update(time_passed)
                        if self.timers['move_limit'].time_limit_hit:
                            self.current_sequence_complete = True
                    gr.run_sequence_move(self)
                elif (not(self.self_paced_bool)
                          and not(self.timers['move_limit'].time_limit_hit)):
                    self.timers['move_limit'].update(time_passed)
                    gg.draw_sequence_progress(self)
                elif not(self.timers['score'].time_limit_hit):
                    self.timers['score'].update(time_passed)
                    if game.current_sequence == game.REST_SEQUENCE:
                        gr.run_sequence_score_rest(self)
                    else:
                        gr.run_sequence_score(self)
                elif not(self.timers['score'].count_limit_hit):
                    gr.reset_for_next_sequence_execution(self)
                elif self.trial_count < self.trials_per_run:
                    gr.reset_for_next_sequence_trial(self)
                else:
                    self.run_trials = False
            else:
                self.draw_splash()
            if self.debug_bool:
                self.draw_debug(time_passed)
            pygame.display.flip()

    def draw_background(self):
        self.screen.fill(self.BG_COLOR)

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
        if game.run_count > 0:
            points_msg = ('Points this run: ' + str(game.points_total))
            time_msg = ('Average movement time: ' + str(round(np.mean(
                            game.execution_time_array)/1000.,2)) + ' seconds')
            error_rate = np.mean(game.error_array)
            error_msg = ('Percent errors: ' + str(round(100*error_rate,1)) + '%')
            if game.run_count < game.runs_per_experiment:
                if error_rate > game.ERROR_CUTOFF:
                    advice_msg = 'For the next run, try slowing down.'
                else:
                    advice_msg = 'For the next run, try going faster.'
            else:
                advice_msg = ''
            if game.mode != 'scan':
                gg.draw_msg(self.screen, points_msg,
                            loc='center', pos=(.5*self.SCREEN_WIDTH,
                                               .6*self.SCREEN_HEIGHT), size=35)
                gg.draw_msg(self.screen, time_msg,
                            loc='center', pos=(.5*self.SCREEN_WIDTH,
                                               .7*self.SCREEN_HEIGHT), size=35)
                gg.draw_msg(self.screen, error_msg,
                            loc='center', pos=(.5*self.SCREEN_WIDTH,
                                               .8*self.SCREEN_HEIGHT), size=35)
                gg.draw_msg(self.screen, advice_msg,
                            loc='center', pos=(.5*self.SCREEN_WIDTH,
                                               .9*self.SCREEN_HEIGHT), size=35)

    def draw_debug(self, time_passed):
        fr = 1000/float(time_passed)
        fr_msg = 'frame rate: ' + str(fr)
        gg.draw_msg(self.screen, fr_msg,
                    loc='left', pos=(10,33), size=28)
        force = self.daq.get_force()
        volt_msg_1 = 'out_volt_1: ' + str(force[0])
        volt_msg_2 = 'out_volt_2: ' + str(force[1])
        gg.draw_msg(self.screen, volt_msg_1,
                    loc='left', pos=(10,66), size=28)
        gg.draw_msg(self.screen, volt_msg_2,
                    loc='left', pos=(10,99), size=28)

    def quit(self):
        sys.exit()

if __name__ == "__main__":
    game = SequenceGame()
    game.run()
