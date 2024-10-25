from sqlite3 import connect, IntegrityError
from os.path import exists
from .AI     import AI


KK_GETTER_SYSTEM_PROMPT = '''
### Твоя задача

Ты - библиотекарь. Твоя задача - выдавать полезную информацию, соответствующую контексту разговора, который будет предоставлен пользователем.

### Правила

- Если в Базе Знаний Айко ничего полезного не нашлось, твой ответ должен выглядеть как "[Нет]" (без кавычек, с квадратными скобками).
- Твой ответ должен содержать одну НЕМОДИФИЦИРОВАННУЮ ТОБОЙ строку из Базы Знаний либо строку "[Нет]".
'''.strip('\n')


KK_PUTTER_SYSTEM_PROMPT = '''
### Твоя задача

Ты - библиотекарь. Твоя задача - получать полезную информацию из контекста разговора и сохранять её в Базу Знаний Айко, который будет предоставлен пользователем.

### Правила

- Не сохранять неважную для Айко информацию в Базу Знаний.
- Если в тексте нет неважной информации, твой ответ должен выглядеть как "[Нет]" (без кавычек, с квадратными скобками).
- Твой ответ должен содержать одно предложение, которое будет сохранено, либо строку "[Нет]".
'''.strip('\n')


class KK_PUTTER_AI(AI):

    def __init__(self, model: str) -> None:
        self.last_reply = None
        super().__init__(model, KK_PUTTER_SYSTEM_PROMPT)
    
    def prompt(self, text: str) -> str:
        self.reset_ctx()
        self.last_reply = super().prompt(text)
        return self.last_reply
    

class KK_GETTER_AI(AI):

    def __init__(self, model: str) -> None:
        self.last_reply = None
        super().__init__(model, KK_GETTER_SYSTEM_PROMPT)
    
    def prompt(self, context: str, database_contents: str) -> str:
        to_fwd = f'''
### Диалог:

{context}

### Содержимое Базы Знаний Айко

{database_contents}
'''.strip('\n')
        self.reset_ctx()
        self.last_reply = super().prompt(to_fwd)
        return self.last_reply


class KnowledgeKeeper:

    def __init__(self, model: str, fname: str = 'data/knowledge.db') -> None:

        self.putter_ai = KK_PUTTER_AI(model)
        self.getter_ai = KK_GETTER_AI(model)

        # Knowledge base initialization
        if exists(fname):
            # Just connect and get cursor
            self.knowledge_db_conn = connect(fname)
            self.knowledge_db = self.knowledge_db_conn.cursor()
        else:
            # Connect, get cursor and create all of that weird stuff
            self.knowledge_db_conn = connect(fname)
            self.knowledge_db = self.knowledge_db_conn.cursor()
            self.knowledge_db.execute('''
CREATE TABLE "found_online" (
	"query"	TEXT NOT NULL UNIQUE,
	"info"	TEXT NOT NULL,
	PRIMARY KEY("query")
)
'''.strip('\n'))
            self.knowledge_db.execute('''
CREATE TABLE "memories" (
	"id"	INTEGER NOT NULL UNIQUE,
	"content"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
)
'''.strip('\n'))
            self.knowledge_db_conn.commit()

    def get_db_contents(self) -> str:

        self.knowledge_db.execute('SELECT info FROM found_online')
        lines = [chunk[0] for chunk in self.knowledge_db.fetchall()] # list[str]
        self.knowledge_db.execute('SELECT content FROM memories')
        lines += [chunk[0] for chunk in self.knowledge_db.fetchall()] # list[str]

        if lines:
            return '\n'.join(lines)
        return '[База Знаний Айко пуста]'
    
    def put(self, context: str) -> bool:

        self.putter_ai.prompt(context)

        if self.putter_ai.last_reply is None or '[Нет]' in self.putter_ai.last_reply:
            return False
        
        self.knowledge_db.execute('INSERT INTO memories (content) VALUES (?)', (self.putter_ai.last_reply,))
        self.knowledge_db_conn.commit()

        return True
    
    def get(self, context: str) -> str:

        return self.getter_ai.prompt(context, self.get_db_contents())