'''
Core.Hanako
for AikoProject
'''


from .AI import AI


LILLY_SYSTEM_PROMPT = '''
Тебя зовут Лилли, ты - сестра Айко.

### Твоя задача

Корректировка поведения Айко в случаях, когда та отклоняется от указаний её системного промпта.

### Правила

- В твоём ответе должны быть строки, обращённые к Айко и содержащие замечания по тому, как Айко придерживается указаний системного промпта.
- В случае, если поведение Айко соответствует системному промпту и ты ни к чему не можешь придраться, нужно сказать "Всё в порядке, Айко."
- Нельзя полностью переписывать системный промпт.
'''.strip('\n')


class Lilly(AI):
    '''
    Lilly is the helper AI for Aiko.
    
    Her purpose is to adjust Aiko's behaviour to her system prompt.
    She doesn't have context, excluding system prompt.
    '''

    def __init__(self, model: str) -> None:
        self.call_interval = 6
        self.last_verdict = None
        super().__init__(model, LILLY_SYSTEM_PROMPT)
    
    def prompt(self, prompt: str) -> str:
        self.reset_ctx()
        self.last_verdict = super().prompt(prompt)
        return self.last_verdict


__all__ = [
    'Lilly',
    'LILLY_SYSTEM_PROMPT'
]