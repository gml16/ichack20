from collections import deque
from collections import Counter
from time import time

class ChatController():
    """ Handles the mapping from messages to actions based on a heuristic 
    
    keyboard: The class that triggers the actual key strokes
    update_every (n): if count is set to TRUE, an key will be triggered every n seconds, 
                    otherwise every n entries
    count: Sets the mode from message counting to time counting
    verbose: controlls printing
    """
    def __init__(self, keyboard, update_every=1, count=False, verbose=False):
        self._storage = deque()
        self._keyboard = keyboard
        self._update_threshold = update_every
        self._verbose = verbose
        self._ctime = time()
        self._counting = count

    def register_move(self, move):
        """ 
        Registers a move to the storage and triggers an update check
        """
        self._storage.append(move)
        if self._verbose:
            print(f"Received '{move}' and has size {len(self._storage)}")
        if self.time_for_update():
            self.update_command()

    def time_for_update(self):
        """ 
        Returns true if _update_threshold ms has gone by since last registered move
        """
        if self._counting:
            return self.size_for_update()
        now = time()
        if abs(self._ctime - now) > self._update_threshold:
            self._ctime = now
            return True
        return False

    def size_for_update(self):
        """ 
        Returns true if the storage is larger than the set limit
        """
        return len(self._storage) >= self._update_threshold

    def update_command(self):
        """
        Triggers a key-stroke for the most commonly voted for input
        """
        if self._counting:
            # Pop upto the update limit
            moves = [self._storage.popleft() for _ in range(self._update_threshold)]
        else:
            # or the entire deque if we're working with timing
            moves = [self._storage.popleft() for _ in range(len(self._storage))]
        move = Counter(moves).most_common(1)[0][0]
        self._keyboard.press_keys(move)
        if self._verbose:
            print(f"Pressed '{move}'")


if __name__== "__main__":
    from keyboard_control import KeyboardController
    from messagefilter import MessageFilter
    from message import Message
    k = KeyboardController()
    c = ChatController(k, update_every=2, count=True, verbose=True)
    moves = [('', 'adsadsd'), ('', 'adsadsd'), ('', 'adsadsd'), ('', 'adsadsd'),
            ('', 'r'), ('', 'r'), ('', 'r'), ('', 'r'), ('', 'e'), ('', 'e'), ('', 'e'), ('', 'asdsad'), ('', 'bbbbb'),
            ('', 'm'), ('', 'cc'), ('', 'i'), ('', 'e'), 
            ('', 'd'), ('', 'as'), ('', '21'), ('', 'adswqEQadsd')]
    valid = ['r', 'e', 'm', 'i']
    f = MessageFilter(valid, c)
    moves = [Message(m[0], m[1]) for m in moves]
    for move in moves:
        f.filter_message(move)