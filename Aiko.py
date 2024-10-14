import AnyAI.AikoGUIBackend
from AnyAI.Aiko import sysprompt
from AnyAI      import AI

from firstrun import init as frun_init

from webbrowser import open_new_tab
from argparse   import ArgumentParser
from warnings   import warn
from os.path    import exists
from pickle     import load, dump
from json       import load as load_json
from time       import sleep
from sys        import argv
from AnyAI.AikoState  import aiko_state

arg_parser = ArgumentParser(description = 'Launch Aiko!')
arg_parser.add_argument('filename')
arg_parser.add_argument('--testmode', action = 'store_true', help = 'Launch in testmode')
args = arg_parser.parse_args(argv)

if args.testmode:
    warn('Aiko is running in testmode!')

PATHS, is_first_run = frun_init()

with open(PATHS['userinfo'], 'rb') as file:
    userinfo = load_json(file) # type: dict[str, str]

AnyAI.AikoGUIBackend.run()

if is_first_run:
    sleep(2)
    open_new_tab(f'http://localhost:5050/WelcomeToAikoProject')
    while aiko_state.agreement_mutex.locked():
        sleep(1)

class Aiko(AI):

    def __init__(self, model: str) -> None:
        super().__init__(model, sysprompt(**userinfo))

if exists(PATHS['aikoinstance']):
    with open(PATHS['aikoinstance'], 'rb') as file:
        aiko = load(file)
else:
    aiko = Aiko('command-r+')
    with open(PATHS['aikoinstance'], 'wb') as file:
        dump(aiko, file)

while True:
    if aiko_state.chat_queue:
        aiko.ctx.messages[0].content = sysprompt(**userinfo)
        aiko_state.last_response = aiko.prompt(aiko_state.chat_queue[0])
        with open(PATHS['aikoinstance'], 'wb') as file:
            dump(aiko, file)
        aiko_state.chat_queue.pop(0)
        aiko_state.is_thinking = False
        print('Sent awake status on backend')
    else:
        sleep(1)