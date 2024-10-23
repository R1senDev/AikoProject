'''
Core.SetupWizard
for AikoProject
'''


from json import load, dump


PREFS_TEMPLATE = {
    'aiko_compat': {
        'steam_library_path': 'D:\\SteamLibrary'
    },
    'ui': {
        'lang': 'ru_ru'
    },
    'user': {
        'name': '',
        'age': 0,
        'personality': '',
        'location': {
            'latitude': 0,
            'longitude': 0
        }
    }
}


def init_aiko() -> None:
    with open('config/prefs.json', 'r') as file:
        prefs = load(file)
    if prefs.keys():
        return None
    
    prefs = PREFS_TEMPLATE
    
    print('\n  Привет! Айко хочет познакомиться с тобой.')
    print('  Как тебя зовут?')
    prefs['user']['name'] = input('> ')
    print('  Сколько тебе лет?')
    prefs['user']['age'] = int(input('> '))
    print('  Опиши себя в несколько фраз или даже предложений.')
    prefs['user']['personality'] = input('> ')
    print('  Укажи свою широту и долготу через запятую. Не переживай, это нужно лишь для того, чтобы Айко знала, какая погода за окном.')
    prefs['user']['location']['latitude'], prefs['user']['location']['longitude'] = map(float, input('> ').replace(' ', '').split(',', 1))
    print('  Укажи путь к своей библиотеке Steam. Например, "D:\\SteamLibrary" (без кавычек).\n  Нет Steam? Ничего не вводи и нажми [Enter].')
    prefs['aiko_compat']['steam_library_path'] = input('> ')
    if not prefs['aiko_compat']['steam_library_path']:
        prefs['aiko_compat']['steam_library_path'] = None
    
    with open('config/prefs.json', 'w', encoding = 'utf-8') as file:
        dump(prefs, file, indent = 4)

    print('  Настройка завершена! Перезапусти программу, чтобы начать разговаривать с Айко.\n  Если что, эти настройки можно изменить вручную. Они хранятся в файле config/prefs.json.')

    while True: ...