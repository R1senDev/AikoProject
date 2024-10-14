from g4f.client import Client
from typing     import overload, Literal


class Role:
    USER = 'user'
    SYSTEM = 'system'
    ASSISTANT = 'assistant'


class Message:

    def __init__(self, role: Literal['user', 'system', 'assistant'], content: str) -> None:

        self.role = role
        self.content = content
    
    def json(self) -> dict[str, str]:

        return {
            'role': self.role,
            'content': self.content
        }
    

class Context:

    def __init__(self, messages: list[Message], preserve_system: Literal['no', 'first', 'all']) -> None:

        self.preserve_system = preserve_system
        self.messages = messages
    
    def add(self, message: Message) -> int:

        self.messages.append(message)
        return len(self.messages)
    
    def strip(self, limit: int) -> int:

        system_ignored = 0
        new_msg_list = [] # type: list[Message]

        for i in range(len(self.messages)):

            if self.messages[i].role == Role.SYSTEM:

                if (self.preserve_system == 'first' and not system_ignored) or self.preserve_system == 'all':
                    system_ignored += 1
                    continue
            
            new_msg_list.append(self.messages[i])

            if len(new_msg_list) == limit:
                break

        self.messages = new_msg_list
        
        return len(self.messages)

    def jsonify(self) -> list[dict[str, str]]:
        
        return [msg.json() for msg in self.messages]
    

class AI:

    def __init__(self, model: str, system_prompt: str | None = None) -> None:

        self._client = Client()
        self.model = model
        self.ctx = Context([], 'first')
        if system_prompt is not None:
            self.ctx.add(Message(Role.SYSTEM, system_prompt))
        
    def prompt(self, prompt: str) -> str:

        self.ctx.add(Message(Role.USER, prompt))
        response_text = self._client.chat.completions.create(
            model    = self.model,
            messages = self.ctx.jsonify()
        ).choices[0].message.content
        self.ctx.add(Message(Role.ASSISTANT, response_text))
        print(response_text)
        return response_text


__all__ = [
    'Role',
    'Message',
    'Context',
    'AI',
]