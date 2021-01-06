import slab
import time
from freefield import main
import numpy as np
from pathlib import Path

proc_list = [["RX81", "RX8", "path/play_buffer_from_channel.rcx"],
             ["RX82", "RX8", "path/play_buffer_from_channel.rcx"],
             ["RP2", "RP2", "path/button_response.rcx"]]

# Initialize
setup.set_speaker_config("arc")
camera.init(type="freefield")

# Define relevant variables for setup.localization_test()
SPEAKERS = main.get_speaker_list(list(range(9, 25)))  # 13 speakers, 24 in the middle, 6 to each side
sound = slab.Sound.whitenoise(duration=1.0, samplerate=48828)


def make_dir(expdir):
    try:
        os.makedirs(expdir)
    except OSError:
        print("Creation of the directory %s failed" % expdir)
    else:
        print("Successfully created the directory %s" % expdir)


def localize_sound():
    response = setup.localization_test(sound, speakers, n_reps=3)
    path = "C:/Projects/EEG_Elevation_Max/data/"+subject + \
        "/"+"localization_test_responses/result"
    with open(path, 'w') as f:
        for item in response:
            f.write("%s\n" % item)
    print("Saved responses as %s!" % path)


if __name__ == "__main__":

    subject = "Barbara"  # name der testperson
    expdir = "C:/Projects/EEG_Elevation_Max/data/"+subject + \
        "/"+"localization_test_responses"  # speicherort
    make_dir(expdir)
    coords = camera.calibrate_camera(n_reps=3)  # calibrate camera
    response = localize_sound()
