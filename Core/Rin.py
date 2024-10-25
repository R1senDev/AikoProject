from pygoogling.googling import GoogleSearch
from bs4                 import BeautifulSoup
from requests            import get
from .AI                 import AI


RIN_SYSTEM_PROMPT = '''
Тебя зовут Рин, ты - сестра Айко.

### Твоя задача

Ты будешь получать огромное количество информации от пользователя.
Ты должна суммаризовать её и в своём ответе объяснить в одном-двух абзацах (или меньше, если нет нужды объяснять подробно) о теме этого набора данных.
ТЕМА ПРЕДОСТАВЛЕНА В ПЕРВОЙ СТРОКЕ ПРОМПТА.

### Правила

- Твой ответ ВСЕГДА ДОЛЖЕН БЫТЬ НА РУССКОМ ЯЗЫКЕ вне зависмости от языка, на котором пользователь предоставил данные.
- Названия, имена и т.д. можно оставлять на языке оригинала, но лучше дублировать их варимантами из источников (пример: "Мику Хацунэ (Hatsune Miku, 初音ミク)")
- Новый текст не должен быть слишком длинным, но передавать основные моменты оригинальных данных.
- Если информации нет, ответь, что информация не нашлась.
- Если запрос был об игре, фильме и т.п., избегай возможных спойлеров в своём ответе (кроме тех случаев, когда это неизбежно).

### Пример твоего ответа

* * *
# User: [Невероятное количество текста. Большинство из него по теме, но некоторый совершенно посторонний (такой нужно будет игнорировать)].
# Assistant: "Мику Хацунэ (Hatsune Miku, 初音ミク) — японская виртуальная певица, созданная компанией Crypton Future Media 31 августа 2007 года. Для синтеза её голоса используется технология семплирования голоса живой певицы с использованием программы Vocaloid компании Yamaha Corporation. Голосовым провайдером послужила японская актриса и певица (сэйю) Саки Фудзита. Оригинальный образ был создан японским иллюстратором KEI Garou[3], также работавшим над внешностью других вокалоидов для Crypton Future Media. Диски с песнями Мику завоёвывали первые позиции в японских чартах."
* * *
'''.strip('\n')


headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.5 Mobile/15E204 Safari/10.4'
}


class Rin(AI):
    '''
    Rin is the helper AI for Aiko.
    
    Her purpose is to summarize any strings (she's optimized for VERY BIG strings) to few paragraphs.
    '''

    def __init__(self, model: str) -> None:
        self.last_reply = None
        super().__init__(model, RIN_SYSTEM_PROMPT)
    
    def prompt(self, data_string: str) -> str:
        self.reset_ctx()
        self.last_reply = super().prompt(search_about(data_string))
        return self.last_reply


def search_about(what: str, max_page: int = 1) -> str:

    engine = GoogleSearch(what)
    engine.start_search(max_page = max_page)
    urls = engine.search_result
    opener = f'# ТЕМА ИНТЕРЕСА: "{what}"'
    pages_contents = [opener]
    
    for url in urls:

        try:
            result = get(url, headers = headers)
        except:
            continue

        if result.status_code != 200:
            continue

        soup = BeautifulSoup(result.text, 'html.parser')
        pages_contents.append(soup.getText('\n'))

    if pages_contents:
        return '\n\n'.join(pages_contents)[:10000]
    return '[Информации не нашлось.]'