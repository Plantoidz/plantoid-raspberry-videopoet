import time
import re
from lib.plantoid.speech import ignoreStderr
from simpleaichat import AIChat
from whisper_mic.whisper_mic import WhisperMic
from elevenlabs import generate, stream, set_api_key
import playsound
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI")
ELEVENLABS_API_KEY = os.environ.get("ELEVEN")

def arduino_event_listen(
    ser,
    plantony,
    network,
    trigger_line,
    max_rounds=4,
    use_arduino=True,
    interaction_mode='Default',
):

    if use_arduino:
        pattern = r"<(-?\d{1,3}),\s*(-?\d{1,3}),\s*(-?\d{1,3}),\s*(-?\d{1,3}),\s*(-?\d{1,3}),\s*(-?\d{1,3})>"

    else:
        pattern = r"button_pressed"

    try:

        while True:

            print('checking if fed...')
            plantony.check_if_fed(network)

            print('checking if button pressed...')
            if ser.in_waiting > 0:

                try:

                    line = ser.readline().decode('utf-8').strip()
                    print("line ====", line)

                    condition = bool(re.fullmatch(pattern, line))
                    print("condition", condition)

                    if condition == True:

                        # Trigger plantony interaction
                        print("Button was pressed, Invoking Plantony!")
                        plantony.trigger(
                            'Touched',
                            plantony,
                            network,
                            interaction_mode=interaction_mode,
                            max_rounds=max_rounds,
                        )

                        # Clear the buffer after reading to ensure no old "button_pressed" events are processed.
                        ser.reset_input_buffer()

                except UnicodeDecodeError:
                    
                    print("Received a line that couldn't be decoded!")

            # only check every 5 seconds
            time.sleep(5)

    except KeyboardInterrupt:
        print("Program stopped by the user.")

    finally:
        ser.close()

def invoke_plantony(plantony, network, interaction_mode='Default', max_rounds=4):

    if interaction_mode == 'Default':
        use_whisper = False

    else:
        use_whisper = True

    print('plantony initiating...')
    plantony.welcome()

    print('Iterating on Plantony n of rounds:', len(plantony.rounds), 'max rounds:', max_rounds)

    while len(plantony.rounds) < max_rounds:

        # create the round
        plantony.create_round()

        print('plantony rounds...')
        print(len(plantony.rounds))

        print('plantony listening...')
        audio = plantony.listen(use_whisper=False)

        print('plantony responding...')
        plantony.respond(audio, use_whisper=use_whisper)

    # TODO: sub function without speech
    print('plantony listening...')
    plantony.listen(use_whisper=False)

    print('plantony terminating...')
    plantony.terminate()

    # print('checking if fed...')
    # plantony.check_if_fed(network)

    # print('debug: plantony rounds...')
    # print(plantony.rounds)

    plantony.reset_rounds()
    plantony.reset_prompt()


# #ELEVENLABS
# set_api_key(ELEVENLABS_API_KEY)

# def invoke_plantony_EXP(plantony, network, max_rounds=4):

#     print('plantony initiating...')
#     plantony.welcome()

#     personality = open(os.getcwd()+"/prompt_context/glitch3.txt").read().strip()
#     ai = AIChat(system=personality, api_key=OPENAI_API_KEY, model="gpt-4-1106-preview")

# 	#WHISPER
#     with ignoreStderr():
#         mic = WhisperMic()

#     print('Iterating on Plantony n of rounds:', len(plantony.rounds), 'max rounds:', max_rounds)

#     while len(plantony.rounds) < max_rounds:

#         # create the round
#         plantony.create_round()

#         print('plantony rounds...')
#         print(len(plantony.rounds))

#         # playsound(os.getcwd()+'/media/beep_start.wav')

#         with ignoreStderr():
#             utterance = mic.listen()
#         print(f"I heard: {utterance}")

#         response = ai(utterance)
#         print(f"I said: {response}")
                
#         audio_stream = generate(
#             text=f"{response}",
#             model="eleven_multilingual_v2",
#             voice=plantony.get_voice_id(),
#             stream=True
#         )
                
#         stream(audio_stream)

