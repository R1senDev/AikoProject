from threading import Lock

class AikoState:
    def __init__(self):
        self.agreement_mutex = Lock()
        self.agreement_mutex.acquire(False)
        self.chat_queue = []  # type: list[str]
        self.is_thinking = False
        self.last_response = None

aiko_state = AikoState()