from collections import deque
from collections import Counter

class ChatController():
    """ Handles the mapping from messages to actions based on a heuristic """
    def __init__(self, keyboard, update_every=10, verbose=False):
        self._storage = deque()
        self._keyboard = keyboard
        self._update_limit = update_every
        self._verbose = verbose

    def register_move(self, move):
        self._storage.append(move)
        if self._verbose:
            print(f"Received '{move}' and has size {len(self._storage)}")
        self.update_command()

    def update_command(self):
        if len(self._storage) >= self._update_limit:
            moves = [self._storage.popleft() for _ in range(self._update_limit)]
            move = Counter(moves).most_common(1)[0][0]
            self._keyboard(move)
            if self._verbose:
                print(f"Pressed '{move}'")


if __name__== "__main__":
    from keyboard_control import press_keys
    from messagefilter import MessageFilter
    from message import Message
    c = ChatController(press_keys, update_every=3, verbose=True)
    moves = [('', 'adsadsd'), ('', 'adsadsd'), ('', 'adsadsd'), ('', 'adsadsd'),
            ('', 'r'), ('', 'r'), ('', 'r'), ('', 'r'), ('', 'e'), ('', 'e'), ('', 'e'), ('', 'asdsad'), ('', 'bbbbb'),
            ('', 'm'), ('', 'cc'), ('', 'i'), ('', 'e'), 
            ('', 'd'), ('', 'as'), ('', '21'), ('', 'adswqEQadsd')]
    valid = ['r', 'e', 'm', 'i']
    f = MessageFilter(valid, c)
    moves = [Message(m[0], m[1]) for m in moves]
    for move in moves:
        f.filter_message(move)