import slab
import time
from freefield import main
import numpy as np
from pathlib import Path
DIR = Path(__file__).parent.resolve()  # location of the main folder

# global variables for experiment configuration:
# SPEAKERS = main.get_speaker_list(list(range(9, 25)))  # 13 speakers, 24 in the middle, 6 to each side
N_FILES = 30  # number of .wav files that contain the stimuli (per condition)
NOISE_DUR = 1.0  # duration that the background noise is played in each trial
SAMPLERATE = 48828  # sample rate that the processors run under

def priming(kind='positive', n_files=7):  # 'negative', or 'neutral
#showing emotional pictures to the participants, additionally playing the adapted priming stimulus
    
    if kind not in ('positive', 'negative', 'neutral'):
        raise ValueError('Unknown run type. Should be positive, negative, or neutral.')
    input(f'Show {kind} priming to participant!')
# randomly choose one of the 7 files to play
    file = DIR / "stimuli" / f"{np.random.randint(n_files)}.wav"

    priming_stimulus = slab.Sound.read(str(file)).channel(0)
    main.write(tag="priming", value=priming_stimulus.data, procs=["RX81", "RX82"])
    main.write(tag="playbuflen", value=priming_stimulus.nsamples, procs=["RX81", "RX82"])
    priming_speakers = SPEAKERS.iloc[::3, :]  # play the priming stimulus from every third speaker
    priming_stimulus.level -= 5*(len(priming_speakers)-1)  # reduce loudness by 5 dB for each additional speaker
    for index, speaker in priming_speakers.iterrows():  # set the speakers
        main.write(tag=f"chan{index}", value=speaker.channel, procs=speaker.analog_proc)
    main.play_and_wait()
    for index, speaker in priming_speakers.iterrows():  # "unset" the speakers again
        main.write(tag=f"chan{index}", value=99, procs=speaker.analog_proc)

"""
def block(speaker_seq, file_seq, kind='positive', noise_gain=-10):  # 'negative', or 'neutral'

    if kind not in ('positive', 'negative', 'neutral', 'noise'):
        raise ValueError('Unknown run type. Should be positive, negative, neutral, or noise.')

    # when starting the block, send a 0 to each speaker
    for speaker in  SPEAKERS.iterrows():
        main.write(tag="chan0", value=speaker.channel, procs=speaker.analog_proc)
        main.write(tag="stim", value=0, procs=speaker.analog_proc)

    if kind != "noise":  # send noise from other speakers
        noise = slab.Sound.whitenoise(duration=1.0, samplerate=48828)  # background noise
        noise.level += noise_gain
        main.write(tag="noise", value=noise.data, procs=["RX81", "RX82"])

    for trial in seq:
        print(f"trial number {speaker_seq.this_n} of {speaker_seq.n_trials}"
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

"""