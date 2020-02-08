

class MessageFilter():
    """ 
    This class will take as input the raw user messages and forwards them to
    the central unit 
    
    legal_moves: list of characters that represent the moves that can be directly 
                translated to commands for the specific game.
    
    """
    def __init__(self, legal_moves, controller):
        self._legal_moves = set(legal_moves)
        self._controller = controller

    """
    Filters the incomming message object
    """
    def filter_message(self, message):
        move = message._content.lower()
        is_legal = move in self._legal_moves
        if is_legal:
            triggered_key = self._controller.register_move(move)
        return is_legal, triggered_key