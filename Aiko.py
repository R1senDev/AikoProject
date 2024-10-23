'''
Aiko Project

Author: Pavel Ovchinnikov (R1senDev)
'''


# Importing important stuff from Core
print('Importing Core modules...', end = ' ')
from Core.UpdateChecker import UpdateChecker
from Core.SetupWizard   import init_aiko
from Core.SteamBridge   import SteamLibrary, SteamLaunchError
from Core.Localizer     import set_locale, locstr
from Core.Weather       import WeatherProvider, signify
from Core.Shizune       import Shizune
from Core.AikoSan       import *
from Core.Palette       import *
from Core.Lilly         import Lilly
from Core.AI            import AI, Role, Message
print('Done')

# Importing other stuff for basic Aiko functioning
from webbrowser import open_new_tab
from argparse   import ArgumentParser
from datetime   import datetime
from pickle     import load, dump
from json       import load as load_json
from math       import floor
from time       import time
from sys        import argv, getsizeof
from os         import system


# First things first
init_aiko()


# Setting up ArgumentParser
argp = ArgumentParser(description = 'AikoProject')
argp.add_argument('filename')
argp.add_argument('-v', '--verbose', action = 'store_true', help = 'Enable verbose mode')
argp.add_argument('--no-shizune',    action = 'store_true', help = 'Run without Shizune')
argp.add_argument('--no-lilly',      action = 'store_true', help = 'Run without Lilly')
args = argp.parse_args(argv)


# Reading preferences
with open('config/prefs.json', 'r', encoding = 'utf-8') as file:
    prefs = load_json(file)


# Doin' some initialization stuff
set_locale(prefs['ui']['lang'])


# WeatherProvider initialization
weather = WeatherProvider(*prefs['user']['location'].values())


# SteamBridge initializing
steam = None
if prefs['aiko_compat']['steam_library_path'] is not None:
    steam = SteamLibrary(prefs['aiko_compat']['steam_library_path'])


# Color presets
presets['assistant'] = ColorPreset(Fore.LIGHTGREEN_EX)
presets['user']      = ColorPreset(Fore.WHITE)
presets['log']       = ColorPreset(Fore.MAGENTA)
presets['verbose']   = ColorPreset(Fore.LIGHTBLACK_EX)
presets['error']     = ColorPreset(Fore.RED)
presets['green'] = ColorPreset(Fore.LIGHTGREEN_EX)


# Checking for updates
version_info = UpdateChecker.check()
if version_info['update_available']:
    system('cls')
    with presets['green']:
        print(locstr('update_available'))
        print(f'{locstr("version")} {version_info["latest_version"]} ({locstr("instead")} {UpdateChecker.current_version})')
        print(f'{locstr("goto_for_update")} {UpdateChecker.target_url}')
        print(locstr('enter_to_continue'))
        input()
        system('cls')


##############
##  CONSTS  ##
##############


INSTANCE_FNAME = 'data/Aiko.bin'
MODEL_NAME = 'command-r+'
SYSTEM_PROMPT = SYSTEM_PROMPT_BASE + '\n\n' + SYSTEM_PROMPT_USERINFO.format(**prefs['user'])


if steam is not None:
    SYSTEM_PROMPT += '\n\n### Установленные игры пользователя из библиотеки Steam\n\n' + '\n'.join([f'- {name}' for name in steam._installed_games_cache.values()])


#####################
##  AIKO SUBCLASS  ##
##   (Important)   ##
#####################


class AikoAI(AI):
    '''
    Extended `AI` class with some extra attributes.
    
    Makes Aiko more Aiko than any regular AI chat bot.
    '''

    def __init__(self, model: str, system_prompt: str) -> None:
        super().__init__(model, system_prompt)

        # Special attributes
        self.last_prompt_ts = 0

        # Aiko's sisters
        self.shizune = Shizune('command-r+')
        self.lilly   = Lilly('command-r+')

    def prompt(self, prompt: str) -> str:

        dmc = self.get_displayed_messages_count()

        if (not args.no_lilly) and self.lilly.call_interval > 0 and dmc > 0 and dmc % self.lilly.call_interval == 0:
            if args.verbose:
                with presets['verbose']:
                    print('Lilly is active now! Generation will take slightly more time.')
            self.lilly.prompt(f'''
### СИСТЕМНЫЙ ПРОМПТ АЙКО ###
                              
{SYSTEM_PROMPT_BASE}

### КОНЕЦ СИСТЕМНОГО ПРОМПТА АЙКО ###

### Фрагмент диалога для оценки:
'''.strip('\n') + '\n\n' + self.last_messages(self.lilly.call_interval)
            )

        if (not args.no_shizune) and self.shizune.call_interval > 0 and dmc > 0 and dmc % self.shizune.call_interval == 0:
            if args.verbose:
                with presets['verbose']:
                    print('Shizune is active now! Generation will take slightly more time.')
            self.shizune.prompt(self.last_messages(self.shizune.call_interval))

        return super().prompt(prompt)

    def get_displayed_messages_count(self) -> int:

        return len(self.ctx.messages) - [msg.role for msg in self.ctx.messages].count(Role.SYSTEM)
    
    def last_messages(self, max_count: int) -> str:

        out = []
        i = len(self.ctx.messages)
        while len(out) < max_count or i > 0:
            i -= 1
            if self.ctx.messages[i].role == Role.SYSTEM:
                continue
            out.append(f'{prefs["user"]["name"] if self.ctx.messages[i].role == Role.USER else "Айко"}: "{self.ctx.messages[i].content}"')
        return '\n'.join(out)


#################
##  FUNCTIONS  ##
#################


def cutout_commands(message: str) -> str:
    '''
    Cutouts every Aiko's command out of the message and shrinks newlines (cap of 2 NLs in a row)

    Arguments:
        message -- Aiko's message

    Returns:
        Aiko's message without any special commands.
    '''

    lines = message.split('\n')
    new_lines = [] # type: list[str]

    for i, line in enumerate(lines):
        if line.startswith('//'):
            continue
        new_lines.append(line)
    
    out = '\n'.join(new_lines)

    while '\n' * 3 in out:
        out = out.replace('\n' * 3, '\n' * 2)
    
    return out


def exec_commands(message: str) -> tuple[str, Message | None]:
    '''
    Allows Aiko to do more than just chatting with u

    Arguments:
        response -- Aiko's message

    Returns:
        Tuple with formatted Aiko's response and system message (or `None` if no need to tell command execution status)
    '''

    lines = message.strip('\n').split('\n')
    new_lines = lines

    for i, line in enumerate(lines):

        if line.startswith('//'):

            command = line[2:].split(' ', 1)[0]
            args = line[2:].split()[1:]

            match command:

                case 'silence':
                    return ('-> Айко молчит.', None)

                case 'pyexec':
                    new_lines[i] = f'{Fore.LIGHTBLACK_EX}-> {locstr("pyexec_desc")}{Fore.LIGHTGREEN_EX}'
                    try:
                        exec(' '.join(args))
                    except:
                        return ('\n'.join(new_lines), Message(Role.SYSTEM, locstr('cmd_sysresp_pyexec_fail').format(command)))
                    return ('\n'.join(new_lines), Message(Role.SYSTEM, locstr('cmd_sysresp_done').format(command)))

                case 'wincmd':
                    new_lines[i] = f'{Fore.LIGHTBLACK_EX}-> {locstr("wincmd_desc")}{Fore.LIGHTGREEN_EX}'
                    system(' '.join(args))
                    return ('\n'.join(new_lines), Message(Role.SYSTEM, locstr('cmd_sysresp_done').format(command)))

                case 'open_browser_tab':
                    open_new_tab(' '.join(args))
                    new_lines[i] = f'{Fore.LIGHTBLACK_EX}-> {locstr("open_browser_tab_desc")}{Fore.LIGHTGREEN_EX}'
                    return ('\n'.join(new_lines), Message(Role.SYSTEM, locstr('cmd_sysresp_done').format(command)))

                case 'start_game':

                    if steam is None:
                        new_lines[i] = f'{Fore.LIGHTBLACK_EX}-> {locstr("start_game_fail_noinit_desc").format(" ".join(args))}{Fore.LIGHTGREEN_EX}'
                        return ('\n'.join(new_lines), Message(Role.SYSTEM, locstr('start_game_fail_noinit_desc').format(command)))

                    try:
                        new_lines[i] = f'{Fore.LIGHTBLACK_EX}-> {locstr("start_game_ok_desc").format(" ".join(args))}{Fore.LIGHTGREEN_EX}'
                        steam.run_game_by_name(' '.join(args))

                    except SteamLaunchError:
                        new_lines[i] = f'{Fore.LIGHTBLACK_EX}-> {locstr("start_game_fail_nogame_desc").format(" ".join(args))}{Fore.LIGHTGREEN_EX}'
                        return ('\n'.join(new_lines), Message(Role.SYSTEM, locstr('cmd_sysresp_start_game_fail').format(' '.join(args))))

                    return ('\n'.join(new_lines), Message(Role.SYSTEM, locstr('cmd_sysresp_done').format(command)))
    
    return (message, None)


# Clearing all the logs
system('cls')


##################
##  UNPICKLING  ##
##################


try:

    with open(INSTANCE_FNAME, 'rb') as file:
        aiko = load(file) # type: AikoAI
    
    with presets['verbose']:
        print(f'Loaded {INSTANCE_FNAME} (current size: {round(getsizeof(aiko) / 1024, 2)} KiB)')

    # Displaying last context messages
    for msg in aiko.ctx.messages[-10:]:
        if msg.role == Role.SYSTEM:
            continue
        with presets[msg.role]:
            print((locstr('assistant_title_nl') if msg.role == Role.ASSISTANT else locstr('you_title_nl')) + cutout_commands(msg.content))
    
    # Updating system prompt, if changed since last pickling
    aiko.ctx.messages[0].content = SYSTEM_PROMPT

    with presets['log']:
        print(locstr('ctx_loaded'))

except:
    # Creating brand new Aiko instance if anything went wrong during unpickling
    aiko = AikoAI(MODEL_NAME, SYSTEM_PROMPT)


#################
##  MAIN LOOP  ##
#################


while True:

    with presets['user']:
        prompt = input(locstr('you_title_nl'))

    if weather is not None:
        # Requesting current weather data
        current_weather = weather.current()
        # Building string describing current weather outside
        current_weather_str = f'{signify(round(current_weather["temperature"]))} {locstr("deg_celsius")}, '
        if current_weather['snowfall']:
            current_weather_str += locstr('snowfall')
        elif current_weather['showers']:
            current_weather_str += locstr('showers')
        elif current_weather['rain']:
            current_weather_str += locstr('rain')
        else:
            current_weather_str += locstr('clear_weather')
        current_weather_str += f', {locstr("wind_speed")}: {current_weather["wind_speed"]} {locstr("mps")}'
    
    if prompt == '//debug_info':
        with presets['verbose']:
            if steam is None:
                print('steam is None')
                continue
            print(f'steam._installed_games_cache:\n{steam._installed_games_cache}\n')
            print(f'aiko.shizune.last_verdict:\n{aiko.shizune.last_verdict}\n')
            print(f'aiko.lilly.last_verdict:\n{aiko.lilly.last_verdict}\n')
            print(f'current_weather_string:\n{current_weather_str}')
            continue

    aiko.ctx.head_message = Message(Role.SYSTEM, f'''
### Следующая информация предоставлена в справочных целях. Она необязательно должна повлиять на ответ, но может, если это уместно.

- Текущие дата и время: {datetime.now().strftime("%H:%M, %A, %d %B %Y")}
- Погода за окном пользователя: {"[не удалось получить данные]" if weather is None else current_weather_str}
- Время, прошедшее с последнего обращения пользователя к тебе: {str(floor(time() - aiko.last_prompt_ts) // 60) + " мин. " + str(floor(time() - aiko.last_prompt_ts) % 60) + " сек." if aiko.last_prompt_ts != 0 else '[никогда]'}

### Напоминания

- Ты можешь отправить ЛИБО одну команду, ЛИБО текст, который будет являться ответом на сообщение пользователя, ЛИБО текст с командой СТРОГО В НАЧАЛЕ
- Если команда будет в середине или в конце текста, она НЕ СРАБОТАЕТ.
- Доступные команды перечислены в первом системном промпте в разделе [Список доступных команд]

### Настроения участников диалога

{'[Информация появится здесь позже.]' if aiko.shizune.last_verdict is None else aiko.shizune.last_verdict}

### Замечания по твоему поведению от твоей сестры-нейросети Лилли

{'[Пока Лилли не анализировала ваш диалог.]' if aiko.lilly.last_verdict is None else aiko.lilly.last_verdict}
'''.strip('\n'))

    with presets['verbose']:
        response = aiko.prompt(prompt)

    response, system_status_message = exec_commands(response)
    if system_status_message is not None:
        aiko.ctx.add(system_status_message)

    with presets['assistant']:
        print(locstr('assistant_title_nl') + response)
    
    aiko.last_prompt_ts = time()

    with open(INSTANCE_FNAME, 'wb') as file:
        dump(aiko, file)