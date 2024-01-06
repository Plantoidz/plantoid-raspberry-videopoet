import subprocess
import sys

def convert_to_surround_ffmpeg(input_file, output_file, channels=6):
    """
    Convert an audio file to a 5.1 channel WAV format using ffmpeg.
    """
    ffmpeg_command = [
        "ffmpeg", 
        "-i", input_file, 
        "-ac", str(channels),
        "-filter_complex", "pan=5.1|FL=FL|FR=FR|FC=FC|LFE=FC|BL=FL|BR=FR",
        output_file
    ]
    subprocess.run(ffmpeg_command, check=True)

def play_test_sound(audio_device, audio_file):
    """
    Play an audio file using mpv on the specified audio device.
    """
    try:
        mpv_command = ["mpv", "--audio-device=" + audio_device, audio_file]
        subprocess.run(mpv_command)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 test_audio.py <audio_device> <input_file>")
        sys.exit(1)

    audio_device = sys.argv[1]
    input_file = sys.argv[2]
    output_file = "converted_surround.wav"

    # Convert the file to a 5.1 channel format using ffmpeg
    convert_to_surround_ffmpeg(input_file, output_file)

    # Play the converted file
    play_test_sound(audio_device, output_file)
