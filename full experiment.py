import slab
import time
import freefield
from freefield import main
import numpy as np
from pathlib import Path
import sys
sys.path.append("C:/Projects/soundtools")
sys.path.append("C:/Projects/freefield_toolbox/freefield")
sys.path.append("C:/Projects/Emotion_Loc/Experiment_2/py/")

EXPDIR = Path('C:\\Projects\\Emotion_Loc\\Experiment_2')
STIM_FOLDER = EXPDIR / Path('stimuli')
PRIMING_FOLDER = STIM_FOLDER / Path('priming')
LOC_FOLDER = STIM_FOLDER / Path('localization')
RCO_FOLDER = EXPDIR / Path('rcx')

# 13 speakers, 24 in the middle, 6 to each side, there is no speaker 0
_speakers = list(range(9, 25))
_files = list(range(1, 31))
rx81_path = str(RCO_FOLDER / Path("play_buffer_from_channel.rcx"))
rp2_path = str(RCO_FOLDER / Path("button_response.rcx"))

# _files = list(range(1, 31))  neutral
# _files = list(range(1, 36)) negative
# _files = list(range(1, 42)) positive

setup.set_speaker_config("arc")
setup.initialize_devices(ZBus=True, cam=True, RX8_file=rx81_path, RP2_file=rp2_path)

# TODO: vortest für noise level
# TODO: Reaktionszeit?
# TODO: LEDs auch an meine LAutsprecher?


def priming(kind='positive'):  # 'negative', or 'neutral'
    if kind not in ('positive', 'negative', 'neutral'):
        raise ValueError('Unknown run type. Should be positive, negative, or neutral.')
    input(f'Show {kind} priming to participant!')
    infolder = PRIMING_FOLDER / Path(kind)
    # randomly choose one of the 7 files to play
    n = np.random.randint(1, 8)
    file = infolder / Path(str(n) + '.wav')
    if not file.is_file():
        raise ValueError(f'File {file} does not exist. Aborting...')
    stim = slab.Sound.read(str(file))
    stim = stim.channel(0)
    stim.level = 80
    setup.set_variable("priming", stim.data, "RX81")
    setup.set_variable("playbuflen", stim.nsamples, "RX81")
    for i, j in zip(range(9, 25, 3), range(6)):  # i = channel nr, j= rco-tag nr
        setup.set_variable(variable="chan"+str(j), value=i, proc="RX81")
        setup.trigger("zBusB")
        setup.wait_to_finish_playing()
    # for j in range(6):  # set all channels back to 25
        setup.set_variable(variable="chan"+str(j), value=25, proc="RX81")


def block(speaker_seq, file_seq, kind='positive', stimlevel=90, noiselevel=80):  # 'negative', or 'neutral'

    # when starting the block, send a 0 to each speaker
    for speaker in _speakers:
        setup.set_variable("stim", 0, "RX81")
        setup.set_variable("chan0", speaker, "RX81")

    if kind not in ('positive', 'negative', 'neutral', 'noise'):
        raise ValueError('Unknown run type. Should be positive, negative, neutral, or noise.')
    response = []
    noise = slab.Sound.whitenoise(duration=1.0, samplerate=48828)  # background noise
    noise.level = noiselevel
    if kind != "noise":  # send noise from other speakers
        setup.set_variable("noise", noise.data, "RX81")
    while speaker_seq.n_remaining > 0:
        speaker = speaker_seq.__next__()
        file = file_seq.__next__()
        print("trial number %s of %s" % (str(speaker_seq.this_n), speaker_seq.n_trials))
        stim = slab.Sound.read(LOC_FOLDER/kind/(str(file)+".wav"))  # read random wav
        stim.level = stimlevel
        stim = stim.channel(0)  # not needed as soon as mono sound files are used
        setup.set_variable("playbuflen", stim.nsamples, "RX81")
        setup.set_variable("stim", stim.data, "RX81")
        setup.set_variable("chan0", speaker, "RX81")
        if kind != "noise":  # send noise from 5 evenly spaced speakers
            noise_speakers = _speakers.copy()
            noise_speakers.remove(speaker)
            for speaker, chan in zip(noise_speakers[::3], range(1, 6)):
                setup.set_variable("chan"+str(chan), speaker, "RX81")
        while not setup.get_variable("response", proc="RP2"):
            time.sleep(0.01)  # wait for trial start
        ele, azi = camera.get_headpose(convert=True, average=True, n_images=5, resolution=0.5)
        # if np.abs(y) < 25:
        #    print("wrong pose!")
        #    setup.trigger(trig=1, proc="RX81")
        #    pass
        else:  # head position is correct --> start trial
            setup.trigger()
            setup.wait_to_finish_playing()
            while not setup.get_variable("response", proc="RP2"):
                time.sleep(0.01)  # wait for response to stimulus
            ele, azi = setup.get_headpose()
            response.append([y])

    return response


def run_experiment(subject, repeat_files=2, repeat_conditions=2):

    out_folder = EXPDIR/Path(subject)
    # experiment
    setup.set_speaker_config("arc")
    setup.initialize_devices(RX81_file=rx81_path, RP2_file=rp2_path, ZBus=True, cam=True)
    conditions = slab.Trialsequence(conditions=["positive", "negative", "neutral"],
                                    n_reps=repeat_conditions, kind='non_repeating')
    # conditions.insert(0, "noise") ??
    conditions.save_json(out_folder/"conditions.npy")

    while conditions.n_remaining > 0:
        condition = conditions.__next__()
        if condition != "noise":
            priming(condition)  # show priming
        input("press enter to start block")
        # one list?
        file_seq = slab.Trialsequence(
            conditions=_files, n_reps=repeat_files, kind='non_repeating')
        speaker_seq = slab.Trialsequence(
            conditions=_speakers, n_reps=repeat_files*3, kind='non_repeating')
        if speaker_seq.n_trials != file_seq.n_trials:
            raise ValueError("File and speaker sequence must be of same length!")
        file_seq.save_json(out_folder/("file_seq_"+condition+str(conditions.this_n)+".npy"))
        speaker_seq.save_json(out_folder/("speaker_seq_"+condition+str(conditions.this_n)+".npy"))

        response = block(kind=condition, speaker_seq=speaker_seq, file_seq=file_seq)
        np.savetxt(out_folder/("response_"+condition+str(conditions.this_n)+".npy"), response)
