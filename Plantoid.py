import time
import os
import re
import lib.plantoid.serial_utils as serial_utils
import lib.plantoid.web3_utils as web3_utils
from plantoids.plantoid import Plantony
from utils.util import load_config, str_to_bool
from dotenv import load_dotenv
from lib.plantoid.event_loops import invoke_plantony, invoke_plantony_EXP, arduino_event_listen

def main():

    # load config
    config = load_config(os.getcwd()+'/configuration.toml')

    cfg = config['general']

    use_blockchain = str_to_bool(cfg['ENABLE_BLOCKCHAIN'])
    use_arduino = str_to_bool(cfg['ENABLE_ARDUINO'])
    max_rounds = cfg['max_rounds']
    trigger_line = cfg['TRIGGER_LINE']
    eleven_voice_id = cfg['ELEVEN_VOICE_ID']

    web3_config = {
        'use_goerli': str_to_bool(cfg['USE_GOERLI']),
        'use_mainnet': str_to_bool(cfg['USE_MAINNET']),
        'use_goerli_address': cfg['USE_GOERLI_ADDRESS'],
        'use_mainnet_address': cfg['USE_MAINNET_ADDRESS'],
        'use_metadata_address': cfg['USE_METADATA_ADDRESS'],
        'goerli_failsafe': cfg['GOERLI_FAILSAFE'],
        'mainnet_failsafe': cfg['MAINNET_FAILSAFE'],
    }

    # get output port from ENV
    PORT = os.environ.get('SERIAL_PORT_OUTPUT')

    # setup serial
    ser = serial_utils.setup_serial(PORT=PORT)

    # setup signals
    if use_arduino:
        serial_utils.wait_for_arduino(ser)
        serial_utils.send_to_arduino(ser, "awake")  

    # setup web3
    goerli, mainnet = web3_utils.setup_web3_provider(web3_config)

    # process previous tx
    if mainnet is not None: web3_utils.process_previous_tx(mainnet)
    if goerli is not None: web3_utils.process_previous_tx(goerli)

    # instantiate plantony with serial
    plantony = Plantony(ser, eleven_voice_id)

    # setup plantony
    plantony.setup()

    # add listener
    plantony.add_listener('Touched', invoke_plantony)
    plantony.add_listener('Touched_EXP', invoke_plantony_EXP)
    
    # use interaction mode
    use_mode = 'Touched_EXP'

    # check for keyboard press
    arduino_event_listen(
        ser,
        plantony,
        goerli,
        trigger_line,
        max_rounds=max_rounds,
        use_arduino=use_arduino,
        use_mode=use_mode,
    )
    # serial_listen.listen_for_keyboard_press(ser)

if __name__ == "__main__":

    # Execute main function
    main()
