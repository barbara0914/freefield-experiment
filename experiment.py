import slab
import time
from freefield import main
import numpy as np
from pathlib import Path
DIR = Path(__file__).parent.resolve()  # location of the main folder

proc_list = [["RX81", "RX8", "path/play_buffer_from_channel.rcx"],
             ["RX82", "RX8", "path/play_buffer_from_channel.rcx"],
             ["RP2", "RP2", "path/button_response.rcx"]]

# for real experiment, change camera_type to "flir"
main.initialize_setup(setup="arc", proc_list=proc_list, zbus=True, connection="GB", camera_type="web")
SPEAKERS = main.get_speaker_list(list(range(9, 25)))  # 13 speakers, 24 in the middle, 6 to each side
FILES = list(range(1, 31))


def priming(kind='positive', n_files=7):  # 'negative', or 'neutral
#showing emotional pictures to the participants, additionally playing the adapted priming stimulus  
    
    if kind not in ('positive', 'negative', 'neutral'):
        raise ValueError('Unknown run type. Should be positive, negative, or neutral.')
    input(f'Show {kind} priming to participant!')
    # randomly choose one of the 7 files to play
    file = DIR / "stimuli" / f"{np.random.randint(n_files)}.wav"
    if not file.is_file():
        raise ValueError(f'File {file} does not exist. Aborting...')
    priming_stimulus = slab.Sound.read(str(file)).channel(0)
    main.write(tag="priming", value=priming_stimulus.data, procs=["RX81", "RX82"])
    main.write(tag="playbuflen", value=priming_stimulus.nsamples, procs=["RX81", "RX82"])
    priming_speakers = SPEAKERS.iloc[::3, :]  # play the priming stimulus from every third speaker
    priming_speakers.level -= 5*(len(priming_speakers)-1)  # reduce loudness by 5 dB for each additional speaker
    for index, speaker in priming_speakers.iterrows():  # set the speakers
        main.write(tag=f"chan{index}", value=speaker.channel, procs=speaker.analog_proc)
    main.play_and_wait()
    for index, speaker in priming_speakers.iterrows():  # "unset" the speakers again
        main.write(tag=f"chan{index}", value=99, procs=speaker.analog_proc)


def block(SPEAKERS, FILES, kind='positive', stimlevel=90, noiselevel=80):  # 'negative', or 'neutral'

    if kind not in ('positive', 'negative', 'neutral', 'noise'):
        raise ValueError('Unknown run type. Should be positive, negative, neutral, or noise.')
    if kind != "noise":  # send noise from other speakers
    file = DIR / "stimuli" / f"{np.random.randint(n_files)}.wav"
    
    
    
 """   
    for speaker in _speakers:
        setup.set_variable("stim", 0, "RX81")
        setup.set_variable("chan0", speaker, "RX81")

    
    response = []
    noise = slab.Sound.whitenoise(duration=1.0, samplerate=48828)  # background noise
    noise.level = noiselevel
    
        setup.set_variable("noise", noise.data, "RX81")
    while speaker_seq.n_remaining > 0:
        speaker = speaker_seq.__next__()
        file = file_seq.__next__()
        print("trial number %s of %s" % (str(speaker_seq.this_n), speaker_seq.n_trials))
        stim = slab.Sound.read(LOC_FOLDER/kind/(str(file)+".wav"))  # read random wav
        stim.level = stimlevel
     
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
"""
