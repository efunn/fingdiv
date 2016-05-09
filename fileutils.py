import os, sys
import numpy as np

###################
# trial recording #
###################

def write_all_headers(game):
    if os.path.exists(game.subj_dir):
        pass
    else:
        os.mkdir(game.subj_dir)
    # game.f_frame = open(game.subj_dir
    #                     + '/frame_'
    #                     + game.subj_id
    #                     + '.txt','w')
    game.f_trial = open(game.subj_dir
                        + '/trial_'
                        + game.subj_id
                        + '.txt','w')
    # frame_header(game.f_frame)
    trial_header(game.f_trial)

# def frame_header(f):
#     f.write('{trial_number},'
#             '{trial_time},'
#             '{hrf},'
#             '{visible},'
#             '{snr},'
#             '{tr},'
#             '{nfb_score},'
#             '{cursor_pos},'
#             '{target_pos}\n'.format(trial_number='trial_number',
#                               trial_time='trial_time',
#                               hrf='hrf',
#                               visible='visible',
#                               snr='snr',
#                               tr='tr',
#                               nfb_score='nfb_score',
#                               cursor_pos='cursor_pos',
#                               target_pos='target_pos'))

# def frame_record(game, f):
#     f.write('{trial_number},'
#             '{trial_time},'
#             '{hrf},'
#             '{visible},'
#             '{snr},'
#             '{tr},'
#             '{nfb_score},'
#             '{cursor_pos},'
#             '{target_pos}\n'.format(trial_number=str(game.trial_count),
#                               trial_time=str(game.trial_clock.getTime()),
#                               hrf=str(game.target.fb_mode),
#                               visible=str(game.target_visible_trial),
#                               snr=str(game.noise_std),
#                               tr=str(game.tr),
#                               nfb_score=str(game.target.error_metric),
#                               cursor_pos=str(game.grating.ori),
#                               target_pos=str(game.target.pos)))


def trial_header(f):
    f.write('{run},'
            '{trial},'
            '{time},'
            '{correct},'
            '{sequence}\n'.format(run='run',
                              trial='trial',
                              time='time',
                              correct='correct',
                              sequence='sequence'))

def trial_record(game, f):
    f.write('{run},'
            '{trial},'
            '{time},'
            '{correct},'
            '{sequence}\n'.format(run=str(game.run_count),
                              trial=str(game.trial_count),
                              time=str(game.timers['move'].time),
                              correct=str(game.sequence_progress == game.SEQUENCE_CORRECT),
                              sequence=str(game.current_sequence).replace(',',' ')))

##########################################
# template file recording functions here #
##########################################

def sample_header(f):
    f.write('{key1},'
            '{key2},'
            '{keyn}\n'.format(key1='key1',
                              key2='key2',
                              keyn='keyn'))

def sample_record(game, f):
    f.write('{key1},'
            '{key2},'
            '{keyn}\n'.format(key1=game.val_1,
                              key2=game.val_2,
                              keyn=game.val_n))

