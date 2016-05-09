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
            elif event.type == pygame.KEYUP:
                pass
        if SENSOR_ACTIVE:
            self.check_keys()

    def check_keys(self):
        self.force_array[:] = self.daq.get_force()

    def run(self):
        while True:
            time_passed = self.clock.tick_busy_loop(self.FRAME_RATE)
            self.check_input()
            self.draw_background()
            gg.draw_keyboard(self)
            pygame.display.flip()


    def draw_background(self):
        self.screen.fill(self.BG_COLOR)

    def quit(self):
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
