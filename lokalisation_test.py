from freefield import camera, setup
import slab
import os
import sys
sys.path.append("C:/Projects/freefield_toolbox")
sys.path.append("C:/Projects/soundtools")
_location = setup._location


# Initialize
setup.set_speaker_config("dome")
camera.init(type="freefield")

# Define relevant variables for setup.localization_test()
speakers = [(0, 37.5), (0, 12.5), (0, -12.5), (0, -37.5)]
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
