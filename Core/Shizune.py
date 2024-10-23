'''
Core.Shizune
for AikoProject
'''


from .AI import AI


SHIZUNE_SYSTEM_PROMPT = '''
Тебя зовут Сидзунэ, ты - сестра Айко.

### Твоя задача

Определять настроения участников диалога

### Правила

- В твоём ответе должно быть ровно две строки, каждая из которых должна начинаться с имени участника диалога
- В каждой строке должно быть не более одного-двух предложений 

### Пример твоей задачи

* * *
# Входные данные
Аня: "Не думаю, что это возможно."
Айко: "Не переживай по этому поводу. Всё будет в порядке, я обещаю!"
Аня: "Вряд ли."
Айко: "Не сомневайся!"

# Твой возможный ответ
- Аня выглядит грустной и подавленной.
- Айко сохраняет неунывающий настрой и старается поддержать Аню.
* * *
'''.strip('\n')


class Shizune(AI):
    '''
    Shizune is the helper AI for Aiko.
    
    Her purpose is to proovide an independent perspective on the dialogue.
    She doesn't have context, excluding system prompt.
    '''

    def __init__(self, model: str) -> None:
        self.call_interval = 10
        self.last_verdict = None
        super().__init__(model, SHIZUNE_SYSTEM_PROMPT)
    
    def prompt(self, prompt: str) -> str:
        self.reset_ctx()
        self.last_verdict = super().prompt(prompt)
        return self.last_verdict


__all__ = [
    'SHIZUNE_SYSTEM_PROMPT',
    'Shizune'
]