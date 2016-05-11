import pygame
from pygame.gfxdraw import aacircle
from pygame.draw import polygon
import numpy as np

def draw_filled_aacircle(screen, radius, color, xpos, ypos):
    pygame.gfxdraw.filled_circle(screen,
                                 int(xpos),
                                 int(ypos),
                                 int(radius),
                                 color)
    pygame.gfxdraw.aacircle(screen,
                            int(xpos),
                            int(ypos),
                            int(radius),
                            color)

def draw_center_rect(screen, width, height, color, xpos, ypos):
    rect = pygame.Rect(xpos-0.5*width,
                       ypos-0.5*height,
                       width,
                       height)
    pygame.draw.rect(screen, color, rect)        

def draw_bottom_rect(screen, width, height, color, xpos, ypos):
    rect = pygame.Rect(xpos-0.5*width,
                       ypos,
                       width,
                       height)
    rect.bottom = ypos
    pygame.draw.rect(screen, color, rect)        


def draw_msg(screen, text, color=(255,255,255),
             loc='center', pos=(1024/2,768/2), size=50,
             font='freesansbold.ttf'):
    font = pygame.font.Font(font, size)
    text_surf, text_rect = make_text(text, font, color)
    if loc == 'center':
        text_rect.center = pos
    elif loc == 'left':
        text_rect.center = pos
        text_rect.left = pos[0]
    elif loc == 'right':
        text_rect.center = pos
        text_rect.right = pos[0]
    screen.blit(text_surf, text_rect)

def make_text(text, font, color):
    text_surface = font.render(text, True, color)
    return text_surface, text_surface.get_rect()

def draw_info_rect(screen, text, text_color,
                   bg_color, border_color,
                   width, height, xpos, ypos,
                   padding_size=4, border_size=4):
    PADDING_SIZE = padding_size
    BORDER_SIZE = border_size
    BORDER_SIZE = PADDING_SIZE + BORDER_SIZE
    # draw border
    draw_center_rect(screen, width+BORDER_SIZE,
                     height+BORDER_SIZE, border_color,
                     xpos, ypos)
    # draw background
    draw_center_rect(screen, width+PADDING_SIZE,
                     height+PADDING_SIZE, bg_color,
                     xpos, ypos)
    # draw message
    draw_msg(screen, text, text_color,
             pos=(xpos-0.5*width+PADDING_SIZE,ypos),
             size=height, loc='left')

def draw_fixation(game, xpos, color=(255,255,255)):
    draw_msg(game.screen, '+', color=color,
         loc='center',
         pos=(xpos,
              .5*game.SCREEN_HEIGHT+game.FIXATION_OFFSET),
         size=130)

def draw_keyboard(game, mode='press'):
    # modes: rest, cue, press, feedback, debug
    for key in range(4):
        draw_center_rect(game.screen,
                         game.KEY_WIDTH,
                         game.KEY_HEIGHT,
                         game.PASSIVE_COLOR,
                         .5*game.SCREEN_WIDTH+game.KEY_XPOS*(key-1.5),
                         game.KEY_YPOS)
        if mode == 'debug' or (mode == 'press' and key == game.current_finger):
            # add logic for color
            if True:
                color = game.GOOD_CORR_COLOR
            else:
                color = game.BAD_CORR_COLOR
            draw_bottom_rect(game.screen,
                             game.KEY_WIDTH,
                             convert_key_height(game, game.force_array[key]),
                             color,
                             .5*game.SCREEN_WIDTH+game.KEY_XPOS*(key-1.5),
                             game.KEY_YPOS+0.5*game.KEY_HEIGHT)
        elif mode == 'cue' and key == game.current_finger:
            draw_center_rect(game.screen,
                             game.KEY_WIDTH,
                             game.KEY_HEIGHT,
                             game.CUE_COLOR,
                             .5*game.SCREEN_WIDTH+game.KEY_XPOS*(key-1.5),
                             game.KEY_YPOS)
        elif mode == 'feedback':
            # add logic for color
            if True:
                color = game.GOOD_CORR_COLOR
            else:
                color = game.BAD_CORR_COLOR
            draw_bottom_rect(game.screen,
                             game.KEY_WIDTH,
                             convert_key_height(game, game.feedback_force_array[key]),
                             color,
                             .5*game.SCREEN_WIDTH+game.KEY_XPOS*(key-1.5),
                             game.KEY_YPOS+0.5*game.KEY_HEIGHT)

def convert_key_height(game, force_in):
    key_ratio = force_in/game.MAX_KEY_FORCE
    clamped_ratio = min(1,key_ratio)
    return clamped_ratio*game.KEY_HEIGHT
     

def draw_cue(game):
    # draw cue on one finger
    pass


def draw_frame_rectangle(game):
    draw_center_rect(game.screen,
                     width=.5*game.KEY_WIDTH+5*game.KEY_XPOS+2*game.FRAME_RECT_BORDER_WIDTH,
                     height=game.FRAME_HEIGHT+2*game.FRAME_RECT_BORDER_WIDTH,
                     color=game.PASSIVE_COLOR,
                     xpos=.5*game.SCREEN_WIDTH,
                     ypos=.5*game.SCREEN_HEIGHT)
    draw_center_rect(game.screen,
                     width=.5*game.KEY_WIDTH+5*game.KEY_XPOS,
                     height=game.FRAME_HEIGHT,
                     color=game.BG_COLOR,
                     xpos=.5*game.SCREEN_WIDTH,
                     ypos=.5*game.SCREEN_HEIGHT)

